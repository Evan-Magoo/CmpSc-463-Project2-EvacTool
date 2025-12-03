import tkinter as tk
import copy
from PIL import Image, ImageTk
from Backend.graph import Abington_Map, Abington_Locations
from Backend.app import *

window = tk.Tk()
window.title('Abington Evacuation Tool')
window.geometry('800x800')
logo = tk.PhotoImage(file="favicon.png")
window.iconphoto(False, logo)

node_ids={}
node_labels={}
current_location=None
path_items=[]

blocked_edges=[]      # list of tuples like ("A", "B")
blocked_items=[]      # canvas line IDs for blocked edges
block_selection=[]    # stores the two clicked nodes to block

graph_copy = copy.deepcopy(Abington_Map)

def set_node_color(node, color):
    if node in node_ids:
        canvas.itemconfig(node_ids[node], fill=color)
        try:
            canvas.tag_raise(node_ids[node])   # bring oval above path lines if needed
        except Exception:
            pass

def reset_node_colors():
    for n in node_ids.keys():
        # default to lightblue
        canvas.itemconfig(node_ids[n], fill='lightblue')

    # preserve isolated nodes
    for node in Abington_Map:
        originally_had = len(Abington_Map[node]) > 0
        now_has = len(graph_copy[node]) > 0
        if originally_had and not now_has:
            set_node_color(node, 'yellow')

    # preserve selection
    if current_location and current_location in node_ids:
        set_node_color(current_location, 'green')

    for node, (x, y) in Abington_Locations.items():
        if node in node_labels and node_labels[node]:
            for tid in node_labels[node]:
                try:
                    canvas.delete(tid)
                except Exception:
                    pass
        if len(node) > 3:
            node_labels[node] = [
                canvas.create_text(x+4, y-10,  text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10,  text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="white", font=("arial", 9, 'bold')),
            ]

def clear_path_visuals():
    """Remove old path lines (not node ovals) and reset node colors to base state."""
    global path_items
    for item in path_items:
        for i in item:
            try: 
                canvas.delete(i)
            except Exception:
                pass
    path_items = []
    reset_node_colors()

def get_path():
    global path_items
    
    clear_path_visuals()

    route = shortest_path(graph_copy, current_location, "Woodland Building")
    path = route[1]
    edges = list(zip(path[:-1], path[1:]))

    for u, v in edges:
        x1, y1 = Abington_Locations[u]
        x2, y2 = Abington_Locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(11, 15, 6)),
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(9, 13, 4)),
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 16, 6)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 14, 5)),
        ]
        path_items.append(line_ids)

    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')

        if len(node) > 3:
            if node in node_labels and node_labels[node]:
                for tid in node_labels[node]:
                    try:
                        canvas.delete(tid)
                    except Exception:
                        pass
            x, y = Abington_Locations[node]
            node_labels[node] = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="#FFA0A0", font=("arial", 9, 'bold')),
            ]

    print(edges)

def get_closest_path():
    global path_items
    
    clear_path_visuals()

    route = closest_building_path(graph_copy, current_location)
    if not route or route[1] is None:
        print("No route found")
        return
    
    path = route[1]
    edges = list(zip(path[:-1], path[1:]))

    for u, v in edges:
        x1, y1 = Abington_Locations[u]
        x2, y2 = Abington_Locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        path_items.append(line_ids)

    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
    
        if len(node) > 3:
            if node in node_labels and node_labels[node]:
                for tid in node_labels[node]:
                    try:
                        canvas.delete(tid)
                    except Exception:
                        pass
            x, y = Abington_Locations[node]
            node_labels[node] = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="#FFA0A0", font=("arial", 9, 'bold')),
            ]

    print(edges)


def update_isolated_nodes():
    for node in Abington_Map:
        originally_had = len(Abington_Map[node]) > 0
        now_has = len(graph_copy[node]) > 0

        print(originally_had, "=?=", now_has)

        if originally_had and not now_has:
            set_node_color(node, 'yellow')


def on_click(event):
    global current_location
    click_x, click_y = event.x, event.y

    for name, (x, y) in Abington_Locations.items():
        if (click_x - x)**2 + (click_y - y)**2 <= 20:
            current_location = name
            print(f"Clicked on node: {name}")

            for n, oval_id in node_ids.items():
                current_color = canvas.itemcget(oval_id, "fill")

                originally_had = len(Abington_Map[n]) > 0
                now_has = len(graph_copy[n]) > 0

                if originally_had and not now_has:
                    continue

                if current_color == "yellow":
                    continue


            if name in node_ids:
                canvas.itemconfig(node_ids[name], fill='green')
            break


def clear_screen():
    for widget in window.winfo_children():
        widget.destroy()


def on_click_block(event):
    """Select nodes by clicking to block the edge between them."""
    click_x, click_y = event.x, event.y
    for name, (x, y) in Abington_Locations.items():
        if (click_x - x)**2 + (click_y - y)**2 <= 20:
            block_selection.append(name)
            canvas.itemconfig(node_ids[name], fill="orange")
            print(f"Selected node for blocking: {name}")
            break

    if len(block_selection) == 2:
        u, v = block_selection
        close_path(u, v)

        for n in block_selection:
            originally_had = len(Abington_Map[n]) > 0
            now_has = len(graph_copy[n]) > 0

            # If still isolated → keep yellow
            if originally_had and not now_has:
                continue
            
            if n in node_ids:
                canvas.itemconfig(node_ids[n], fill="lightblue")
        block_selection.clear()


def close_path(u, v):
    global path_items, blocked_edges, blocked_items

    if u not in Abington_Map or v not in Abington_Map:
        print(f"Invalid nodes: {u}, {v}")
        return

    if (u, v) in blocked_edges or (v, u) in blocked_edges:
        print(f"Path {u} <-> {v} is already blocked.")
        return

    blocked_edges.append((u, v))

    if u in graph_copy:
        graph_copy[u] = [pair for pair in graph_copy[u] if pair[0] != v]
    if v in graph_copy:
        graph_copy[v] = [pair for pair in graph_copy[v] if pair[0] != u]

    x1, y1 = Abington_Locations[u]
    x2, y2 = Abington_Locations[v]
    line_ids = [
        canvas.create_line(x1, y1, x2, y2, fill='black', width=5.5),
        canvas.create_line(x1, y1, x2, y2, fill='yellow', width=4, dash=(15, 5)),
    ]
    blocked_items.append(line_ids)

    if u in node_ids:
        canvas.tag_raise(node_ids[u])
    if v in node_ids:
        canvas.tag_raise(node_ids[v])

    clear_path_visuals()
    update_isolated_nodes()

    if current_location is None:
        print("No current location selected.")
        return

    try:
        route = shortest_path(graph_copy, current_location, "Woodland Building")
        new_path = route[1]
        edges = list(zip(new_path[:-1], new_path[1:]))
    except:
        print("No alternative path available.")
        return

    for u2, v2 in edges:
        x1, y1 = Abington_Locations[u2]
        x2, y2 = Abington_Locations[v2]
        line_id = canvas.create_line(x1, y1, x2, y2, fill='red', width=2)
        path_items.append(line_id)

    for node in new_path:
        if node in node_ids:
            set_node_color(node, 'red')

    update_isolated_nodes()


def forFlooding(elevation_data, threshold):
    """
    Automatically close all paths where either node is below the flood elevation limit.
    elevation_data: dict like {"A": 310, "B": 280, ...}
    threshold: minimum safe elevation in feet or meters
    """
    print("\n>>> Running Flooding Auto-Closure...")
    for u in Abington_Map:
        for v, _ in Abington_Map[u]:

            # Prevent double-blocking & enforce undirected edges
            if (u, v) in blocked_edges or (v, u) in blocked_edges:
                continue

            # If either node is below threshold → block this edge
            if elevation_data.get(u, 9999) < threshold or elevation_data.get(v, 9999) < threshold:
                print(f"Flooding risk! Closing {u} <-> {v}")
                close_path(u, v)


def forSnowStorm(incline_data, threshold):
    """
    Automatically close all paths where incline between nodes is too steep.
    incline_data: dict of dicts like:
        {
            "A": {"B": 12, "C": 4},
            "B": {"A": 12}
        }
    threshold: maximum safe incline (degrees or %)
    """
    print("\n>>> Running SnowStorm Auto-Closure...")
    for u in Abington_Map:
        for v, _ in Abington_Map[u]:

            # Prevent double-blocking
            if (u, v) in blocked_edges or (v, u) in blocked_edges:
                continue

            incline = 0

            # inclines can be stored A→B or B→A; check both
            if u in incline_data and v in incline_data[u]:
                incline = incline_data[u][v]
            elif v in incline_data and u in incline_data[v]:
                incline = incline_data[v][u]

            # Block if incline is too steep for icy conditions
            if incline > threshold:
                print(f"Snowstorm hazard! Closing steep path {u} <-> {v} (incline={incline})")
                close_path(u, v)
'''
# Example elevation of each node (in feet)
elevation_data = {
    "A": 320, "B": 305, "C": 290, "D": 270, "E": 330, "F": 310,
    "Y": 265, "Z": 260, "AA": 300, "AN": 325,
    # Add all others...
}

# Example incline between nodes
incline_data = {
    "A": {"B": 8, "C": 12},
    "B": {"A": 8, "D": 15},
    "C": {"A": 12, "D": 5},
    "D": {"B": 15, "C": 5},
    # Add all others as needed
}

'''

if __name__ == "__main__":
    global canvas_img_ref
    clear_screen()
    
    campus_img = Image.open("Abington Map.png")
    campus_img = campus_img.resize((800, 640))
    canvas_width, canvas_height = campus_img.size

    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height)
    canvas.pack()

    tk_img = ImageTk.PhotoImage(campus_img)
    canvas.create_image(0, 0, anchor='nw', image=tk_img)
    canvas_img_ref = tk_img

    node_labels = {}

    for node, (x, y) in Abington_Locations.items():
        r = 4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="lightblue", activefill='blue')
        node_ids[node] = oval_id
        if len(node) > 3:
            label_ids = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="white", font=("arial", 9, 'bold')),
            ]
            node_labels[node] = label_ids

    button = tk.Button(window, text="Run Test", command=lambda: get_path())
    button.pack()

    button = tk.Button(window, text="Find Closest Building", command=lambda: get_closest_path())
    button.pack()

    canvas.bind('<Button-1>', on_click)

    close_path('Z', 'AA')
    close_path('Z', 'Y')

    button = tk.Button(window, text="Test Location", command=lambda: print(current_location))
    button.pack()

    button = tk.Button(window, text="Flooding Scenario", command=lambda: forFlooding(elevation_data, threshold=300))
    button.pack()

    button = tk.Button(window, text="Snowstorm Scenario", command=lambda: forSnowStorm(incline_data, threshold=10))
    button.pack()

    window.mainloop()

