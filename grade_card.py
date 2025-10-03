import tkinter as tk
import requests
import re
import mysql.connector
import subprocess
import os

from tkinter import ttk
from termcolor import colored
from xlsxwriter import Workbook

rootuser = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306"
)

mysql_exe = "mysql"
mysql_login_file = "--defaults-file=mylogin.cnf"
mysql_args = ["--table", "-D", "grade_cards", "-e"]
mysql_default_command = [mysql_exe, mysql_login_file, *mysql_args]

database_name = "grade_cards"
query = rootuser.cursor()
def default_database():
    query.execute(f"show databases like '{database_name}'")
    t = query.fetchall()
    if (len(t) != 1):
        query.execute(f"create database {database_name}")
    query.execute(f"use {database_name}")

    query.execute("show tables like 'all_recorded_data'")
    t = query.fetchall()
    if (len(t) != 1):
        q = "create table all_recorded_data(enrolnment_number varchar(20), name char(50), programme_code varchar(20), grade_card_type varchar(5), table_name varchar(80) primary key)"
        query.execute(q)
default_database()

window = tk.Tk()
wt = 320
ht = 320
window.geometry(f"{wt+50}x{ht}+800+50")
window.title("Grade Card")
window.configure(bg="white")

heading_color = "green"
table_color = "light_cyan"

frame1 = tk.Frame(window, background="white", width=wt/2)
frame1.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
frame1.grid_columnconfigure(0, weight=1)

frame2 = tk.Frame(window, background="white", width=wt/2)
frame2.pack(side=tk.RIGHT, fill="both", expand=True, padx=10)
frame2.grid_columnconfigure(0, weight=1)

enrolnment = tk.StringVar()
programme = tk.StringVar()
grade_card_type = tk.StringVar()
current_name = tk.StringVar(value="--Select--")
all_dropdown_items = []
dropdown_selected = []


def all_dropdown_items_fetch():
    global all_dropdown_items, dropdown_menu
    default_database()
    query.execute("select * from all_recorded_data")
    t = query.fetchall()
    all_dropdown_items.clear()
    all_names = []
    for i in t:
        all_dropdown_items.append([i[0], i[1], i[2], i[3], i[4]])
        all_names.append(i[1])
    dropdown_menu["values"] = all_names
    
def fetch(enrolment_number, programme_code, grade_card_t):
    fetch_remark.config(text="")
    r = requests.get(f"https://gradecard.ignou.ac.in/gradecard/view_gradecard.aspx?eno={str(enrolment_number)}&prog={programme_code}&type={grade_card_t}")

    content = r.content.decode("utf-8")
    content = content.replace("\r", "")
    content = content.replace("\t", "")
    content = content.replace("\n", "")

    try:
        table = re.findall('<table cellspacing="0" cellpadding="8" align="Center" border="0" id="ctl00_ContentPlaceHolder1_gvDetail" width="100%">(.*?)</table>', content)[0]
    except:
        fetch_remark.config(text="Error:- No Record Found", fg="red")
        return None
    
    default_database()
    name = re.findall('Name:.*?<b>(.*?)</b>.*?Programme Code:', content)[0]

    tr = re.findall('<tr align="center" valign=".*?" bgcolor=".*?">(.*?)</tr>', table)
    th = re.findall('<th scope="col"><font face="Arial" color="White" size="4"><b>(.*?)</b></font></th>', tr[0])

    table_name = (f"{name.replace(" ", "_")}_{str(enrolment_number)}_{str(programme_code)}_{str(grade_card_t)}").lower()
    query.execute(f"select * from all_recorded_data where table_name='{str(table_name)}'")
    t = query.fetchall()
    if (len(t) != 1):
        query.execute(f"insert into all_recorded_data value('{enrolment_number}', '{name.title()}', '{programme_code}', '{grade_card_t}', '{table_name}')")

    query.execute(f"show tables like '{table_name}'")
    t = query.fetchall()

    if (len(t) != 1):
        q = f"create table {table_name}("
        for i in range(len(th)):
            if (th[i] == th[-1]):
                q += f"{th[i].replace(" ", "_")} varchar(50))"
            elif (th[i].lower() == "course"):
                q += f"{th[i].replace(" ", "_")} varchar(50) primary key, "
            else:
                q += f"{th[i].replace(" ", "_")} varchar(50), "
        query.execute(q)
    else:
        query.execute(f"truncate table {table_name}")

    tr.pop(0)

    insert = f"insert into {table_name} value ("
    for i in tr:
        td = re.findall('<td><font face="Arial" color=".*?" size="4">(.*?)</font></td>', i)
        for j in range(len(td)-1):
            insert += f"'{td[j]}', "
        insert += f"'{td[len(td)-1]}')"
        query.execute(insert)
        insert = f"insert into {table_name} value ("

    rootuser.commit()
    fetch_remark.config(text="Done", fg="green")
    all_dropdown_items_fetch()

def update_dropdown_selected_item():
    global dropdown_selected
    name = current_name.get()
    name_index = dropdown_menu.current()
    if (name != "--Select--"):
        dropdown_selected = all_dropdown_items[name_index]

def update_marks():
    update_dropdown_selected_item()
    name = current_name.get()
    if (name != "--Select--"):
        fetch(dropdown_selected[0], dropdown_selected[2], dropdown_selected[3])

def show_marks():
    update_dropdown_selected_item()
    name = current_name.get()
    if (name != "--Select--"):
        course = dropdown_selected[2]
        table_name = dropdown_selected[4]

        q = f"select count(*) from {table_name}"
        query.execute(q)
        t = query.fetchall()
        count = t[0][0]

        q = f"select * from {table_name}"
        output = subprocess.check_output([*mysql_default_command, q], universal_newlines=True)
        print(colored(f"Enrolnment No: {dropdown_selected[0]}\tName: {name}\tProgramme Code: {course}\tTotal Rows: {count}",heading_color,attrs=["bold"]))
        print(colored(output, table_color))

def show_marks_c():
    update_dropdown_selected_item()
    name = current_name.get()
    if (name != "--Select--"):
        course = dropdown_selected[2]
        table_name = dropdown_selected[4]
        
        q = f"select count(*) from {table_name} where STATUS='COMPLETED'"
        query.execute(q)
        t = query.fetchall()
        count = t[0][0]

        q = f"select * from {table_name} where STATUS='COMPLETED'"
        output = subprocess.check_output([*mysql_default_command, q], universal_newlines=True)
        print(colored(f"Enrolnment No: {dropdown_selected[0]}\tName: {name}\tProgramme Code: {course}\tTotal Rows: {count}",heading_color,attrs=["bold"]))
        print(colored(output, table_color))

def show_marks_nc():
    update_dropdown_selected_item()
    name = current_name.get()
    if (name != "--Select--"):
        course = dropdown_selected[2]
        table_name = dropdown_selected[4]
        
        q = f"select count(*) from {table_name} where STATUS='NOT COMPLETED'"
        query.execute(q)
        t = query.fetchall()
        count = t[0][0]

        q = f"select * from {table_name} where STATUS='NOT COMPLETED'"
        output = subprocess.check_output([*mysql_default_command, q], universal_newlines=True)
        print(colored(f"Enrolnment No: {dropdown_selected[0]}\tName: {name}\tProgramme Code: {course}\tTotal Rows: {count}",heading_color,attrs=["bold"]))
        print(colored(output, table_color))

def export_into_excel():
    update_dropdown_selected_item()
    name = current_name.get()
    if (name != "--Select--"):
        course = dropdown_selected[2]
        table_name = dropdown_selected[4]
        excel_file_name = f"{os.environ["USERPROFILE"]}\\Desktop\\{table_name}.xlsx"
        excel_file = Workbook(excel_file_name)
        excel_write = excel_file.add_worksheet()

        heading_format = excel_file.add_format({
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "center",
            "bg_color": "#0000dd",
            "font_color": "#ffffff"
        })
        merge_format = excel_file.add_format({
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "center",
            "font_size": 15,
            "bg_color": "#ffff00",
            "font_color": "#000000"
        })

        user_format = excel_file.add_format({
            "border": 1,
            "align": "center",
            "valign": "center",
            "bg_color": "#b8f3fd",
            "font_color": "#000000"
        })

        marks_format_dict = {
            "border": 1,
            "font_color": "#000000"
        }

        excel_write.write(1, 1, "Name", heading_format)
        excel_write.write(1, 2, "Enrolnment No", heading_format)
        excel_write.write(1, 3, "Programme Code", heading_format)
        excel_write.write(2, 1, name, user_format)
        excel_write.write(2, 2, dropdown_selected[0], user_format)
        excel_write.write(2, 3, course, user_format)

        excel_write.set_column(1, 3, 16)
        excel_write.set_column(7, 7, 21)
        excel_write.set_column(8, 8, 25)
        excel_write.set_column(9, 9, 16)

        excel_write.set_row(4, 15)

        q = f"describe {table_name}"
        query.execute(q)
        table_description = query.fetchall()
        for i, heading in enumerate(table_description):
            excel_write.write(5, i+1, heading[0].replace("_", " "), heading_format)

        q = f"select * from {table_name}"
        query.execute(q)
        table_data = query.fetchall()

        excel_write.merge_range(4, 1, 4, len(table_data[0])+0, "Grade Card", merge_format)

        row_design = True
        for i, row in enumerate(table_data):
            new_design = marks_format_dict
            if row_design:
                if (row[-1] == "COMPLETED"):
                    new_design["bg_color"] = "#99ff99"
                elif (row[-1] == "NOT COMPLETED"):
                    new_design["bg_color"] = "#ff9999"
                row_design = False
            else:
                if (row[-1] == "COMPLETED"):
                    new_design["bg_color"] = "#ddffdd"
                elif (row[-1] == "NOT COMPLETED"):
                    new_design["bg_color"] = "#ffdddd"
                row_design = True
            marks_format = excel_file.add_format(new_design)
            for j, data in enumerate(row):
                if (data == "-"):
                    data = ""
                elif (data.isnumeric()):
                    data = int(data)
                excel_write.write(i+6, j+1, data, marks_format)
        excel_file.close()
        print(colored(f"Export File :- {excel_file_name} ", "light_green"))


enrolnment_input = tk.Entry(frame1, textvariable=enrolnment)
enrolnment_input.grid(row=0, column=0, pady=5)

programme_input = tk.Entry(frame1, textvariable=programme)
programme_input.insert(0, "BCA")
programme_input.grid(row=1, column=0, pady=5)

type_input = tk.Entry(frame1, textvariable=grade_card_type)
type_input.insert(0, "1")
type_input.grid(row=2, column=0, pady=5)

tk.Button(frame1, text="Fetch", background="green", fg="white", command=lambda: fetch(enrolnment.get(), programme.get(), grade_card_type.get())).grid(row=3, column=0, pady=5)

fetch_remark = tk.Label(frame1, text="", bg="white", fg="green")
fetch_remark.grid(row=4, column=0, pady=5)

dropdown_menu = ttk.Combobox(frame2, textvariable=current_name, values=dropdown_selected, state="readonly")
dropdown_menu.grid(row=0, column=0, pady=5)

tk.Button(frame2, text="Update", width=int(wt/2), background="green", fg="white", command=update_marks).grid(row=1, column=0, pady=5)
tk.Button(frame2, text="Show all marks", width=int(wt/2), background="yellow", command=show_marks).grid(row=2, column=0, pady=5)
tk.Button(frame2, text="Show only completed", width=int(wt/2), background="yellow", command=show_marks_c).grid(row=3, column=0, pady=5)
tk.Button(frame2, text="show only not completed", width=int(wt/2), background="yellow", command=show_marks_nc).grid(row=4, column=0, pady=5)
tk.Button(frame2, text="Export into excel", width=int(wt/2), background="#ff7700", fg="white", command=export_into_excel).grid(row=5, column=0, pady=5)

all_dropdown_items_fetch()

window.mainloop()

rootuser.close()