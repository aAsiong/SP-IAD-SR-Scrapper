from html.parser import HTMLParser
import pandas as pd
import re
import time
from datetime import datetime as dt

class MyHTMLParser(HTMLParser):
    def __init__(self, log_queue):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.log_queue = log_queue

        # Row variables
        self.row_count = 0
        self.current_row_data = {}
        self.all_extracted_data = []

        # Column variables
        self.col_index = 0
        self.current_col = ""
        self.columns = ["notes_id", "web_id", "date_requested", "requestor", "form", "description"]

    def extract_notes_id_from_url(self, url, stt):
        if (stt == 1):
            # For 1st column
            return url.split('/')[4] + '/' + url.split('/')[5]
        elif (stt == 2):
            # For 2nd column
            return url.split('/')[5]
    
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        
        get_tag = tag.upper()
        
        if (get_tag == "TABLE"):
            self.in_table = True

        if (get_tag == "TR" and self.in_table):
            self.row_count += 1

            # If self.row_count == 1 then its the Header, skip it
            if (self.row_count == 1):
                return
                    
            self.in_row = True
                
            self.col_index = 0
            self.current_col = ""
            self.current_row_data = {}

            if (self.row_count > 1):
                self.log_queue.put(
                    ("INFO",
                    f"Processing Row {self.row_count - 1}",
                    "")
                )

        if (get_tag == "TD" and self.in_row):
            # self.in_cell will only be True during <td> process
            # It will be set to False come the handle_endtag()
            # This validation will only run if there are nested <td>
            if (self.in_cell == True):
                self.in_row = False
                
                self.log_queue.put(
                    ("ERROR",
                     f"Row {self.row_count} - Invalid <td> structure detected",
                    "")
                )
                return
            
            self.col_index += 1

            # Check if <tr>'s <td> exceeds 6
            if (self.col_index > 6):
                return
            
            self.in_cell = True
            # Get key from hard-coded array of header
            self.current_col = self.columns[self.col_index - 1]

            time.sleep(0.02)

        
        # Processing of A will only work for 1st and 2nd column
        if (get_tag == "A" and self.in_cell == True and self.col_index <= 2):
            if ("href" in attr_dict and attr_dict["href"] is None):
                # 1st and 2nd column is important in identifying a record into the db
                # If something is wrong, skip the entire row
                self.in_row = False

                self.log_queue.put(
                    ("ERROR",
                     f"Row {self.row_count} - Skipped due to missing key values",
                    "")
                )
                return
            else:
                extracted_id = self.extract_notes_id_from_url(attr_dict["href"], self.col_index)
                self.current_row_data[self.current_col] = extracted_id
                self.log_queue.put(
                    ("SUCCESS",
                    f"Row {self.row_count - 1}'s {self.current_col} successfully parsed",
                    "")
                )
                return

    def handle_data(self, data):
        if (self.in_cell == True and self.in_row == True):
            # Only run this for 3rd to 6th columns
            if (self.col_index > 2 and self.col_index < 7):
                clean_data = data.strip()
                if (clean_data):
                    self.current_row_data[self.current_col] = clean_data
                    self.log_queue.put(
                        ("SUCCESS",
                        f"Row {self.row_count - 1}'s {self.current_col} successfully parsed",
                        "")
                    )
                else:
                    # 3rd to 6th columns can be null
                    # But must inform user via log_queue()
                    self.current_row_data[self.current_col] = ""
                    self.log_queue.put(
                        ("INFO",
                        f"Row {self.row_count - 1}'s {self.current_col} has no value",
                        "")
                    )
            else:
                return
        else:
            return

    def handle_endtag(self, tag):
        get_tag = tag.upper()
        
        if (get_tag == "TABLE"):
            self.in_table = False

        elif (get_tag == "TR" and self.in_table):
            # Since setting self.in_row is used as a breaker or sort
            # Only run this if self.in_row is still True, meaning there
            # was no error encountered during <td> processing
            if (self.in_row and self.col_index == 6):
                self.all_extracted_data.append(self.current_row_data)

                self.log_queue.put(
                    ("ROW_DONE",
                    f"Row {self.row_count - 1} - DONE PROCESSING",
                    len(self.all_extracted_data))
                )
                
                # Properly close in_row
                self.in_row = False
            else:
                return

        elif (get_tag == "TD" and self.in_cell):
            self.in_cell = False

def pandas_dt_frame(data):
    return pd.DataFrame(data)

def pandas_to_excel(df, check_file_folder):
    # Construct Filename
    get_dt = dt.now() 
    filename = str(get_dt.strftime("%Y%m%d%H%M%S")) + "-sr-report.xlsx"

    # Create proper header for replacement
    actual_col_headers = {
        "notes_id" : "NOTES ID",
        "web_id" : "WEB ID",
        "date_requested" : "DATE REQUESTED",
        "requestor" : "REQUESTOR",
        "form" : "FORM",
        "description" : "DESCRIPTION"
    }

    dl_exist, get_path = check_file_folder("")
    format_path = check_file_folder(filename)

    if (dl_exist):
        with pd.ExcelWriter(format_path, engine="xlsxwriter") as writer:
            df.to_excel(
                writer,
                sheet_name="Report",
                startcol=1,
                startrow=2,
                header=False,
                index=False
            )

            workbook = writer.book
            worksheet = writer.sheets["Report"]

            header = workbook.add_format({
                "bold" : True,
                "font_color" : "white",
                "bg_color" : "#0F3D5E",
                "border" : 2,
                "align" : "center",
                "valign" : "vcenter"
            })
            
            body = workbook.add_format({
                "border" : 2,
                "text_wrap" : True,
                "valign" : "top"
            })

            try:
                for col, value in enumerate(df.columns):
                    worksheet.write(1, col + 1, actual_col_headers.get(value, value), header)
                
                # Temporary Disable
                """
                for r in range(len(df)):
                    for c in range(len(df.columns)):
                        worksheet.write(r + 2, c + 1, df.iloc[r, c], body)
                """
            except Exception (e):
                print(f"{str(e)}")

            worksheet.set_row(0, 0.5)
            worksheet.set_default_row(60)

            worksheet.set_column("A:A", 0.5)
            worksheet.set_column("B:B", 80, body)
            worksheet.set_column("C:C", 35, body)
            worksheet.set_column("D:D", 18, body)
            worksheet.set_column("E:E", 18, body)
            worksheet.set_column("F:F", 35, body)
            worksheet.set_column("G:G", 60, body)
            
def process_input_call(data, log_queue, check_file_folder):
    # Check <table> count. Make sure only one
    table_count = len(re.findall(r"<table\b", data, re.IGNORECASE))
    if (table_count != 1):
        log_queue.put(
            ("ERROR",
            f"Invalid Input Structure",
            "")
        )
        return
    
    # Compute total rows inside user input
    total_rows = len(re.findall(r"<tr\b", data, re.IGNORECASE)) - 1
    log_queue.put(
        ("SET_MAX",
         f"Detected records: {total_rows}",
         total_rows)
    )

    parser = MyHTMLParser(log_queue)
    parser.feed(data)
    log_queue.put(
       ("INFO",
        "Starting Excel Conversion",
        "")
    )
    try:
        df = pandas_dt_frame(parser.all_extracted_data)
        pandas_to_excel(df, check_file_folder)
        log_queue.put(
            ("FULL_DONE",
            "Excel Exported in root folder",
            "")
        )
    except Exception as e:
        log_queue.put(
            ("ERROR",
            f"Encountered {str(e)}",
            "")
        )
