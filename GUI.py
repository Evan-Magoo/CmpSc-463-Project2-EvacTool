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

node_ids={}
node_labels={}
current_location=None
destination=None
path_items=[]
node_text_id=None
path_length_id=None
path_name_id=None
blocked_edges=[]      
blocked_items=[]      
block_selection=[]
k_paths = []
k_path_index = []

graph_copy = copy.deepcopy(Abington_Map)

def set_destinantion(d):
    global destination
    destination = d

def set_location_text(node):
    if node in node_ids:
        canvas.itemconfig(node_text_id, text=f"Location: {node}")

def set_path_name_id(id):
    canvas.itemconfig(path_name_id, text=id+1)

def set_path_length(length):
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

    # preserve isolated nodes
    for node in Abington_Map:
        originally_had = len(Abington_Map[node]) > 0
        now_has = len(graph_copy[node]) > 0
        if originally_had and not now_has:
            set_node_color(node, 'yellow')
            set_node_active_color(node, 'orange')

    # preserve selection
    if current_location and current_location in node_ids:
        set_node_color(current_location, 'dodgerblue')

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

def reopen_paths():
    global graph_copy, blocked_edges, blocked_items

    graph_copy = copy.deepcopy(Abington_Map)
    for line_group in blocked_items:
        for line_id in line_group:
            try:
                canvas.delete(line_id)
            except Exception:
                pass
    
    blocked_items.clear()

    blocked_edges.clear()

    clear_path_visuals()

    print("All closed paths reopened.")

def update_isolated_nodes():
    for node in Abington_Map:
        originally_had = len(Abington_Map[node]) > 0
        now_has = len(graph_copy[node]) > 0

        if originally_had and not now_has:
            set_node_color(node, 'yellow')
            set_node_active_color(node, 'yellow')

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
            set_node_active_color(node, 'red')
    
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
            set_node_active_color(node, 'red')

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




def on_click(event):
    global current_location
    click_x, click_y = event.x, event.y

    for name, (x, y) in Abington_Locations.items():
        if (click_x - x)**2 + (click_y - y)**2 <= 20:
            current_location = name
            print(f"Clicked on node: {name}")

            # Reset all nodes except isolated (yellow) and blocked (red)
            for n, oval_id in node_ids.items():
                originally_had = len(Abington_Map[n]) > 0
                now_has = len(graph_copy[n]) > 0

                # Isolated node
                if originally_had and not now_has:
                    canvas.itemconfig(oval_id, fill='yellow', activefill='yellow')
                    continue

                # Blocked node
                if canvas.itemcget(oval_id, "fill") == 'red':
                    continue

                # Normal reset
                canvas.itemconfig(oval_id, fill='lightblue', activefill='blue')

            # Set clicked node to green if not isolated
            originally_had = len(Abington_Map[name]) > 0
            now_has = len(graph_copy[name]) > 0

            if not (originally_had and not now_has):   # not isolated
                set_node_color(name, 'dodgerblue')
                set_node_active_color(name, 'dodgerblue')
                set_location_text(name)

            break


def forFlooding(threshold):
    """
    Automatically close all paths where either node is below the flood elevation limit.
    elevation_data: dict like {"A": 310, "B": 280, ...}
    threshold: minimum safe elevation in feet or meters
    """
    print("\n>>> Running Flooding Auto-Closure...")
    reopen_paths()
    clear_path_visuals()
    for u in Abington_Map:
        for v, _ in Abington_Map[u]:

            # Prevent double-blocking & enforce undirected edges
            if (u, v) in blocked_edges or (v, u) in blocked_edges:
                continue

            # If either node is below threshold → block this edge
            if Abington_Elevations[u] < threshold or Abington_Elevations[v] < threshold:
                print(f"Flooding risk! Closing {u} <-> {v}")
                close_path(u, v)


def forSnowStorm(threshold):
    """
    Automatically close all paths where incline between nodes is too steep.
    incline_data: dict of dicts like:
        {
            "A": {"B": 12, "C": 4},
            "B": {"A": 12}
        }
    threshold: maximum safe incline (degrees)
    """
    print("\n>>> Running SnowStorm Auto-Closure...")
    reopen_paths()
    clear_path_visuals()
    for u in Abington_Map:
        for v, dist in Abington_Map[u]:

            # Prevent double-blocking
            if (u, v) in blocked_edges or (v, u) in blocked_edges:
                continue

            u_elv = Abington_Elevations[u]
            v_elv = Abington_Elevations[v]

            elv_dif = abs(u_elv - v_elv)

            incline = elv_dif / dist

            # inclines can be stored A→B or B→A; check both
            incline_angle = math.degrees(math.atan(incline))

            # Block if incline is too steep for icy conditions
            if incline_angle > threshold:
                print(f"Snowstorm hazard! Closing steep path {u} <-> {v} (incline_angle={incline_angle})")
                close_path(u, v)

def clear_screen():
    for widget in window.winfo_children():
        widget.destroy()

if __name__ == "__main__":
    global canvas_img_ref
    clear_screen()
    
    campus_img = Image.open("Abington Map.png")
    campus_img = campus_img.resize((800, 640))
    canvas_width, canvas_height = campus_img.size

    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height)
    canvas.pack(side=tk.TOP)

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
        bg="#3b5998",
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
        bg="#3b5998",
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

    window.mainloop()
    

