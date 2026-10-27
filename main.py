from tkinter import *

from customtkinter import *

set_appearance_mode("System")
set_default_color_theme("green")


class BFSLiveDemonstration(CTk):
    def __init__(self):
        super().__init__()

        # CustomTkinter new Window Declaration
        self.geometry("700x750")
        self.title("BFS Live Demonstration")

        self.ROWS = 20
        self.COLUMNS = 20
        self.CELL_SIZE = 30  # unit = pixels

        # Defining Grid structure
        self.grid = []
        for i in range(self.ROWS):
            row = []
            for j in range(self.COLUMNS):
                row.append(0)
            self.grid.append(row)

        # Total canvas height and breadth
        canvas_width = self.COLUMNS * self.CELL_SIZE
        canvas_height = self.ROWS * self.CELL_SIZE

        self.canvas = CTkCanvas(
            self,
            width=canvas_width,
            height=canvas_height,
            bg="#000000",
            highlightthickness=1,
        )

        self.canvas.pack(padx=10, pady=10)
        # self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")


if __name__ == "__main__":
    app = BFSLiveDemonstration()
    app.mainloop()
