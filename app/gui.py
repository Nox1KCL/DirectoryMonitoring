import customtkinter as ctk
from monitor import MonitorManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DirectoryMonitor")
        self.geometry("400x300")

        self.monitor = MonitorManager(log_callback=self.update_log_box)

        self.textbox = ctk.CTkTextbox(self, width=300, height=200)
        self.textbox.pack(pady=10)


        self.btn_start = ctk.CTkButton(self, text="Start", command=self.start_click)
        self.btn_start.pack(pady=10)

        self.btn_stop = ctk.CTkButton(self, text="Stop", command=self.stop_click, state="disabled") # Спочатку вимкнена
        self.btn_stop.pack(pady=10)


    def update_log_box(self, message):
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")

    def start_click(self):
        result_message = self.monitor.start()
        if result_message:
            self.update_log_box(result_message)
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")

    def stop_click(self):
        result_message = self.monitor.stop()
        if result_message:
            self.update_log_box(result_message)
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()