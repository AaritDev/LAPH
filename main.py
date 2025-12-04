import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--clear-logs":
        from core.logger import Logger

        Logger().clear()
        print("L.A.P.H. logs cleared.")
    else:
        from core.gui import LAPH_GUI

        import tkinter as tk

        root = tk.Tk()
        app = LAPH_GUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
