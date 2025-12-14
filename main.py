import tkinter as tk
from core.gui import LAPH_GUI

def main():
    root = tk.Tk()
    app = LAPH_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
