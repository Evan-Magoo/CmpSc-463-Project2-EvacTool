import tkinter as tk
from tkinter import *
import Backend.app

window = tk.Tk()
window.title('Abington Evacuation Tool')
window.geometry('900x600')
logo = tk.PhotoImage(file="lapel-shield.png")
window.iconphoto(True, logo)

def main_screen():
    clear_screen()
    logo_label = tk.Label(window, image=resized_logo_subsample)
    logo_label.pack(side=TOP)

    label = tk.Label(window, text="Playlist Pilot", font=font.Font(size=22))
    label.pack()

def clear_screen():
    for widget in window.winfo_children():
        widget.destroy()

if __name__ == "__main__":
    window.mainloop()