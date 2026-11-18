import tkinter as tk
from app.interfaz import VentanaLogin

def main():
    root = tk.Tk()
    app = VentanaLogin(root)
    root.mainloop()

if __name__ == "__main__":
    main()