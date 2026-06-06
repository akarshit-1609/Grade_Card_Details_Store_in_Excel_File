import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from bs4 import BeautifulSoup
from xlsxwriter import Workbook

class IGNOUGradeCard:
    def __init__(self):
        self.default_url = "https://gradecard.ignou.ac.in/"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0"
        }
        self.tag_ids = {
            "status_for": "ddlGradecardfor",
            "programme_id": "ddlProgram",
            "student_enrolnment_no": "ctl00_ContentPlaceHolder1_lblDispEnrolno",
            "student_name": "ctl00_ContentPlaceHolder1_lblDispname",
            "student_program_code": "ctl00_ContentPlaceHolder1_lblDispProgCode",
            "student_marksheet": "ctl00_ContentPlaceHolder1_gvDetail"
        }
        self.payload = {
            "__VIEWSTATE": "",
            "__VIEWSTATEGENERATOR": "",
            "__VIEWSTATEENCRYPTED": "",
            "__EVENTVALIDATION": "",
            self.tag_ids["status_for"]: 0
        }
        self.student_details = {
            "Name": "",
            "Programme Code": "",
            "Enrolment No": "",
            "Marksheet": [[]]
        }
        self.session = requests.Session()
        try:
            response = self.session.get(self.default_url, headers=self.headers)
            response.raise_for_status()
        except HTTPError as e:
            raise ValueError(f"HTTP Error:{e.response.status_code} - {e}")
        except ConnectionError:
            raise ValueError(f"Connection Error:Check your internet or the server status.")
        except Timeout:
            raise ValueError(f"Timeout Error:The request took too long.")
        except RequestException as e:
            raise ValueError(f"Error:{e}")
        soup = BeautifulSoup(response.text, "html.parser")
        self.payload["__VIEWSTATE"] = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        self.payload["__VIEWSTATEGENERATOR"] = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
        self.payload["__VIEWSTATEENCRYPTED"] = soup.find("input", {"id": "__VIEWSTATEENCRYPTED"})["value"]
        self.payload["__EVENTVALIDATION"] = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
        select = soup.find("select", {"id": self.tag_ids["status_for"]})
        self.status_for_options = {
            option.text.strip(): option["value"]
            for option in select.find_all("option") if str(option["value"]) != "0"
        }
        self.program_options = {}
    def fetch_programs(self, status_type):
        self.payload[self.tag_ids["status_for"]] = self.status_for_options[status_type]
        try:
            response = self.session.post(self.default_url, headers=self.headers, data=self.payload)
            response.raise_for_status()
        except HTTPError as e:
            raise ValueError(f"HTTP Error:{e.response.status_code} - {e}")
        except ConnectionError:
            raise ValueError(f"Connection Error:Check your internet or the server status.")
        except Timeout:
            raise ValueError(f"Timeout Error:The request took too long.")
        except RequestException as e:
            raise ValueError(f"Error:{e}")
        soup = BeautifulSoup(response.text, "html.parser")
        select = soup.find("select", {"id": self.tag_ids["programme_id"]})
        self.program_options = {
            option.text.strip(): option["value"]
            for option in select.find_all("option") if str(option["value"]) != "0"
        }
    def get_datails_and_marksheet(self, status_type, programme_code, enrolnment_no):
        try:
            response = self.session.get(f'{self.default_url}view_gradecard.aspx?eno={enrolnment_no}&prog={self.program_options[programme_code]}&type={self.status_for_options[status_type]}', headers=self.headers)
            response.raise_for_status()
        except HTTPError as e:
            raise ValueError(f"HTTP Error:{e.response.status_code} - {e}")
        except ConnectionError:
            raise ValueError(f"Connection Error:Check your internet or the server status.")
        except Timeout:
            raise ValueError(f"Timeout Error:The request took too long.")
        except RequestException as e:
            raise ValueError(f"Error:{e}")
        soup = BeautifulSoup(response.text, "html.parser")
        self.student_details["Name"] = soup.find("span", {"id": self.tag_ids["student_name"]}).get_text().title()
        self.student_details["Programme Code"] = soup.find("span", {"id": self.tag_ids["student_program_code"]}).get_text()
        self.student_details["Enrolment No"] = soup.find("span", {"id": self.tag_ids["student_enrolnment_no"]}).get_text()
        if self.student_details["Name"] == "" and self.student_details["Programme Code"] == "" and self.student_details["Enrolment No"] == "":
            self.student_details["Marksheet"] = [[]]
            return False
        table = soup.find("table", {"id": self.tag_ids["student_marksheet"]})
        self.student_details["Marksheet"] = [
            [ceil.get_text(strip=True) for ceil in row.find_all(["th", "td"])]
            for row in table.find_all("tr")
        ]
        self.student_details["Marksheet"].pop()
        return True
    def marksheet_save_in_excel_file(self, file_path):
        excel_file_name = file_path
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
        excel_write.write(2, 1, self.student_details["Name"], user_format)
        excel_write.write(2, 2, self.student_details["Enrolment No"], user_format)
        excel_write.write(2, 3, self.student_details["Programme Code"], user_format)
        excel_write.set_column(1, 3, 16)
        excel_write.set_column(7, 7, 21)
        excel_write.set_column(8, 8, 25)
        excel_write.set_column(9, 9, 16)
        excel_write.set_row(4, 15)
        for i, heading in enumerate(self.student_details["Marksheet"][0]):
            excel_write.write(5, i+1, heading, heading_format)
        excel_write.merge_range(4, 1, 4, len(self.student_details["Marksheet"][0])+0, "Grade Card", merge_format)
        row_design = True
        for i, row in enumerate(self.student_details["Marksheet"][1:]):
            new_design = marks_format_dict
            if row_design:
                if (row[-1] == "COMPLETED"):
                    new_design["bg_color"] = "#99ff99"
                elif (row[-1] == "NOT COMPLETED"):
                    new_design["bg_color"] = "#ff9999"
            else:
                if (row[-1] == "COMPLETED"):
                    new_design["bg_color"] = "#ddffdd"
                elif (row[-1] == "NOT COMPLETED"):
                    new_design["bg_color"] = "#ffdddd"
            row_design = not row_design
            marks_format = excel_file.add_format(new_design)
            for j, data in enumerate(row):
                if (data == "-"):
                    data = ""
                elif (data.isnumeric()):
                    data = int(data)
                excel_write.write(i+6, j+1, data, marks_format)
        excel_file.close()

if __name__ == "__main__":
    obj = IGNOUGradeCard()
    l = list(obj.status_for_options.keys())
    for i in l:
        print(i)