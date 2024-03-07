import tkinter as tk
import networkx as nx


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

        self.canvas.bind("<Button-1>", self.handle_canvas_click)
        self.master.bind("r", self.color_selected_edge_red)
        self.master.bind("b", self.color_selected_edge_blue)
        self.canvas.pack()

    def handle_canvas_click(self, event):
        clicked_node = None
        for node, pos in self.node_positions.items():
            if (event.x - pos[0]) ** 2 + (event.y - pos[1]) ** 2 <= 400:  # Node radius check
                clicked_node = node
                break

        if clicked_node is not None:
            if self.edge_start is None:
                self.edge_start = clicked_node
            else:
                # Prevent creating a loop from a node to itself
                if self.edge_start != clicked_node:
                    self.create_edge(self.edge_start, clicked_node)
                self.edge_start = None
        else:
            # Check if clicking near an edge before deciding to create a new node
            clicked_near_edge = False
            for (node1, node2), line in self.edges.items():
                x1, y1, x2, y2 = self.canvas.coords(line)
                if self.is_near_line(x1, y1, x2, y2, event.x, event.y):
                    self.select_edge((node1, node2))
                    clicked_near_edge = True
                    break

            if not clicked_near_edge:
                self.create_node(event.x, event.y)

    def is_near_line(self, x1, y1, x2, y2, x, y, tolerance=10):
        """Check if a point (x, y) is near the line segment (x1, y1, x2, y2)"""
        # Line segment length
        line_len = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if line_len == 0:
            return False  # Line is a point

        # Using the projection to determine the distance
        dot = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / line_len ** 2
        closest_x = x1 + dot * (x2 - x1)
        closest_y = y1 + dot * (y2 - y1)
        d = ((closest_x - x) ** 2 + (closest_y - y) ** 2) ** 0.5

        return d <= tolerance

    def select_edge(self, edge):
        """Select an edge without changing other edges' colors."""
        if self.selected_edge is not None and self.selected_edge in self.edge_colors:
            # Only highlight the selected edge without changing its color
            self.canvas.itemconfig(self.edges[self.selected_edge], fill=self.edge_colors[self.selected_edge])
        else:
            # If there was no previously selected edge or it doesn't have a specific color, do nothing special
            pass

        self.selected_edge = edge
        # Highlight the selected edge (optional, if you want a visual cue for selection)
        self.canvas.itemconfig(self.edges[edge],
                               fill="green")  # Or remove this if you don't want to change the color upon selection

    def color_selected_edge_red(self, event):
        if self.selected_edge:
            self.canvas.itemconfig(self.edges[self.selected_edge], fill="red")
            self.edge_colors[self.selected_edge] = "red"  # Update color information

    def color_selected_edge_blue(self, event):
        if self.selected_edge:
            self.canvas.itemconfig(self.edges[self.selected_edge], fill="blue")
            self.edge_colors[self.selected_edge] = "blue"  # Update color information

    def create_node(self, x, y):
        node_id = self.node_counter
        self.node_counter += 1
        self.node_positions[node_id] = (x, y)
        self.nodes[node_id] = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="green", outline="black")

    def create_edge(self, node1, node2):
        x1, y1 = self.node_positions[node1]
        x2, y2 = self.node_positions[node2]
        edge_id = self.canvas.create_line(x1, y1, x2, y2, fill="black")  # Simple line for edge
        self.edges[(node1, node2)] = edge_id


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
