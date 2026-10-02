import tkinter as tk
from tkinter import ttk

class Window(tk.Tk):
    def __init__(self, title, window_width, window_height, icon=None):
        super().__init__()
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{window_width}x{window_height}+{int((screen_width-window_width)/2)}+{int((screen_height-window_height)/2)}")
        self.minsize(window_width, window_height)
        self.title(title)
        if icon:
            self.iconbitmap(icon)
        self.update_idletasks()

class Frame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)

class HeadingUsingFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(anchor="center", pady=(15, 0))
    def createHeading(self, heading="", required=False):
        frame = tk.Frame(self, background="white")
        frame.pack(anchor="w")
        tk.Label(frame, text=heading, background="white", fg="black", font=("AppleSystemUIFont", 10, "bold"), anchor="w").pack(side="left")
        if required:
            tk.Label(frame, text="*", background="white", fg="red", font=("AppleSystemUIFont", 10, "bold"), anchor="w").pack(side="left")

class InputBox(ttk.Entry):
    def __init__(self, master=None, heading=None, required=False, **kwargs):
        frame = HeadingUsingFrame(master, background="white")
        self.text = tk.StringVar()
        vcmd = (frame.register(self.validate), "%P")
        super().__init__(frame, textvariable=self.text, validate="key", validatecommand=vcmd, **kwargs)
        if heading:
            frame.createHeading(heading, required=required)
        self.pack(anchor="w")
    def validate(self, value):
        return value == "" or value.isdigit() and len(value) <= 10
    def getText(self):
        return self.text.get()

class DropdownBox(ttk.Combobox):
    def __init__(self, master=None, heading=None, required=False, **kwargs):
        frame = HeadingUsingFrame(master, background="white")
        self.selected = tk.StringVar(value="---Select---")
        super().__init__(frame, textvariable=self.selected, **kwargs)
        if heading:
            frame.createHeading(heading, required=required)
        self.pack(anchor="w")
        self.tip = tk.Toplevel(self)
        self.tip.overrideredirect(True)
        self.tip.withdraw()
        self.tip_label = tk.Label(self.tip, background="lightyellow", relief="solid", borderwidth=1)
        self.tip_label.pack()
        self.bind("<Button-1>", self._bind_listbox)
    def updateValues(self, values=[]):
        self["values"] = values
    def _option_hover_motion(self, y_pos):
        popdown = self.tk.eval(f'ttk::combobox::PopdownWindow {self}')
        listbox = f"{popdown}.f.l"
        index = self.tk.call(listbox, "nearest", y_pos)
        values = self["values"]
        if values and 0 <= int(index) < len(values):
            value = values[int(index)]
            self.tip_label.config(text=value)
            self.tip.geometry(f"+{self.winfo_pointerx()+15}+{self.winfo_pointery()-15}")
            self.tip.attributes("-topmost", True)
            self.tip.deiconify()
    def _option_hover_leave(self):
        self.tip.withdraw()
    def _bind_listbox(self, event=None):
        popdown = self.tk.eval(f'ttk::combobox::PopdownWindow {self}')
        listbox = f"{popdown}.f.l"
        on_hover = self.register(self._option_hover_motion)
        on_leave = self.register(self._option_hover_leave)
        self.tk.call("bind", listbox, "<Motion>", f"{on_hover} %y")
        self.tk.call("bind", listbox, "<Leave>", on_leave)
    
class Button(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(pady=(15, 0))
    def display(self, b: bool):
        if b:
            self.pack(pady=(10, 0))
        else:
            self.pack_forget()

class OutputLabel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(anchor="center", pady=(20, 0))
        self.grid_columnconfigure(0, weight=1)
        self.display_data = {
            "Name": "",
            "Total Rows": "",
            "Complete": "",
            "Not Complete": ""
        }
    def showOutput(self, background: str = None, fg: str = None):
        for widget in self.winfo_children():
            widget.destroy()
        for i, row_key in enumerate(self.display_data):
            tk.Label(self, text=row_key, background=background, fg=fg, font=("Arial", 12, "bold"), anchor="w").grid(row=i, column=0, sticky="w")
            tk.Label(self, text=": ", background=background, fg=fg, font=("Arial", 12, "bold"), anchor="w").grid(row=i, column=1, sticky="w")
            tk.Label(self, text=self.display_data[row_key], background=background, fg=fg, font=("Arial", 12, "normal"), anchor="w").grid(row=i, column=2, sticky="w")
    def display(self, b: bool):
        if b:
            self.pack(anchor="center", pady=(20, 0))
        else:
            self.pack_forget()

class IGNOUGradeCardTable(tk.Toplevel):
    def __init__(self, master = None, header_list: list[str] = [""]*9, marks_data: list[list] = []):
        super().__init__(master)
        self.title("Grade Card")
        self.geometry("960x400")
        self._header_len = len(header_list)
        columns_width = [100, 67, 166, 100]
        columns_width[2:2] = [59] * (self._header_len - 4)
        columns_anchor = [tk.W, tk.W]
        columns_anchor[1:1] = [tk.E] * (self._header_len - 2)
        table = ttk.Treeview(self, columns=["A", "B"], show="headings")
        table = ttk.Treeview(self, columns=header_list, show="headings")
        table.pack(fill="both", expand=True)
        table.tag_configure("dark_blue", background="#0000ff", foreground="#ffffff")
        table.tag_configure("blue", background="#8e8eff", foreground="#ffffff")
        table.tag_configure("white", background="#ffffff", foreground="#000000")
        for i, header in enumerate(header_list):
            table.heading(header, text=header, anchor=tk.CENTER)
            table.column(header, width=columns_width[i], anchor=columns_anchor[i])
        y_scroll = ttk.Scrollbar(self, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=y_scroll.set)
        row_color = False
        for row in marks_data:
            if row_color:
                color = "blue"
            else:
                color = "white"
            table.insert("", tk.END, values=row, tags=(color, ))
            row_color = not row_color
        table.insert("", tk.END, values=[""]*9, tags=("dark_blue", ))

if __name__ == "__main__":
    root = Window("Test", 300, 200)
    d = DropdownBox(root, values=["A", "B", "C", "D", "E"], heading="Alphabets", required=True)
    root.mainloop()