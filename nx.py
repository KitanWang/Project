import tkinter as tk
import networkx as nx


def is_near_edge(x1, y1, x2, y2, x, y, tolerance=10):
    edge_len = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if edge_len == 0:
        return False
    dot = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / edge_len ** 2
    closest_x = x1 + dot * (x2 - x1)
    closest_y = y1 + dot * (y2 - y1)
    d = ((closest_x - x) ** 2 + (closest_y - y) ** 2) ** 0.5
    return d <= tolerance


class Command:
    """Abstract command class."""
    def execute(self):
        pass

    def undo(self):
        pass


class CreateNodeCommand(Command):
    """Command to create a node."""
    def __init__(self, app, x, y):
        self.app = app
        self.x = x
        self.y = y
        self.node_id = None

    def execute(self):
        self.node_id = self.app.node_counter
        self.app.node_counter += 1
        self.app.node_positions[self.node_id] = (self.x, self.y)
        self.app.nodes[self.node_id] = self.app.canvas.create_oval(self.x - 10, self.y - 10, self.x + 10, self.y + 10, fill="green", outline="black")

    def undo(self):
        if self.node_id is not None:
            self.app.canvas.delete(self.app.nodes[self.node_id])
            del self.app.nodes[self.node_id]
            del self.app.node_positions[self.node_id]


class CreateEdgeCommand(Command):
    """Command to create an edge."""
    def __init__(self, app, node1, node2):
        self.app = app
        self.node1 = node1
        self.node2 = node2

    def execute(self):
        x1, y1 = self.app.node_positions[self.node1]
        x2, y2 = self.app.node_positions[self.node2]
        self.create_edge(x1, y1, x2, y2)

    def undo(self):
        if (self.node1, self.node2) in self.app.edges:
            edge = self.app.edges[(self.node1, self.node2)]
            self.app.canvas.delete(edge)
            del self.app.edges[(self.node1, self.node2)]
            del self.app.edge_colors[(self.node1, self.node2)]

    def create_edge(self, x1, y1, x2, y2):
        radius = 10
        dx = x2 - x1
        dy = y2 - y1
        dist = ((dx ** 2) + (dy ** 2)) ** 0.5
        if dist == 0:
            return
        dx /= dist
        dy /= dist
        adjusted_x1 = x1 + dx * radius
        adjusted_y1 = y1 + dy * radius
        adjusted_x2 = x2 - dx * radius
        adjusted_y2 = y2 - dy * radius
        edge = self.app.canvas.create_line(adjusted_x1, adjusted_y1, adjusted_x2, adjusted_y2, fill="black")
        self.app.edges[(self.node1, self.node2)] = edge
        self.app.edge_colors[(self.node1, self.node2)] = "black"


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.graph = nx.Graph()
        self.master.title("Graph GUI")
        self.nodes = {}
        self.edges = {}
        self.node_counter = 0
        self.node_positions = {}
        self.edge_start = None
        self.selected_edge = None
        self.edge_colors = {}
        self.canvas = tk.Canvas(master, width=600, height=600, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.canvas.bind("<Button-1>", self.handle_canvas_click)
        self.master.bind("r", self.color_selected_edge_red)
        self.master.bind("b", self.color_selected_edge_blue)

        self.undo_stack = []
        self.redo_stack = []
        self.master.bind("<Control-z>", self.undo)
        self.master.bind("<Control-y>", self.redo)

    def handle_canvas_click(self, event):
        clicked_node = None
        for node, pos in self.node_positions.items():
            if (event.x - pos[0]) ** 2 + (event.y - pos[1]) ** 2 <= 100:
                clicked_node = node
                break

        if clicked_node is not None:
            if self.edge_start is None:
                self.edge_start = clicked_node
            else:
                if self.edge_start != clicked_node:
                    # Use command to create an edge
                    self.execute_command(CreateEdgeCommand(self, self.edge_start, clicked_node))
                self.edge_start = None
            self.deselect_edge()
        else:
            clicked_near_edge = False
            for (node1, node2), edge in self.edges.items():
                x1, y1, x2, y2 = self.canvas.coords(edge)
                if is_near_edge(x1, y1, x2, y2, event.x, event.y):
                    self.deselect_edge()  # Deselect current edge
                    self.selected_edge = (node1, node2)  # Select new edge
                    self.highlight_selected_edge()
                    clicked_near_edge = True
                    break

            if not clicked_near_edge:
                self.deselect_edge()
                self.execute_command(CreateNodeCommand(self, event.x, event.y))

    def execute_command(self, command):
        """Executes a command, adds it to the undo stack, and clears the redo stack."""
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def highlight_selected_edge(self):
        """Highlights the selected edge based on its current color."""
        if self.selected_edge:
            edge = self.edges[self.selected_edge]
            if self.edge_colors[self.selected_edge] == "black":
                self.canvas.itemconfig(edge, fill="grey")
                self.edge_colors[self.selected_edge] = "grey"
            elif self.edge_colors[self.selected_edge] == "red":
                self.canvas.itemconfig(edge, fill="pink")
                self.edge_colors[self.selected_edge] = "pink"
            elif self.edge_colors[self.selected_edge] == "blue":
                self.canvas.itemconfig(edge, fill="cyan")
                self.edge_colors[self.selected_edge] = "cyan"

    def deselect_edge(self):
        if self.selected_edge:
            if self.edge_colors[self.selected_edge] == "grey":
                self.canvas.itemconfig(self.edges[self.selected_edge], fill="black")
                self.edge_colors[self.selected_edge] = "black"
            if self.edge_colors[self.selected_edge] == "pink":
                self.canvas.itemconfig(self.edges[self.selected_edge], fill="red")
                self.edge_colors[self.selected_edge] = "red"
            if self.edge_colors[self.selected_edge] == "cyan":
                self.canvas.itemconfig(self.edges[self.selected_edge], fill="blue")
                self.edge_colors[self.selected_edge] = "blue"
        self.selected_edge = None

    def color_selected_edge_red(self, event):
        if self.selected_edge:
            self.canvas.itemconfig(self.edges[self.selected_edge], fill="pink")
            self.edge_colors[self.selected_edge] = "pink"

    def color_selected_edge_blue(self, event):
        if self.selected_edge:
            self.canvas.itemconfig(self.edges[self.selected_edge], fill="cyan")
            self.edge_colors[self.selected_edge] = "cyan"

    def undo(self, event=None):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self, event=None):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()