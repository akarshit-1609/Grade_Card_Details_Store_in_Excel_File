from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from customTkinterClasses import *
from gradecard import IGNOUGradeCard
import threading
from pathlib import Path

def updateProgramme(event):
    global gradecard, status_type_dropdown, programme_code_dropdown
    hide_output(event)
    programme_code_dropdown.config(state="disabled")
    programme_code_dropdown.set("---Select---")
    programme_code_dropdown.select_clear()
    try:
        gradecard.fetch_programs(status_type_dropdown.get())
        l = list(gradecard.program_options.keys())
        programme_code_dropdown.updateValues(l)
    except Exception as e:
        error_message = str(e).split(":")
        messagebox.showerror(error_message[0], error_message[1])
        programme_code_dropdown.updateValues([])
    programme_code_dropdown.config(state="readonly")

def hide_output(event):
    global output, export_button
    export_button.display(False)
    output.display(False)

def fetch_marksheet():
    global gradecard, status_type_dropdown, programme_code_dropdown, enrolnment_input, fetch_button, output, show_button, export_button
    show_button.display(False)
    export_button.display(False)
    output.display(False)
    fetch_button.config(state="disabled")
    if status_type_dropdown.current() == -1:
        messagebox.showerror("Invalid Input", "Status For field not selected.")
        fetch_button.config(state="normal")
        return
    if programme_code_dropdown.current() == -1:
        messagebox.showerror("Invalid Input", "Programme Code field not selected.")
        fetch_button.config(state="normal")
        return
    if enrolnment_input.get() == "":
        messagebox.showerror("Invalid Input", "Enrolnment No field is empty.")
        fetch_button.config(state="normal")
        return
    try:
        marksheet_found = gradecard.get_datails_and_marksheet(status_type_dropdown.get(), programme_code_dropdown.get(), enrolnment_input.get())
        if marksheet_found:
            complete_count = 0
            not_complete_count = 0
            for i in gradecard.student_details["Marksheet"][1:]:
                if len(i) == 9:
                    if i[8] == "COMPLETED":
                        complete_count = complete_count + 1
                    elif i[8] == "NOT COMPLETED":
                        not_complete_count = not_complete_count + 1
            output.display_data["Name"] = gradecard.student_details["Name"]
            output.display_data["Total Rows"] = str(len(gradecard.student_details["Marksheet"])-1)
            output.display_data["Complete"] = str(complete_count)
            output.display_data["Not Complete"] = str(not_complete_count)
            output.display(True)
            show_button.display(True)
            output.showOutput(background="#ffffff", fg="#019C01")
            export_button.display(True)
        else:
            messagebox.showwarning("Not Found", "Your Marksheet not found.", icon="error")
    except Exception as e:
        error_message = str(e).split(":")
        messagebox.showerror(error_message[0], error_message[1])
    fetch_button.config(state="normal")

def show_marksheet():
    global window, gradecard
    IGNOUGradeCardTable(
        window,
        header_list = gradecard.student_details["Marksheet"][0],
        marks_data = gradecard.student_details["Marksheet"][1:]
    )

def save_in_file():
    global gradecard, export_button
    export_button.config(state="disabled")
    default_filename = f'{gradecard.student_details["Name"].lower().replace(" ", "_")}_{gradecard.student_details["Enrolment No"]}.xlsx'
    file_path = filedialog.asksaveasfilename(
        initialdir=Path(__file__).parent,
        initialfile=default_filename,
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
        title="Save File",
    )
    if file_path:
        gradecard.marksheet_save_in_excel_file(file_path)
    export_button.config(state="normal")

window = Window("IGNOU Grade Card", 400, 450)
style = ttk.Style()
style.theme_use("clam")
frame = Frame(window, background="#ffffff")

def main():
    global window, style, frame, gradecard, status_type_dropdown, programme_code_dropdown, enrolnment_input, fetch_button, output, show_button, export_button
    some_error = True
    while some_error:
        try:
            gradecard = IGNOUGradeCard()
            l = list(gradecard.status_for_options.keys())
            some_error = False
        except Exception as e:
            error_message = str(e).split(":")
            fetch_problem = messagebox.askretrycancel(error_message[0], error_message[1])
            if not fetch_problem:
                window.destroy()
    status_type_dropdown = DropdownBox(frame, heading="Status For", required=True, width=42, values=l, state="readonly")
    status_type_dropdown.bind("<<ComboboxSelected>>", lambda e: threading.Thread(target=lambda: updateProgramme(e), daemon=True).start())
    programme_code_dropdown = DropdownBox(frame, heading="Programme Code", required=True, width=42, values=[], state="readonly")
    programme_code_dropdown.bind("<<ComboboxSelected>>", lambda e: threading.Thread(target=lambda: hide_output(e), daemon=True).start())
    enrolnment_input = InputBox(frame, heading="Enrolnment No", required=True, width=45)
    enrolnment_input.bind("<Return>", lambda e: threading.Thread(target=fetch_marksheet, daemon=True).start())
    style.configure("fetch_button.TButton", background="#1e80f7", foreground="#ffffff", borderwidth=0, padding=4)
    style.map(
        "fetch_button.TButton",
        background=[("pressed", "#0f4ea3"), ("active", "#1666c1"), ("disabled", "#cccccc")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff"), ("disabled", "#000000")])
    fetch_button = Button(frame, text="Search", style="fetch_button.TButton", width=45, command=lambda: threading.Thread(target=fetch_marksheet, daemon=True).start())
    output = OutputLabel(frame, background="white")
    output.showOutput(background="#ffffff", fg="#019C01")
    style.configure("Treeview.Heading", background="#0000ff", foreground="#ffffff")
    style.configure("show_button.TButton", background="#20c20a", foreground="#ffffff", borderwidth=0, padding=4)
    style.map(
        "show_button.TButton",
        background=[("pressed", "#0da540"), ("active", "#549e0f"), ("disabled", "#cccccc")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff"), ("disabled", "#000000")])
    show_button = Button(frame, text="View Marksheet", style="show_button.TButton", width=45, command=lambda: threading.Thread(target=show_marksheet, daemon=True).start())
    show_button.display(False)
    style.configure("export_button.TButton", background="#f08930", foreground="#ffffff", borderwidth=0, padding=4)
    style.map(
        "export_button.TButton",
        background=[("pressed", "#b95f17"), ("active", "#d9731f"), ("disabled", "#cccccc")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff"), ("disabled", "#000000")])
    export_button = Button(frame, text="Save Marksheet in Excel File", style="export_button.TButton", width=45, command=lambda: threading.Thread(target=save_in_file, daemon=True).start())
    export_button.display(False)
    output.display(False)

window.after(100, lambda: threading.Thread(target=main, daemon=True).start())
window.mainloop()