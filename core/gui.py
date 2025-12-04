import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY, SUCCESS, DANGER, WARNING
import threading
from core.repair_loop import RepairLoop

class LAPH_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("L.A.P.H. — Local Autonomous Programming Helper")
        self.root.geometry("900x700")
        self.agent = RepairLoop()
        self.setup_widgets()

    def setup_widgets(self):
        style = tb.Style("darkly")
        frame = tb.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        tb.Label(frame, text="L.A.P.H.", font=("Orbitron", 28, "bold"), bootstyle=PRIMARY).pack(pady=10)
        tb.Label(frame, text="Describe the program you want L.A.P.H. to build:", font=("Segoe UI", 14)).pack(pady=5)
        self.task_entry = tb.Entry(frame, width=80, font=("Segoe UI", 12))
        self.task_entry.pack(pady=5)
        self.run_button = tb.Button(frame, text="Run Task", bootstyle=SUCCESS, command=self.run_task_thread)
        self.run_button.pack(pady=10)
        self.status_label = tb.Label(frame, text="Idle", font=("Segoe UI", 12), bootstyle=PRIMARY)
        self.status_label.pack(pady=5)
        self.output_box = tb.ScrolledText(frame, width=100, height=25, font=("Fira Mono", 12))
        self.output_box.pack(pady=10)

        # Dice roller example button
        tb.Button(frame, text="Dice Roller Example", bootstyle=WARNING, command=self.fill_dice_prompt).pack(pady=5)

    def fill_dice_prompt(self):
        example = (
            "a program that makes a simple dice roller where you can choose any dice with any amount of sides and then roll them, "
            "maybe add extra dice like two 20 sided dices or 1 four sided dice, and 2 six sided dices, all rolling together "
            "(and maybe total all the dices values and also make it so whatever the dice rolls to you can add a custom value to it)"
        )
        self.task_entry.delete(0, "end")
        self.task_entry.insert(0, example)

    def run_task_thread(self):
        threading.Thread(target=self.run_task, daemon=True).start()

    def run_task(self):
        task = self.task_entry.get()
        self.status_label.config(text="Running...", bootstyle=WARNING)
        self.output_box.delete(1.0, "end")
        final_code = self.agent.run_task(task)
        if final_code:
            self.status_label.config(text="Success!", bootstyle=SUCCESS)
            self.output_box.insert("end", final_code)
        else:
            self.status_label.config(text="Failed after max iterations.", bootstyle=DANGER)