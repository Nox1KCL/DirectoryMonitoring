import customtkinter as CTk
# from PIL import Image


class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.title("DirectoryManager")
        self.resizable(False, False)

        self.title_label = CTk.CTkLabel(master=self, 
                                        text="DirectoryManager", 
                                        font=("Arial", 54, "bold"),
                                        text_color="#3498db"
                                        )
        self.title_label.pack(pady=30, padx=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()