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


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.graph = nx.Graph()
        self.master.title("Graph GUI")
        self.nodes = {}  # Store canvas node objects for reference
        self.edges = {}  # Store canvas edge objects for reference
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
                    self.create_edge(self.edge_start, clicked_node)
                self.edge_start = None
            self.deselect_edge()  # Deselect any selected edge when a node is clicked
        else:
            clicked_near_edge = False
            for (node1, node2), edge in self.edges.items():
                x1, y1, x2, y2 = self.canvas.coords(edge)
                if is_near_edge(x1, y1, x2, y2, event.x, event.y):
                    self.deselect_edge()  # Deselect current edge
                    self.selected_edge = (node1, node2)  # Select new edge
                    if self.edge_colors[(node1, node2)] == "black":
                        self.canvas.itemconfig(edge, fill="grey")
                        self.edge_colors[self.selected_edge] = "grey"
                    if self.edge_colors[(node1, node2)] == "red":
                        self.canvas.itemconfig(edge, fill="pink")
                        self.edge_colors[self.selected_edge] = "pink"
                    if self.edge_colors[(node1, node2)] == "blue":
                        self.canvas.itemconfig(edge, fill="cyan")
                        self.edge_colors[self.selected_edge] = "cyan"
                    clicked_near_edge = True
                    break

            if not clicked_near_edge:
                self.deselect_edge()
                self.create_node(event.x, event.y)

    def color_selected_edge_red(self, event):
        if self.selected_edge:
            self.canvas.itemconfig(self.edges[self.selected_edge], fill="red")
            self.edge_colors[self.selected_edge] = "red"

    def color_selected_edge_blue(self, event):
        if self.selected_edge:
            self.canvas.itemconfig(self.edges[self.selected_edge], fill="blue")
            self.edge_colors[self.selected_edge] = "blue"

    def create_node(self, x, y):
        node_id = self.node_counter
        self.node_counter += 1
        self.node_positions[node_id] = (x, y)
        self.nodes[node_id] = self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="green", outline="black")

    def create_edge(self, node1, node2):
        radius = 10
        x1, y1 = self.node_positions[node1]
        x2, y2 = self.node_positions[node2]
        dx = x2 - x1
        dy = y2 - y1
        dist = ((dx ** 2) + (dy ** 2)) ** 0.5
        dx /= dist
        dy /= dist
        adjusted_x1 = x1 + dx * radius
        adjusted_y1 = y1 + dy * radius
        adjusted_x2 = x2 - dx * radius
        adjusted_y2 = y2 - dy * radius
        edge = self.canvas.create_line(adjusted_x1, adjusted_y1, adjusted_x2, adjusted_y2, fill="black")
        self.edges[(node1, node2)] = edge
        self.edge_colors[(node1, node2)] = "black"


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
