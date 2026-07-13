from html.parser import HTMLParser
import pandas as pd

class MyHTMLParser(HTMLParser):
    def __init__(self, log_callback):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.row_count = 0
        self.col_index = 0
        self.columns = ["web_id", "date_requested", "requestor", "form", "description"]
        self.current_col = ""
        self.current_row_data = {}
        self.all_extracted_data = []
        self.log = log_callback

    def extract_notes_id_from_url(self, url):
        return url.split('/')[5]
    
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        get_tag = tag.upper()
        
        if (get_tag == "TABLE"):
            self.in_table = True

        elif (get_tag == "TR" and self.in_table == True):
            self.in_row = True
            self.row_count += 1
            
            self.log("1", f"Row {self.row_count}: processing begin")
            self.current_row_data = {}
            self.col_index = 0
            
        elif (get_tag == "TD" and self.in_row == True):
            if (self.row_count <= 1):
                self.log("0", "====Skipping Header====")
                return
            
            self.in_cell = True
            if (self.col_index == 0):
                return

            self.current_col = self.columns[self.col_index - 1]
                
        elif  (get_tag == "A" and self.in_cell == True and self.col_index == 1):
            if ("href" in attr_dict):
                if (attr_dict["href"] is None):
                    self.log("2", f"Row {self.row_count}: No URL found in web column")
                else:
                    extracted_id = self.extract_notes_id_from_url(attr_dict["href"])
                    self.current_row_data[self.current_col ] = extracted_id
            else:
                self.log("2", f"Row {self.row_count}: No HREF attribute")
        else:
            return

    def handle_data(self, data):
        if (self.in_cell == True and self.row_count > 1 and self.col_index > 0):
            clean_data = data.strip()
            if (clean_data and clean_data != "Notes" and clean_data != "Web"):
                self.current_row_data[self.current_col] = clean_data
        self.col_index += 1

    def handle_endtag(self, tag):
        get_tag = tag.upper()
        
        if (get_tag == "TABLE"):
            self.in_table = False

        elif (get_tag == "TR" and self.in_table):
            if (self.in_row and self.row_count > 1):
                self.all_extracted_data.append(self.current_row_data)
            self.in_row = False

        elif (get_tag == "TD" and self.in_cell == True):
            self.in_cell = False

def pandas_dt_frame(data):
    df = pd.DataFrame(data)
    df.to_excel('output.xlsx', index=False)
            
def process_input_call(data, log_callback):
    parser = MyHTMLParser(log_callback)
    parser.feed(data)
    pandas_dt_frame(parser.all_extracted_data)
