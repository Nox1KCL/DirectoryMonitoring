import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
import threading
from monitor import MonitorManager
from user import User
from tkinter import filedialog
import os


class SideBar(ctk.CTkFrame):
    def __init__(self, master, command, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)

        self.opt_default_setting = ctk.CTkButton(self, 
                                                 text='Default setting',
                                                 fg_color="transparent",
                                                 command=lambda: command("default_setting"))
        self.opt_default_setting.grid(row=1, column=0, padx=5,pady=5, sticky="ew")

        self.opt_documents = ctk.CTkButton(self, 
                                           text='Documents', 
                                           fg_color="transparent",
                                           )
        self.opt_documents.grid(row=2, column=0, padx=5,pady=5, sticky="ew")
        
        self.opt_pictures = ctk.CTkButton(self, 
                                          text='Pictures', 
                                          fg_color="transparent",
                                          )
        self.opt_pictures.grid(row=3, column=0, padx=5,pady=5, sticky="ew")


class DefSettingFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.app = self.winfo_toplevel()
        saved_text = self.app.user.data.get("documents_path", "You don't have path") # pyright: ignore[reportAttributeAccessIssue]

        self.extensions()

        self.path_field = ctk.CTkEntry(self,
                                       width=520,
                                       placeholder_text="Enter path to save",
                                       )
        self.path_field.bind('<Return>', self.save_path)
        self.path_field.grid(row=0, column=1, padx=20, pady=40)

        self.btn_browse = ctk.CTkButton(self, 
                                text="...",
                                width=10,
                                command=self.browse_folder)
        self.btn_browse.grid(row=0, column=2, padx=10)

        self.current_path_label = ctk.CTkLabel(self,
                                               text=f"Current path: {saved_text}",
                                               anchor='w',
                                               )
        self.current_path_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(70, 5), sticky="ew")
        if saved_text != "You don't have path":
            self.path_field.insert(0, saved_text)



    def extensions(self):
        self.app = self.winfo_toplevel()
        current_rules = self.app.user.data["rules"].get("Documents", []) # pyright: ignore[reportAttributeAccessIssue]

        self.checkbox_container = ctk.CTkFrame(self, fg_color="transparent")
        self.checkbox_container.grid(row=1, column=1, columnspan=2, sticky="w")

        self.docx = ctk.CTkCheckBox(self.checkbox_container,
                                    text=".docx",
                                    font=('Arial', 15),
                                    command=self.save_checkboxes)
        self.docx.grid(row=0, column=0, padx=(20, 15))

        if ".docx" in current_rules:
            self.docx.select()

        self.doc = ctk.CTkCheckBox(self.checkbox_container, 
                                    text=".doc",
                                    font=('Arial', 15),
                                    command=self.save_checkboxes)
        self.doc.grid(row=0, column=1, padx=0)

        if ".doc" in current_rules:
            self.doc.select()
        
        self.xlsx = ctk.CTkCheckBox(self.checkbox_container, 
                                    text=".xlsx",
                                    font=('Arial', 15),
                                    command=self.save_checkboxes)
        self.xlsx.grid(row=0, column=2, padx=0)

        if ".xlsx" in current_rules:
            self.xlsx.select()

    def save_path(self, event=None):
        text = self.path_field.get()

        if os.path.exists(text) and os.path.isdir(text):
            self.app.global_saved_path = text # pyright: ignore[reportAttributeAccessIssue]
            print(f"Valid path saved: {text}")
            self.app.user.data["documents_path"] = text # pyright: ignore[reportAttributeAccessIssue]
            self.app.user.save_to_json(self.app.user.data, "user_data.json")  # pyright: ignore[reportAttributeAccessIssue]
            self.current_path_label.configure(text=f"Current path: {text}", text_color="white") 
        else:
            print("Error: Path does not exist")
            self.current_path_label.configure(text=f"Error: Directory '{text}' not found!", text_color="#FF5555")


    def save_checkboxes(self):
        selected_extensions = []

        if self.docx.get() == 1:
            selected_extensions.append(".docx")
        
        if self.doc.get() == 1:
            selected_extensions.append(".doc")

        if self.xlsx.get() == 1:
            selected_extensions.append(".xlsx")         

        print(f"Save rules: {selected_extensions}")

        self.app.user.data["rules"]["Documents"] = selected_extensions # pyright: ignore[reportAttributeAccessIssue]
        
        self.app.user.save_to_json(self.app.user.data, "user_data.json") # pyright: ignore[reportAttributeAccessIssue]


    def browse_folder(self):
        path = filedialog.askdirectory() 
        if path:
            self.path_field.delete(0, "end") 
            self.path_field.insert(0, path)
            print(f"Chosen dir: {path}")

            self.save_path()

class DocumentsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_propagate(False)

        # self.monitor = MonitorManager(log_callback=self.update_log_box)
        self.title("DirectoryMonitor")
        self.geometry("800x600")
        self.resizable(False, False)
        self.user = User("user_data.json")

        #self.protocol('WM_DELETE_WINDOW', self.withdraw_window)

        self.global_saved_path = "You don't have path"

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)

        self.sidebar = SideBar(self, command=self.select_frame_by_name, width=150)
        self.sidebar.grid(row=0, column=0, padx=15, pady=10, sticky="nsw")


        self.active_frame = None

    def select_frame_by_name(self, name):
        if self.active_frame is not None:
            self.active_frame.grid_forget()

        if name == "default_setting":
            self.active_frame = DefSettingFrame(self, width=605, fg_color="gray25")
        elif name == "documents":
            self.active_frame = DocumentsFrame(self)

        if self.active_frame is not None:
            self.active_frame.grid(row=0, column=1, sticky="nsew")

    def withdraw_window(self):  
        self.withdraw()
        self.tray_thread = threading.Thread(target=self.create_tray_icon)
        self.tray_thread.start()

    def create_tray_icon(self):
        try:

            image = Image.new('RGB', (64, 64), color=(255, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.rectangle((16, 16, 48, 48), fill=(255, 255, 255))

            menu = (
                pystray.MenuItem('Open', self.show_window),
                pystray.MenuItem('Exit', self.quit_window)
            )

            self.icon = pystray.Icon("name", image, "Directory Monitor", menu)
            
            self.icon.run()

        except Exception as e:
            print(f"ПОМИЛКА ТРЕЮ: {e}")
            self.after(0, self.deiconify)

    def show_window(self, icon, item):
        self.icon.stop()
        self.after(0, self.deiconify) 

    def quit_window(self, icon, item):
        self.icon.stop() 
        self.quit()       
        self.destroy()    
        import sys
        sys.exit()   




    #     self.textbox = ctk.CTkTextbox(self, width=300, height=200)
    #     # self.textbox.pack(pady=10)

    #     self.btn_start = ctk.CTkButton(self, text="Start", command=self.start_click)
    #     # self.btn_start.pack(pady=10)

    #     self.btn_stop = ctk.CTkButton(self, text="Stop", command=self.stop_click, state="disabled")
    #     # self.btn_stop.pack(pady=10)

    # Callback 
    # def update_log_box(self, message):
    #     self.textbox.insert("end", message + "\n")
    #     self.textbox.see("end")

    # def start_click(self):
    #     result_message = self.monitor.start()
    #     if result_message:
    #         self.update_log_box(result_message)
    #         self.btn_start.configure(state="disabled")
    #         self.btn_stop.configure(state="normal")

    # def stop_click(self):
    #     result_message = self.monitor.stop()
    #     if result_message:
    #         self.update_log_box(result_message)
    #         self.btn_start.configure(state="normal")
    #         self.btn_stop.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()