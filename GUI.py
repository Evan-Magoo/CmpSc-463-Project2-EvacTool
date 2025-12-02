import tkinter as tk
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

def get_path():
    global path_items
    
    for item in path_items:
        canvas.delete(item)
    path_items = []

    route = shortest_path(Abington_Map, "Woodland Building", current_location)
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

    canvas.bind('<Button-1>', on_click)

    button = tk.Button(window, text="Test Location", command=lambda: print(current_location))
    button.pack()
    window.mainloop()