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
current_location = None
path_items = []

blocked_edges = []      # list of tuples like ("A", "B")
blocked_items = []      # canvas line IDs for blocked edges
block_selection = []    # stores the two clicked nodes to block

graph_copy = copy.deepcopy(Abington_Map)


def get_path():
    global path_items
    
    for item in path_items:
        canvas.delete(item)
    path_items = []

    route = shortest_path(graph_copy, current_location, "Woodland Building")
    path = route[1]
    edges = list(zip(path[:-1], path[1:]))

    for u, v in edges:
        x1, y1 = Abington_Locations[u]
        x2, y2 = Abington_Locations[v]
        line_id = canvas.create_line(x1, y1, x2, y2, fill='red', width=2)
        path_items.append(line_id)

    for node in path:
        x, y = Abington_Locations[node]
        r=4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="red")
        path_items.append(oval_id)
        if len(node) > 3:
            canvas.create_text(x+4, y-9, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+4, y-11, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+6, y-9, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+6, y-11, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+5, y-10, text=node, fill="red", font=("arial", 9, 'bold'))

    print(edges)

def get_closest_path():
    global path_items
    
    for item in path_items:
        canvas.delete(item)
    path_items = []

    route = closest_building_path(graph_copy, current_location)
    path = route[1]
    edges = list(zip(path[:-1], path[1:]))

    for u, v in edges:
        x1, y1 = Abington_Locations[u]
        x2, y2 = Abington_Locations[v]
        line_id = canvas.create_line(x1, y1, x2, y2, fill='red', width=2)
        path_items.append(line_id)

    for node in path:
        x, y = Abington_Locations[node]
        r=4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="red")
        path_items.append(oval_id)
        if len(node) > 3:
            canvas.create_text(x+4, y-9, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+4, y-11, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+6, y-9, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+6, y-11, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+5, y-10, text=node, fill="red", font=("arial", 9, 'bold'))

    print(edges)


def on_click(event):
    global current_location
    click_x, click_y = event.x, event.y
    for name, (x, y) in Abington_Locations.items():
        if (click_x - x)**2 + (click_y - y)**2 <= 20:
            current_location = name
            print(f"Clicked on node: {name}")
            for n, oval_id in node_ids.items():
                canvas.itemconfig(oval_id, fill="lightblue")
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
    line_id = canvas.create_line(x1, y1, x2, y2, fill='yellow', width=3)
    for node, (x, y) in Abington_Locations.items():
        r = 4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="lightblue", activefill='blue')
        node_ids[node] = oval_id
    blocked_items.append(line_id)

    for item in path_items:
        canvas.delete(item)
    path_items = []

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
        x, y = Abington_Locations[node]
        r = 4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="red")
        path_items.append(oval_id)

    print(f"Rerouted path: {edges}")


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

    for node, (x, y) in Abington_Locations.items():
        r = 4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="lightblue", activefill='blue')
        node_ids[node] = oval_id
        if len(node) > 3:
            canvas.create_text(x+4, y-9, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+4, y-11, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+6, y-9, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+6, y-11, text=node, fill="black", font=("arial", 9, 'bold'))
            canvas.create_text(x+5, y-10, text=node, fill="white", font=("arial", 9, 'bold'))

    button = tk.Button(window, text="Run Test", command=lambda: get_path())
    button.pack()

    button = tk.Button(window, text="Find Closest Building", command=lambda: get_closest_path())
    button.pack()

    canvas.bind('<Button-1>', on_click)

    close_path('Z', 'AA')
    close_path('Z', 'Y')

    button = tk.Button(window, text="Test Location", command=lambda: print(current_location))
    button.pack()
    window.mainloop()
