from customtkinter import *
from tkinter import *

set_appearance_mode("System")
set_default_color_theme("Green")

class BFSLiveDemonstration():
    def __init__(self):
        super().__init__()

        self.geometry("700x750")

if __name__ == "__main__":
    app = BFSLiveDemonstration()
    app.mainloop()
