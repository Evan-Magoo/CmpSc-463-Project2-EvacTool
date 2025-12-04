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

blocked_edges = []      # list of tuples (u, v)
blocked_items = []      # list of lists of canvas ids drawn to indicate closure
block_selection = []
k_paths = []
k_path_index = 0        # use an int (you previously had a list here)

screen = 0
locations = Abington_Locations
map = Abington_Map

graph_copy = copy.deepcopy(map)

def swap_screen():
    global screen, locations, map
    global current_location, destination, graph_copy
    global k_paths, k_path_index

    # toggle screen (0 = Abington, 1 = Woodland)
    screen = (screen + 1) % 2

    # wipe old widgets/canvas
    clear_screen()

    # reset run-time stored data
    node_ids.clear()
    node_labels.clear()
    path_items.clear()
    blocked_edges.clear()
    blocked_items.clear()

    k_paths.clear()
    k_path_index = 0

    current_location = None
    destination = None

    # reset underlying graph to default
    graph_copy = copy.deepcopy(Abington_Map if screen == 0 else Woodland_Map)

    # load correct screen
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
    # idx is the path index (int)
    if path_name_id is not None:
        canvas.itemconfig(path_name_id, text=f"Path ID: {idx+1}")

def set_path_length(length):
    if path_length_id is not None:
        canvas.itemconfig(path_length_id, text=f"Length: {length}ft")

def set_node_color(node, color):
    if node in node_ids:
        canvas.itemconfig(node_ids[node], fill=color)
        try:
            canvas.tag_raise(node_ids[node])   # bring oval above path lines if needed
        except Exception:
            pass

def set_node_active_color(node, color):
    if node in node_ids:
        canvas.itemconfig(node_ids[node], activefill=color)
        try:
            canvas.tag_raise(node_ids[node])   # bring oval above path lines if needed
        except Exception:
            pass

def reset_node_colors():
    for n in node_ids.keys():
        # default to lightblue
        canvas.itemconfig(node_ids[n], fill='lightblue')

    # preserve isolated nodes (compare original map vs graph_copy)
    for node in map:
        originally_had = len(map[node]) > 0
        now_has = len(graph_copy[node]) > 0
        if originally_had and not now_has:
            set_node_color(node, 'yellow')
            set_node_active_color(node, 'orange')

    # preserve selection
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

def reopen_paths():
    global graph_copy, blocked_edges, blocked_items

    graph_copy = copy.deepcopy(map)
    # delete any drawn blocked indicators
    for line_group in blocked_items:
        for line_id in line_group:
            try:
                canvas.delete(line_id)
            except Exception:
                pass

    blocked_items.clear()
    blocked_edges.clear()
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
        # use current locations dict (works for Woodland or Abington depending on screen)
        x1, y1 = locations[u]
        x2, y2 = locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        path_items.append(line_ids)

    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
            set_node_active_color(node, 'red')

        if len(node) > 3:
            if node in node_labels and node_labels[node]:
                for tid in node_labels[node]:
                    try:
                        canvas.delete(tid)
                    except Exception:
                        pass
            x, y = locations[node]
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
        x1, y1 = locations[u]
        x2, y2 = locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        path_items.append(line_ids)

    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
            set_node_active_color(node, 'red')

        if len(node) > 3:
            if node in node_labels and node_labels[node]:
                for tid in node_labels[node]:
                    try:
                        canvas.delete(tid)
                    except Exception:
                        pass
            x, y = locations[node]
            node_labels[node] = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="#FFA0A0", font=("arial", 9, 'bold')),
            ]

    print(edges)

def get_k_paths():
    global k_paths
    if not current_location or not destination:
        print("Select a start and destination first")
        return

    all_paths = k_shortest_paths(graph_copy, current_location, destination, k=10)
    if not all_paths:
        print("No paths found")
        return

    k_paths = []
    for dist, path in all_paths:
        edges = list(zip(path[:-1], path[1:]))
        if any((u, v) in blocked_edges or (v, u) in blocked_edges for u, v in edges):
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

    k_path_index = path_index % len(k_paths)  # loop around if out of bounds
    dist, path = k_paths[k_path_index]
    edges = list(zip(path[:-1], path[1:]))

    set_path_name_id(k_path_index)
    set_path_length(dist)

    for u, v in edges:
        # Skip blocked edges
        if (u, v) in blocked_edges or (v, u) in blocked_edges:
            print(f"Skipping blocked edge {u} <-> {v}")
            continue

        x1, y1 = locations[u]
        x2, y2 = locations[v]
        line_ids = [
            canvas.create_line(x1, y1, x2, y2, fill='black', width=4, arrow=tk.LAST, arrowshape=(10, 12, 5)),
            canvas.create_line(x1, y1, x2, y2, fill='red', width=2, arrow=tk.LAST, arrowshape=(10, 12, 5)),
        ]
        path_items.append(line_ids)

    for node in path:
        if node in node_ids:
            set_node_color(node, 'red')
            set_node_active_color(node, 'red')

        if len(node) > 3:
            if node in node_labels and node_labels[node]:
                for tid in node_labels[node]:
                    try:
                        canvas.delete(tid)
                    except Exception:
                        pass
            x, y = locations[node]
            node_labels[node] = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="#FFA0A0", font=("arial", 9, 'bold')),
            ]

def close_path(u, v):
    global path_items, blocked_edges, blocked_items, graph_copy

    # use current map (works for Abington or Woodland)
    if u not in map or v not in map:
        print(f"Invalid nodes: {u}, {v}")
        return

    if (u, v) in blocked_edges or (v, u) in blocked_edges:
        print(f"Path {u} <-> {v} is already blocked.")
        return

    blocked_edges.append((u, v))

    # remove from graph_copy (undirected)
    if u in graph_copy:
        graph_copy[u] = [pair for pair in graph_copy[u] if pair[0] != v]
    if v in graph_copy:
        graph_copy[v] = [pair for pair in graph_copy[v] if pair[0] != u]

    # draw blocked indicator using current locations
    x1, y1 = locations[u]
    x2, y2 = locations[v]
    line_ids = [
        canvas.create_line(x1, y1, x2, y2, fill='black', width=5.5),
        canvas.create_line(x1, y1, x2, y2, fill='yellow', width=4, dash=(4, 4)),
    ]
    blocked_items.append(line_ids)

    if u in node_ids:
        canvas.tag_raise(node_ids[u])
    if v in node_ids:
        canvas.tag_raise(node_ids[v])

    clear_path_visuals()
    update_isolated_nodes()

def on_click(event):
    global current_location
    click_x, click_y = event.x, event.y

    for name, (x, y) in locations.items():
        if (click_x - x)**2 + (click_y - y)**2 <= 20:
            current_location = name
            print(f"Clicked on node: {name}")

            # Reset all nodes except isolated (yellow) and blocked (red)
            for n, oval_id in node_ids.items():
                originally_had = len(map[n]) > 0
                now_has = len(graph_copy[n]) > 0

                # Isolated node
                if originally_had and not now_has:
                    canvas.itemconfig(oval_id, fill='yellow', activefill='yellow')
                    continue

                # Blocked node (we consider nodes already colored 'red' blocked)
                if canvas.itemcget(oval_id, "fill") == 'red':
                    continue

                # Normal reset
                canvas.itemconfig(oval_id, fill='lightblue', activefill='blue')

            # Set clicked node to green if not isolated
            originally_had = len(map[name]) > 0
            now_has = len(graph_copy[name]) > 0

            if not (originally_had and not now_has):   # not isolated
                set_node_color(name, 'dodgerblue')
                set_node_active_color(name, 'dodgerblue')
                set_location_text(name)

            break

def forFlooding(threshold):
    """
    Automatically close all paths where either node is below the flood elevation limit.
    """
    print("\n>>> Running Flooding Auto-Closure...")
    reopen_paths()
    clear_path_visuals()
    for u in map:
        for v, _ in map[u]:
            # Prevent double-blocking & enforce undirected edges
            if (u, v) in blocked_edges or (v, u) in blocked_edges:
                continue

            # If either node is below threshold → block this edge
            # use Abington_Elevations / Woodland_Elevations depending on current locations map
            # try to select the correct elevation dict:
            try:
                elv_u = Abington_Elevations[u] if u in Abington_Elevations else Woodland_Elevations[u]
                elv_v = Abington_Elevations[v] if v in Abington_Elevations else Woodland_Elevations[v]
            except Exception:
                # fallback: try single dicts or assume Abington_Elevations exists
                elv_u = Abington_Elevations.get(u, 0)
                elv_v = Abington_Elevations.get(v, 0)

            if elv_u < threshold or elv_v < threshold:
                print(f"Flooding risk! Closing {u} <-> {v}")
                close_path(u, v)

def forSnowStorm(threshold):
    """
    Automatically close all paths where incline between nodes is too steep.
    threshold: max safe incline angle in degrees
    """
    print("\n>>> Running SnowStorm Auto-Closure...")
    reopen_paths()
    clear_path_visuals()
    for u in map:
        for v, dist in map[u]:
            # Prevent double-blocking
            if (u, v) in blocked_edges or (v, u) in blocked_edges:
                continue

            # Try to get elevations from either elevation dict
            try:
                u_elv = Abington_Elevations[u] if u in Abington_Elevations else Woodland_Elevations[u]
                v_elv = Abington_Elevations[v] if v in Abington_Elevations else Woodland_Elevations[v]
            except Exception:
                u_elv = Abington_Elevations.get(u, 0)
                v_elv = Abington_Elevations.get(v, 0)

            elv_dif = abs(u_elv - v_elv)
            if dist == 0:
                continue
            incline = elv_dif / dist
            incline_angle = math.degrees(math.atan(incline))

            # Block if incline is too steep for icy conditions
            if incline_angle > threshold:
                print(f"Snowstorm hazard! Closing steep path {u} <-> {v} (incline_angle={incline_angle})")
                close_path(u, v)

def forFireScenario():
    print("\n>>> Running Fire Scenario...")
    reopen_paths()
    clear_path_visuals()
    close_path('D', 'E')
    close_path('F', 'E')
    close_path('E', 'J')
    close_path('E', 'Exit 9')

def clear_screen():
    for widget in window.winfo_children():
        widget.destroy()

# ---------- main_screen and woodland_building remain mostly the same but now use locations/global map ----------
def main_screen():
    global canvas, canvas_img_ref, node_labels, node_ids, node_text_id, path_name_id, path_length_id, k_path_index, locations, map

    # ensure we are using Abington assets for this screen
    locations = Abington_Locations
    map = Abington_Map

    campus_img = Image.open("Abington Map.png")
    campus_img = campus_img.resize((800, 640))
    canvas_width, canvas_height = campus_img.size

    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height)
    canvas.pack(side=tk.TOP)

    tk_img = ImageTk.PhotoImage(campus_img)
    canvas.create_image(0, 0, anchor='nw', image=tk_img)
    canvas_img_ref = tk_img

    node_labels = {}

    for node, (x, y) in locations.items():
        r = 4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="lightblue", activefill='blue')
        node_ids[node] = oval_id
        if len(node) > 3:
            label_ids = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="white", font=("arial", 9, 'bold'))
            ]
            node_labels[node] = label_ids

    canvas.bind('<Button-1>', on_click)

    controls = tk.Frame(window, bg="#001E44")
    controls.pack(pady=10)

    button = tk.Button(
        controls,
        text="Find Closest Building",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: get_closest_path())
    button.grid(row=0, column=0, padx=5)

    controls.grid_columnconfigure(2, minsize=180)

    button = tk.Button(
        controls,
        text="Flooding Scenario",
        width=20,
        bg="#DB7C6B",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: forFlooding(threshold=265)
    )
    button.grid(row=0, column=3, padx=5)

    button = tk.Button(
        controls,
        text="Snowstorm Scenario",
        width=20,
        bg="#DB7C6B",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: forSnowStorm(threshold=5)
    )
    button.grid(row=1, column=3, padx=5)

    button = tk.Button(
        controls,
        text="Reopen Paths",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: reopen_paths()
    )
    button.grid(row=0, column=1, padx=5)

    button = tk.Button(
        controls,
        text="Find Path to Building",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        bd=2,
        command=get_k_paths
    )
    button.grid(row=1, column=0, padx=5, pady=10)

    selected_option = tk.StringVar()
    selected_option.set('Choose Location')
    option_menu = tk.OptionMenu(
        controls,
        selected_option,
        *Buildings,
        command=lambda chosen: set_destinantion(chosen)
    )
    option_menu.config(
        width=18,
        bg="white",
        fg="#1e407c",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        relief="ridge",
        bd=2
    )
    menu = option_menu["menu"]
    menu.config(
        bg="white",
        fg="black",
        activebackground="#1e407c",   # hover color
        activeforeground="white",
        font=("Arial", 11)
    )
    option_menu.grid(row=2, column=0, padx=5)

    node_text_id = canvas.create_text(
        10,
        10,
        text="Location: None",
        fill="#1e407c",
        font=("Arial", 16, "bold"),
        anchor="nw"
    )

    path_name_id = canvas.create_text(
        10,
        32,
        text="Path ID: 0",
        fill="#1e407c",
        font=("Arial", 16, "bold"),
        anchor="nw"
    )

    path_length_id = canvas.create_text(
        10,
        54,
        text="Length: 0ft",
        fill="#1e407c",
        font=("Arial", 16, "bold"),
        anchor="nw"
    )

    button = tk.Button(
        controls,
        text="Next Path",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        command=lambda: display_path(k_path_index + 1)
    )
    button.grid(row=2, column=1, padx=5)

    button = tk.Button(
        controls,
        text="Switch Map",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        command=lambda: swap_screen()
    )
    button.grid(row=2, column=3, padx=5)

def woodland_building():
    global canvas, canvas_img_ref, node_labels, node_ids, node_text_id, path_name_id, path_length_id, k_path_index, locations, map

    # ensure Woodland assets used
    locations = Woodland_Locations
    map = Woodland_Map

    campus_img = Image.open("Woodland Building.png")
    campus_img = campus_img.resize((800, 640))
    canvas_width, canvas_height = campus_img.size

    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height)
    canvas.pack(side=tk.TOP)

    tk_img = ImageTk.PhotoImage(campus_img)
    canvas.create_image(0, 0, anchor='nw', image=tk_img)
    canvas_img_ref = tk_img

    node_labels = {}

    for node, (x, y) in locations.items():
        r = 4
        oval_id = canvas.create_oval(x-r, y-r, x+r, y+r, fill="lightblue", activefill='blue')
        node_ids[node] = oval_id
        if len(node) > 3:
            label_ids = [
                canvas.create_text(x+4, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+4, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-10, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+6, y-12, text=node, fill="black", font=("arial", 9, 'bold')),
                canvas.create_text(x+5, y-11, text=node, fill="white", font=("arial", 9, 'bold'))
            ]
            node_labels[node] = label_ids

    canvas.bind('<Button-1>', on_click)

    controls = tk.Frame(window, bg="#001E44")
    controls.pack(pady=10)

    button = tk.Button(
        controls,
        text="Find Closest Exit",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: get_closest_exit())
    button.grid(row=0, column=0, padx=5)

    controls.grid_columnconfigure(2, minsize=180)

    button = tk.Button(
        controls,
        text="Fire Scenario",
        width=20,
        bg="#DB7C6B",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="white",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: forFireScenario()
    )
    button.grid(row=0, column=3, padx=5)

    button = tk.Button(
        controls,
        text="Reopen Paths",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        command=lambda: reopen_paths()
    )
    button.grid(row=0, column=1, padx=5)

    button = tk.Button(
        controls,
        text="Find Path to Exit",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        bd=2,
        command=get_k_paths
    )
    button.grid(row=1, column=0, padx=5, pady=10)

    selected_option = tk.StringVar()
    selected_option.set('Choose Location')
    option_menu = tk.OptionMenu(
        controls,
        selected_option,
        *Woodland_Exits,
        command=lambda chosen: set_destinantion(chosen)
    )
    option_menu.config(
        width=18,
        bg="white",
        fg="#1e407c",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        highlightthickness=0,
        relief="ridge",
        bd=2
    )
    menu = option_menu["menu"]
    menu.config(
        bg="white",
        fg="black",
        activebackground="#1e407c",   # hover color
        activeforeground="white",
        font=("Arial", 11)
    )
    option_menu.grid(row=2, column=0, padx=5)

    node_text_id = canvas.create_text(
        10,
        10,
        text="Location: None",
        fill="#1e407c",
        font=("Arial", 16, "bold"),
        anchor="nw"
    )

    path_name_id = canvas.create_text(
        10,
        32,
        text="Path ID: 0",
        fill="#1e407c",
        font=("Arial", 16, "bold"),
        anchor="nw"
    )

    path_length_id = canvas.create_text(
        10,
        54,
        text="Length: 0ft",
        fill="#1e407c",
        font=("Arial", 16, "bold"),
        anchor="nw"
    )

    button = tk.Button(
        controls,
        text="Next Path",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        command=lambda: display_path(k_path_index + 1)
    )
    button.grid(row=2, column=1, padx=5)

    button = tk.Button(
        controls,
        text="Switch Map",
        width=20,
        bg="#3b5998",
        fg="white",
        font=("Arial", 11, "bold"),
        activebackground="#96BEE6",
        activeforeground="white",
        command=lambda: swap_screen()
    )
    button.grid(row=2, column=3, padx=5)


if __name__ == "__main__":
    global canvas_img_ref
    clear_screen()
    main_screen()
    window.mainloop()
