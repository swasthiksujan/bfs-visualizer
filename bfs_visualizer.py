"""
BFS Pathfinding Visualizer
--------------------------
Requirements:
    pip install customtkinter

Run:
    python bfs_visualizer.py

Controls:
    - Select Wall, Start, or End mode.
    - Click/drag to draw or erase walls in Wall mode.
    - Click a cell in Start/End mode to move that marker.
    - Run BFS to animate exploration and the shortest path.
"""

from collections import deque
import tkinter as tk
import customtkinter as ctk


class BFSPathfindingVisualizer(ctk.CTk):
    ROWS = 20
    COLS = 20
    CELL_SIZE = 27
    CANVAS_PADDING = 12

    # Dark palette
    BG = "#242424"
    PANEL = "#2B2B2B"
    CANVAS_BG = "#1B1B1B"
    GRID_LINE = "#34383D"
    WALL_COLOR = "#59636F"
    START_COLOR = "#22C55E"
    END_COLOR = "#EF4444"
    UNVISITED_COLOR = "#1B1B1B"
    FRONTIER_COLOR = "#2563EB"
    VISITED_COLOR = "#164E63"
    PATH_COLOR = "#FBBF24"
    TEXT_COLOR = "#E5E7EB"
    MUTED_TEXT = "#A3A3A3"

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("BFS Pathfinding Visualizer")
        self.configure(fg_color=self.BG)
        self.resizable(False, False)

        self.canvas_width = self.COLS * self.CELL_SIZE
        self.canvas_height = self.ROWS * self.CELL_SIZE

        self.start = (2, 2)
        self.end = (17, 17)
        self.walls = set()

        self.mode = tk.StringVar(value="Wall")
        self.is_running = False
        self.animation_job = None
        self.search_generator = None
        self.visited_count = 0
        self.path_length = 0
        self.cells = {}  # (row, col) -> Canvas rectangle ID

        self._build_ui()
        self._draw_grid()
        self._update_stats("Ready — add walls, then run BFS.")

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        outer.pack(padx=18, pady=16)

        header = ctk.CTkFrame(outer, fg_color=self.BG, corner_radius=0)
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="BFS PATHFINDING",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=self.TEXT_COLOR,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Breadth-First Search  •  Unweighted shortest path",
            font=ctk.CTkFont(size=12),
            text_color=self.MUTED_TEXT,
        ).pack(anchor="w", pady=(2, 0))

        body = ctk.CTkFrame(outer, fg_color=self.BG, corner_radius=0)
        body.pack()

        canvas_frame = ctk.CTkFrame(
            body, fg_color=self.CANVAS_BG, corner_radius=8,
            border_width=1, border_color="#3A3A3A"
        )
        canvas_frame.grid(row=0, column=0, padx=(0, 14), sticky="n")

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.CANVAS_BG,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(padx=self.CANVAS_PADDING, pady=self.CANVAS_PADDING)
        self.canvas.bind("<Button-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)

        side = ctk.CTkFrame(body, fg_color=self.PANEL, corner_radius=10, width=220)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)

        ctk.CTkLabel(
            side, text="CONTROLS", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=14, pady=(14, 8))

        ctk.CTkLabel(
            side, text="Edit mode", text_color=self.MUTED_TEXT,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=14)

        for label, color in (
            ("Wall", "#475569"),
            ("Start", self.START_COLOR),
            ("End", self.END_COLOR),
        ):
            ctk.CTkRadioButton(
                side,
                text=label,
                variable=self.mode,
                value=label,
                command=self._mode_changed,
                radiobutton_width=17,
                radiobutton_height=17,
                font=ctk.CTkFont(size=12),
            ).pack(anchor="w", padx=14, pady=4)

        ctk.CTkFrame(side, height=1, fg_color="#444444").pack(
            fill="x", padx=14, pady=10
        )

        self.run_button = ctk.CTkButton(
            side, text="▶  Run BFS", height=36, command=self.run_bfs,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.run_button.pack(fill="x", padx=14, pady=(0, 8))

        self.reset_button = ctk.CTkButton(
            side, text="Reset Search", height=32, command=self.reset_search,
            fg_color="#444444", hover_color="#555555"
        )
        self.reset_button.pack(fill="x", padx=14, pady=4)

        self.clear_button = ctk.CTkButton(
            side, text="Clear Walls", height=32, command=self.clear_walls,
            fg_color="#444444", hover_color="#555555"
        )
        self.clear_button.pack(fill="x", padx=14, pady=4)

        self.reset_all_button = ctk.CTkButton(
            side, text="Reset Everything", height=32, command=self.reset_everything,
            fg_color="#444444", hover_color="#555555"
        )
        self.reset_all_button.pack(fill="x", padx=14, pady=4)

        ctk.CTkFrame(side, height=1, fg_color="#444444").pack(
            fill="x", padx=14, pady=10
        )

        ctk.CTkLabel(
            side, text="LEGEND", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.MUTED_TEXT
        ).pack(anchor="w", padx=14, pady=(0, 6))

        legend = [
            (self.START_COLOR, "Start"),
            (self.END_COLOR, "Destination"),
            (self.WALL_COLOR, "Wall"),
            (self.VISITED_COLOR, "Visited"),
            (self.FRONTIER_COLOR, "Frontier"),
            (self.PATH_COLOR, "Shortest path"),
        ]
        for color, label in legend:
            line = ctk.CTkFrame(side, fg_color="transparent")
            line.pack(fill="x", padx=14, pady=2)
            swatch = ctk.CTkFrame(
                line, width=12, height=12, fg_color=color, corner_radius=3
            )
            swatch.pack(side="left", padx=(0, 8))
            swatch.pack_propagate(False)
            ctk.CTkLabel(
                line, text=label, font=ctk.CTkFont(size=11),
                text_color=self.TEXT_COLOR
            ).pack(side="left")

        ctk.CTkFrame(side, height=1, fg_color="#444444").pack(
            fill="x", padx=14, pady=10
        )

        ctk.CTkLabel(
            side, text="SEARCH STATS", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.MUTED_TEXT
        ).pack(anchor="w", padx=14, pady=(0, 6))

        self.visited_label = ctk.CTkLabel(
            side, text="Visited: 0", font=ctk.CTkFont(size=12)
        )
        self.visited_label.pack(anchor="w", padx=14, pady=2)

        self.path_label = ctk.CTkLabel(
            side, text="Path length: —", font=ctk.CTkFont(size=12)
        )
        self.path_label.pack(anchor="w", padx=14, pady=2)

        self.status_label = ctk.CTkLabel(
            outer,
            text="",
            anchor="w",
            justify="left",
            text_color=self.MUTED_TEXT,
            font=ctk.CTkFont(size=12),
        )
        self.status_label.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(
            outer,
            text="Tip: In Wall mode, click or drag to paint walls; drag over a wall to erase it.",
            text_color=self.MUTED_TEXT,
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w", pady=(4, 0))

    def _draw_grid(self):
        self.canvas.delete("all")
        self.cells.clear()

        # Draw cell fills first, then thin grid lines over them.
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x1 = col * self.CELL_SIZE
                y1 = row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.UNVISITED_COLOR,
                    outline=self.GRID_LINE,
                    width=1,
                )
                self.cells[(row, col)] = rect

        self._redraw_all_cells()

    def _cell_color(self, cell):
        if cell == self.start:
            return self.START_COLOR
        if cell == self.end:
            return self.END_COLOR
        if cell in self.walls:
            return self.WALL_COLOR
        return self.UNVISITED_COLOR

    def _redraw_all_cells(self):
        for cell, rect in self.cells.items():
            self.canvas.itemconfigure(rect, fill=self._cell_color(cell))

    def _paint_cell(self, cell, color):
        rect = self.cells.get(cell)
        if rect is not None:
            self.canvas.itemconfigure(rect, fill=color)

    def _cell_from_event(self, event):
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            return (row, col)
        return None

    def _on_canvas_press(self, event):
        cell = self._cell_from_event(event)
        if cell is not None:
            self._edit_cell(cell, initial=True)

    def _on_canvas_drag(self, event):
        cell = self._cell_from_event(event)
        if cell is not None:
            self._edit_cell(cell, initial=False)

    def _edit_cell(self, cell, initial=False):
        if self.is_running:
            return

        mode = self.mode.get()
        if mode == "Start":
            if initial and cell != self.end and cell not in self.walls:
                self.start = cell
                self._clear_search_visuals()
                self._redraw_all_cells()
                self._update_stats("Start node moved.")
            return

        if mode == "End":
            if initial and cell != self.start and cell not in self.walls:
                self.end = cell
                self._clear_search_visuals()
                self._redraw_all_cells()
                self._update_stats("Destination moved.")
            return

        # Wall mode: choose draw/erase once per press, then keep that action
        # during a drag. This makes painting continuous and predictable.
        if initial:
            self._drag_action = "erase" if cell in self.walls else "draw"

        if cell == self.start or cell == self.end:
            return

        if self._drag_action == "erase":
            self.walls.discard(cell)
            self._paint_cell(cell, self.UNVISITED_COLOR)
        else:
            self.walls.add(cell)
            self._paint_cell(cell, self.WALL_COLOR)

        # Clear old search colors as well, so editing after a run never leaves stale overlays.
        self._clear_search_visuals()
        self._update_stats(f"Editing walls — {len(self.walls)} wall cell(s).")

    def _mode_changed(self):
        labels = {
            "Wall": "Wall mode: click/drag to draw or erase obstacles.",
            "Start": "Start mode: click an open cell to move the start node.",
            "End": "End mode: click an open cell to move the destination.",
        }
        self._update_stats(labels.get(self.mode.get(), "Ready."))

    def _update_stats(self, message=None):
        self.visited_label.configure(text=f"Visited: {self.visited_count}")
        self.path_label.configure(
            text=f"Path length: {self.path_length if self.path_length else '—'}"
        )
        if message is not None:
            self.status_label.configure(text=message)

    def _clear_search_visuals(self, keep_grid=False):
        self.visited_count = 0
        self.path_length = 0
        if not keep_grid:
            self._redraw_all_cells()
        self._update_stats()

    def reset_search(self):
        self._stop_animation()
        self._clear_search_visuals()
        self._update_stats("Search visualization cleared. Your walls and markers remain.")

    def clear_walls(self):
        if self.is_running:
            self._stop_animation()
        self.walls.clear()
        self._clear_search_visuals()
        self._redraw_all_cells()
        self._update_stats("All walls cleared.")

    def reset_everything(self):
        self._stop_animation()
        self.start = (2, 2)
        self.end = (17, 17)
        self.walls.clear()
        self._clear_search_visuals()
        self._redraw_all_cells()
        self._update_stats("Grid reset to its initial state.")

    def _stop_animation(self):
        if self.animation_job is not None:
            try:
                self.after_cancel(self.animation_job)
            except tk.TclError:
                pass
        self.animation_job = None
        self.search_generator = None
        self.is_running = False
        if hasattr(self, "run_button"):
            self.run_button.configure(state="normal", text="▶  Run BFS")

    def run_bfs(self):
        if self.is_running:
            return

        self._stop_animation()
        self._clear_search_visuals()
        self._redraw_all_cells()

        self.is_running = True
        self.run_button.configure(state="disabled", text="Searching…")
        self.search_generator = self._bfs_steps()
        self._update_stats("BFS started — exploring the grid…")
        self._animate_next_step()

    def _neighbors(self, cell):
        row, col = cell
        # Four-directional movement: up, right, down, left.
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nxt = (row + dr, col + dc)
            if 0 <= nxt[0] < self.ROWS and 0 <= nxt[1] < self.COLS:
                yield nxt

    def _bfs_steps(self):
        """
        Generator yielding visual events while performing BFS.

        queue (deque): cells waiting to be explored.
        visited (set): cells discovered already, preventing duplicate queue entries.
        parent (dict): child -> previous cell; used to reconstruct the path.
        """
        queue = deque([self.start])
        visited = {self.start}
        parent = {self.start: None}

        while queue:
            current = queue.popleft()

            if current == self.end:
                # Follow parent links backwards from the destination to the start.
                path = []
                node = self.end
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()

                for cell in path:
                    yield ("path", cell, len(visited), len(path) - 1)
                yield ("done", "Path found", len(visited), len(path) - 1)
                return

            # Mark the expanded cell as visited, except for special markers.
            if current != self.start:
                yield ("visited", current, len(visited), 0)

            for neighbor in self._neighbors(current):
                if neighbor in visited or neighbor in self.walls:
                    continue

                # Mark as discovered when enqueued, not when dequeued.
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

                if neighbor != self.end:
                    yield ("frontier", neighbor, len(visited), 0)

        yield ("done", "No path exists — try removing some walls.", len(visited), 0)

    def _animate_next_step(self):
        if not self.is_running or self.search_generator is None:
            return

        # Process a small batch per frame for smooth animation without freezing Tk.
        try:
            for _ in range(3):
                event = next(self.search_generator)
                kind = event[0]

                if kind == "visited":
                    _, cell, count, _ = event
                    self.visited_count = count
                    self._paint_cell(cell, self.VISITED_COLOR)
                    self._update_stats(f"Exploring… {count} cell(s) discovered.")
                elif kind == "frontier":
                    _, cell, count, _ = event
                    self.visited_count = count
                    self._paint_cell(cell, self.FRONTIER_COLOR)
                    self._update_stats(f"Exploring… {count} cell(s) discovered.")
                elif kind == "path":
                    _, cell, count, length = event
                    self.visited_count = count
                    self.path_length = length
                    if cell != self.start and cell != self.end:
                        self._paint_cell(cell, self.PATH_COLOR)
                    self._update_stats("Destination reached — highlighting shortest path…")
                elif kind == "done":
                    _, message, count, length = event
                    self.visited_count = count
                    self.path_length = length
                    self.is_running = False
                    self.search_generator = None
                    self.animation_job = None
                    self.run_button.configure(state="normal", text="▶  Run BFS")
                    self._update_stats(message)
                    return
        except StopIteration:
            self.is_running = False
            self.search_generator = None
            self.animation_job = None
            self.run_button.configure(state="normal", text="▶  Run BFS")
            return

        self.animation_job = self.after(18, self._animate_next_step)


if __name__ == "__main__":
    app = BFSPathfindingVisualizer()
    app.mainloop()
