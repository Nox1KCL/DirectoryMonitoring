import customtkinter as ctk
from monitor import MonitorManager


class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)

        self.opt_default_setting = ctk.CTkButton(self, 
                                                 text='Default setting', 
                                                 command=self.default_setting)
        self.opt_default_setting.grid(row=1, column=0, padx=5,pady=5, sticky="ew")

        self.opt_documents = ctk.CTkButton(self, 
                                           text='Documents', 
                                           command=self.default_setting)
        self.opt_documents.grid(row=2, column=0, padx=5,pady=5, sticky="ew")
        
        self.opt_pictures = ctk.CTkButton(self, 
                                          text='Pictures', 
                                          command=self.default_setting)
        self.opt_pictures.grid(row=3, column=0, padx=5,pady=5, sticky="ew")

    def default_setting(self):
        self.path = ctk.CTkLabel(self, text='Path')
        self.path.grid(row=2, column=4)
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_propagate(False)

        self.title("DirectoryMonitor")
        self.geometry("800x600")

        # self.monitor = MonitorManager(log_callback=self.update_log_box)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)

        self.my_frame = MyFrame(self, width=150)
        self.my_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsw")




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