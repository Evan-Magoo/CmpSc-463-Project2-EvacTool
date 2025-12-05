import tkinter as tk
import copy
import math
from PIL import Image, ImageTk
from Backend.graph import *
from Backend.app import *

window = tk.Tk()
window.title('Abington Evacuation Tool')
window.geometry('800x800')
window.configure(bg='#001E44')
logo = tk.PhotoImage(file="favicon.png")
window.iconphoto(False, logo)

node_ids = {}
node_labels = {}
current_location = None
destination = None
path_items = []
node_text_id = None
path_length_id = None
path_name_id = None

blocked_items = []      # list of lists of canvas ids drawn to indicate closure
block_selection = []
k_paths = []
k_path_index = 0        # use an int (you previously had a list here)

screen = 0
locations = Abington_Locations
map = Abington_Map

graph_copy = copy.deepcopy(map)

#=========================================================================================
# New: Edge Click Blocking 
line_to_nodes = {}  # map canvas line IDs to tuple (u, v)  # **BLOCKING FEATURE CHANGE**

def on_line_click(event): 
    clicked_items = canvas.find_overlapping(event.x, event.y, event.x, event.y)  
    for item in clicked_items: 
        if item in line_to_nodes: 
            u, v = line_to_nodes[item]  
            if is_blocked(u, v): 
                unblock_edge(u, v) 
                canvas.itemconfig(item, fill='red')  
                print(f"Unblocked edge {u} <-> {v}") 
            else: 
                block_edge(u, v)  
                canvas.itemconfig(item, fill='gray')  
                print(f"Blocked edge {u} <-> {v}")  
            return  
#=========================================================================================

def swap_screen():
    global screen, locations, map
    global current_location, destination, graph_copy
    global k_paths, k_path_index

    screen = (screen + 1) % 2

    clear_screen()

    node_ids.clear()
    node_labels.clear()
    path_items.clear()
    blocked_items.clear()

    k_paths.clear()
    k_path_index = 0

    current_location = None
    destination = None

    graph_copy = copy.deepcopy(Abington_Map if screen == 0 else Woodland_Map)

    if screen == 0:
        locations = Abington_Locations
        map = Abington_Map
        main_screen()
    else:
        locations = Woodland_Locations
        map = Woodland_Map
        woodland_building()

def set_destinantion(d):
    global destination
    destination = d

def set_location_text(node):
    if node in node_ids and node_text_id is not None:
        canvas.itemconfig(node_text_id, text=f"Location: {node}")

def set_path_name_id(idx):
    if path_name_id is not None:
        canvas.itemconfig(path_name_id, text=f"Path ID: {idx+1}")

def set_path_length(length):
    if path_length_id is not None:
        canvas.itemconfig(path_length_id, text=f"Length: {length}ft")

def set_node_color(node, color):
    if node in node_ids:
        canvas.itemconfig(node_ids[node], fill=color)
        try:
            canvas.tag_raise(node_ids[node])
        except Exception:
            pass

def set_node_active_color(node, color):
    if node in node_ids:
        canvas.itemconfig(node_ids[node], activefill=color)
        try:
            canvas.tag_raise(node_ids[node])
        except Exception:
            pass

def reset_node_colors():
    for n in node_ids.keys():
        canvas.itemconfig(node_ids[n], fill='lightblue')
    for node in map:
        originally_had = len(map[node]) > 0
        now_has = len(graph_copy[node]) > 0
        if originally_had and not now_has:
            set_node_color(node, 'yellow')
            set_node_active_color(node, 'orange')
    if current_location and current_location in node_ids:
        set_node_color(current_location, 'dodgerblue')
    for node, (x, y) in locations.items():
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
    global path_items, line_to_nodes
    for item in path_items:
        for i in item:
            try:
                canvas.delete(i)
                if i in line_to_nodes:  # **BLOCKING FEATURE CHANGE**
                    del line_to_nodes[i]  # **BLOCKING FEATURE CHANGE**
            except Exception:
                pass
    path_items = []

def reopen_paths():
    global graph_copy, blocked_items
    graph_copy = copy.deepcopy(map)
    for line_group in blocked_items:
        for line_id in line_group:
            try:
                canvas.delete(line_id)
            except Exception:
                pass
    blocked_items.clear()
    clear_path_visuals()
    update_isolated_nodes()
    print("All closed paths reopened.")

def update_isolated_nodes():
    for node in map:
        originally_had = len(map[node]) > 0
        now_has = len(graph_copy[node]) > 0
        if originally_had and not now_has:
            set_node_color(node, 'yellow')
            set_node_active_color(node, 'yellow')

def get_closest_exit():
    global path_items
    clear_path_visuals()
    route = closest_exit_path(graph_copy, current_location)
    if not route or route[1] is None:
        print("No route found")
        return
    path = route[1]
    edges = list(zip(path[:-1], path[1:]))
    for u, v in edges:
        x1, y1 = locations[u]
        x2, y2 = locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        for lid in line_ids:  # **BLOCKING FEATURE CHANGE**
            line_to_nodes[lid] = (u, v)  # **BLOCKING FEATURE CHANGE**
        path_items.append(line_ids)
    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
            set_node_active_color(node, 'red')

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
        x1, y1 = locations[u]
        x2, y2 = locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        for lid in line_ids:  # **BLOCKING FEATURE CHANGE**
            line_to_nodes[lid] = (u, v)  # **BLOCKING FEATURE CHANGE**
        path_items.append(line_ids)
    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
            set_node_active_color(node, 'red')

def get_k_paths():
    global k_paths
    if not current_location or not destination:
        print("Select a start and destination first")
        return
    all_paths = k_shortest_paths(graph_copy, current_location, destination, k=10)
    if not all_paths:
        print("No paths found")
        return
    k_paths.clear()
    for dist, path in all_paths:
        edges = list(zip(path[:-1], path[1:]))
        if any(is_blocked(u, v) for u, v in edges):
            continue
        k_paths.append((dist, path))
    if not k_paths:
        print("No unblocked paths available")
        return
    display_path(0)
    print("Available unblocked paths:")
    for i, (dist, path) in enumerate(k_paths):
        print(f"{i+1}: {dist} → {' → '.join(path)}")

def display_path(path_index=0):
    global path_items, k_paths, k_path_index
    clear_path_visuals()
    if not k_paths:
        print("No paths available")
        return
    k_path_index = path_index % len(k_paths)
    dist, path = k_paths[k_path_index]
    edges = list(zip(path[:-1], path[1:]))
    set_path_name_id(k_path_index)
    set_path_length(dist)
    for u, v in edges:
        if is_blocked(u, v):
            continue
        x1, y1 = locations[u]
        x2, y2 = locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        for lid in line_ids:  # **BLOCKING FEATURE CHANGE**
            line_to_nodes[lid] = (u, v)  # **BLOCKING FEATURE CHANGE**
        path_items.append(line_ids)
    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
            set_node_active_color(node, 'red')

def close_path(u, v):
    block_edge(u, v)
    clear_path_visuals()
    update_isolated_nodes()

def on_click(event):
    global current_location
    on_line_click(event)  # **BLOCKING FEATURE CHANGE**
    click_x, click_y = event.x, event.y
    for name, (x, y) in locations.items():
        if (click_x - x)**2 + (click_y - y)**2 <= 20:
            current_location = name
            print(f"Clicked on node: {name}")
            for n, oval_id in node_ids.items():
                originally_had = len(map[n]) > 0
                now_has = len(graph_copy[n]) > 0
                if originally_had and not now_has:
                    canvas.itemconfig(oval_id, fill='yellow', activefill='yellow')
                    continue
                if canvas.itemcget(oval_id, "fill") == 'red':
                    continue
                canvas.itemconfig(oval_id, fill='lightblue', activefill='blue')
            originally_had = len(map[name]) > 0
            now_has = len(graph_copy[name]) > 0
            if not (originally_had and not now_has):
                set_node_color(name, 'dodgerblue')
                set_node_active_color(name, 'dodgerblue')
                set_location_text(name)
            break

# main_screen() and woodland_building() remain unchanged

if __name__ == "__main__":
    global canvas_img_ref
    clear_screen()
    main_screen()
    window.mainloop()
