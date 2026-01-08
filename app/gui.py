import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
import threading
import os
from tkinter import filedialog

# Імпортуємо твій бекенд
from monitor import MonitorManager, rules 
from user import User



class SideBar(ctk.CTkFrame):
    """
    Бокова панель
    """
    def __init__(self, master, command, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=("white", "gray17"))
        self.grid_propagate(False)

        # Логотип 
        self.lbl_logo = ctk.CTkLabel(self, text="DirMonitor", font=("Arial", 20, "bold"),
                                     text_color=("gray10", "gray90")) 
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Головна
        self.btn_dashboard = ctk.CTkButton(self, text='Monitor Control', fg_color="transparent", anchor="w",
                                           text_color=("gray10", "gray90"), 
                                           command=lambda: command("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Налаштування
        self.btn_settings = ctk.CTkButton(self, text='General Settings', fg_color="transparent", anchor="w",
                                          text_color=("gray10", "gray90"),
                                          command=lambda: command("Settings"))
        self.btn_settings.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Розділювач
        self.lbl_cats = ctk.CTkLabel(self, text="CATEGORIES", font=("Arial", 10), anchor="w",
                                     text_color=("gray50", "gray70"))
        self.lbl_cats.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="ew")

        # Категорії
        categories = ["Documents", "Images", "Audio", "Archives", "Programs"]
        
        for i, cat in enumerate(categories, start=4):
            if cat in rules:
                btn = ctk.CTkButton(self, text=cat, fg_color="transparent", anchor="w",
                                    text_color=("gray10", "gray90"),
                                    command=lambda c=cat: command(c))
                btn.grid(row=i, column=0, padx=10, pady=2, sticky="ew")


class GlobalSettingsFrame(ctk.CTkFrame):
    """
    Сторінка загальних налаштувань (Рекурсія, Тема і т.д.)
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.app = self.winfo_toplevel() # Доступ до User і Monitor
        adaptive_bg = ("gray20", "gray95")

        # Заголовок
        self.lbl_title = ctk.CTkLabel(self, 
                                      text="Global Settings", 
                                      font=("Arial", 24, "bold"),
                                      text_color=adaptive_bg) 
        self.lbl_title.pack(pady=20, padx=20, anchor="w")

        # Блок Моніторингу 
        self.frame_monitor = ctk.CTkFrame(self)
        self.frame_monitor.pack(pady=10, padx=20, fill="x")

        self.lbl_monitor = ctk.CTkLabel(self.frame_monitor, 
                                        text="Monitoring Logic", 
                                        font=("Arial", 14, "bold"),
                                        text_color=adaptive_bg)
        self.lbl_monitor.pack(pady=10, padx=10, anchor="w")

        # Рекурсія
        self.switch_recursive = ctk.CTkSwitch(self.frame_monitor, 
                                              text="Recursive Scan (Check subfolders)",
                                              text_color=adaptive_bg,
                                              command=self.toggle_recursive)
        self.switch_recursive.pack(pady=10, padx=20, anchor="w")
        
        # Автозапуск
        self.switch_autostart = ctk.CTkSwitch(self.frame_monitor, 
                                              text="Run on Windows Startup (Coming soon)",
                                              text_color=adaptive_bg)
        self.switch_autostart.configure(state="disabled")
        self.switch_autostart.pack(pady=10, padx=20, anchor="w")

        # Блок Зовнішнього вигляду
        self.frame_appearance = ctk.CTkFrame(self)
        self.frame_appearance.pack(pady=10, padx=20, fill="x")
        
        self.lbl_app = ctk.CTkLabel(self.frame_appearance, 
                                    text="Appearance", 
                                    font=("Arial", 14, "bold"),
                                    text_color=adaptive_bg)
        self.lbl_app.pack(pady=10, padx=10, anchor="w")

        self.switch_theme = ctk.CTkSwitch(self.frame_appearance, 
                                          text="Dark Mode",
                                          text_color=adaptive_bg,
                                          command=self.toggle_theme)
        self.switch_theme.select() # За замовчуванням темна
        self.switch_theme.pack(pady=10, padx=20, anchor="w")

        self._load_recursive_state()

    # Для відображення стану рекурсії
    def _load_recursive_state(self):
        is_recursive = self.app.user.data.get("recursive", False)  # pyright: ignore[reportAttributeAccessIssue]
        if is_recursive:
            self.switch_recursive.select() 

    # Міняє стан рекурсії + перезапускає прогу якщо включена під час перемикання
    def toggle_recursive(self):
        state = self.switch_recursive.get()
        print(f"Recursive scan set to: {bool(state)}")

        self.app.user.data['recursive'] = state # pyright: ignore[reportAttributeAccessIssue]
        self.app.user.save_to_json(self.app.user.data, "user_data.json") # pyright: ignore[reportAttributeAccessIssue]
        
        if self.app.monitor_manager.is_running: # type: ignore
            msg = self.app.monitor_manager.restart() # type: ignore
            self.app.frames["dashboard"].update_log(msg) # type: ignore
        
    # Міняє тему
    def toggle_theme(self):
        if self.switch_theme.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")


class MonitorControlFrame(ctk.CTkFrame):
    """
    Головна сторінка
    """
    def __init__(self, master, monitor_manager: MonitorManager, **kwargs):
        super().__init__(master, **kwargs)
        self.monitor = monitor_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # Верхня панель
        self.buttons_frame = ctk.CTkFrame(self, 
                                          fg_color="transparent")
        self.buttons_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_start = ctk.CTkButton(self.buttons_frame, 
                                       text="START MONITORING",
                                       fg_color="#2CC985",
                                       hover_color="#229965",
                                       command=self.start_monitoring)
        self.btn_start.pack(side="left", padx=10)

        self.btn_stop = ctk.CTkButton(self.buttons_frame, 
                                      text="STOP",
                                      fg_color="#C92C2C",
                                      hover_color="#992222",
                                      state="disabled",
                                      command=self.stop_monitoring)
        self.btn_stop.pack(side="left", padx=10)

        # Лог
        self.log_box = ctk.CTkTextbox(self, 
                                      font=("Consolas", 12))
        self.log_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_box.insert("0.0", "System ready...\n")

    def update_log(self, message):
        self.after(0, lambda: self._write_log(message))


    def _write_log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")


    def start_monitoring(self):
        msg = self.monitor.start()
        if msg:
            self.update_log(msg)
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")


    def stop_monitoring(self):
        msg = self.monitor.stop()
        if msg:
            self.update_log(msg)
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")


class CategorySettingsFrame(ctk.CTkFrame):
    """
    Сторінка налаштувань категорій
    """
    def __init__(self, master, category_name, available_extensions, **kwargs):
        super().__init__(master, **kwargs)
        self.app = self.winfo_toplevel()
        self.category_name = category_name
        self.available_extensions = available_extensions
        self.path_json_key = f"{category_name.lower()}_path"
        self._init_ui()
        self._load_saved_data()

    # Генерація сторінок
    def _init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        adaptive_bg = ("gray20", "gray95")

        self.lbl_title = ctk.CTkLabel(self, 
                                      text=f"Settings for {self.category_name}", 
                                      font=("Arial", 20, "bold"),
                                      text_color=adaptive_bg)
        self.lbl_title.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")

        # Шлях
        self.lbl_current_path = ctk.CTkLabel(self, 
                                             text="Path: Not set", 
                                             anchor="w",
                                             text_color=adaptive_bg)
        self.lbl_current_path.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")

        self.ent_path = ctk.CTkEntry(self, 
                                     placeholder_text="Enter folder path...")
        self.ent_path.bind('<Return>', self.save_path)
        self.ent_path.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="ew")

        self.btn_browse = ctk.CTkButton(self, 
                                        text="Browse", 
                                        width=60,
                                        text_color=adaptive_bg,
                                        command=self.browse_folder)
        self.btn_browse.grid(row=2, column=1, padx=(0, 20), pady=10)

        # Розширення
        self.lbl_ext = ctk.CTkLabel(self, 
                                    text="Select extensions to monitor:",
                                    text_color=adaptive_bg,
                                    font=("Arial", 14))
        self.lbl_ext.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="w")

        self.checkbox_frame = ctk.CTkFrame(self, 
                                           fg_color="transparent")
        self.checkbox_frame.grid(row=4, column=0, columnspan=2, padx=20, sticky="w")

        self.checkboxes = {}
        for idx, ext in enumerate(self.available_extensions):
            cb = ctk.CTkCheckBox(self.checkbox_frame, 
                                 text=ext, 
                                 font=("Consolas", 14),
                                 text_color=adaptive_bg,
                                 command=self.save_extensions)
            cb.grid(row=0, column=idx, padx=10, pady=5)
            self.checkboxes[ext] = cb

    # Витягуєм шлях, розширення (для чекбоксів)
    def _load_saved_data(self):
        adaptive_bg = ("gray20", "gray95")
        saved_path = self.app.user.data.get(self.path_json_key, None) # pyright: ignore
        if saved_path:
            self.ent_path.insert(0, saved_path)
            self.lbl_current_path.configure(text=f"Path: {saved_path}", 
                                            text_color=adaptive_bg)
        else:
            self.lbl_current_path.configure(text="Path: Not set (files will not be moved)")

        saved_rules = self.app.user.data["rules"].get(self.category_name, []) # pyright: ignore
        for ext, cb in self.checkboxes.items():
            if ext in saved_rules:
                cb.select()

    # Зберіємо шлях у файл
    def save_path(self, event=None):
        path = self.ent_path.get()
        if os.path.exists(path) and os.path.isdir(path):
            self.app.user.data[self.path_json_key] = path # pyright: ignore
            self.app.user.save_to_json(self.app.user.data, "user_data.json") # pyright: ignore
            
            
            self.lbl_current_path.configure(text=f"Path: {path}", text_color=("gray90", "gray10"))
            print(f"[{self.category_name}] Path saved: {path}")
        else:
            self.lbl_current_path.configure(text="Error: Directory does not exist!", text_color="#FF5555")

    # Для кнопки яка викликає провідник і дає змогу вибрати шлях
    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.ent_path.delete(0, "end")
            self.ent_path.insert(0, path)
            self.save_path()

    # Зберігаємо розширення
    def save_extensions(self):
        selected = []
        for ext, cb in self.checkboxes.items():
            if cb.get() == 1:
                selected.append(ext)
        self.app.user.data["rules"][self.category_name] = selected # pyright: ignore
        self.app.user.save_to_json(self.app.user.data, "user_data.json") # pyright: ignore
        print(f"[{self.category_name}] Rules updated: {selected}")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("DirectoryMonitor")
        self.geometry("800x600")
        self.resizable(False, False)
        self.grid_propagate(False)
        
        self.user = User("user_data.json")
        self.monitor_manager = MonitorManager() 

        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SideBar(self, 
                               command=self.select_frame, 
                               width=150)
        self.sidebar.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.frames = {}
        adaptive_bg = ("gray95", "gray20")
        
        self.frames["dashboard"] = MonitorControlFrame(self, 
                                                       self.monitor_manager, 
                                                       width=600, 
                                                       fg_color=adaptive_bg)
        self.monitor_manager.handler.callback_func = self.frames["dashboard"].update_log

        self.frames["Settings"] = GlobalSettingsFrame(self, 
                                                      width=600, 
                                                      fg_color=adaptive_bg)

        for category, extensions in rules.items():
            self.frames[category] = CategorySettingsFrame(self, 
                                                          category_name=category, 
                                                          available_extensions=extensions,
                                                          width=600, 
                                                          fg_color=adaptive_bg)

        self.select_frame("dashboard")

    # Обираєм шо відмальовувати
    def select_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()
        
        if name in self.frames:
            self.frames[name].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        else:
            print(f"Error: Frame '{name}' not found")

    # Для фонового режиму
    def withdraw_window(self):  
        self.withdraw()
        self.tray_thread = threading.Thread(target=self.create_tray_icon)
        self.tray_thread.start()

    # Створює іконку
    def create_tray_icon(self):
        try:
            image = Image.new('RGB', (64, 64), color=(200, 50, 50))
            draw = ImageDraw.Draw(image)
            draw.rectangle((16, 16, 48, 48), fill=(255, 255, 255))

            menu = (
                pystray.MenuItem('Open Monitor', self.show_window),
                pystray.MenuItem('Exit', self.quit_window)
            )

            self.icon = pystray.Icon("DirectoryMonitor", image, "Directory Monitor", menu)
            self.icon.run()

        except Exception as e:
            print(f"Tray Error: {e}")
            self.after(0, self.deiconify)

    # Відновлення проги від трею
    def show_window(self, icon, item):
        self.icon.stop()
        self.after(0, self.deiconify) 

    # Повністю закриваєм
    def quit_window(self, icon, item):
        self.monitor_manager.stop()
        self.icon.stop() 
        self.quit()       
        self.destroy()
        import sys
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()