import os
import json
from app import app
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import xlsxwriter

def create_driver():
    if os.environ.get("CHROMEDRIVER_PATH"):
            #Chrome driver options
        chrome_options = webdriver.ChromeOptions()
        # Environment variable set in Heroku
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # Use headless so it saves memory and runtime by not launching a UI view of the browser
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    else:
        s=Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s)
    driver.implicitly_wait(10)
    return driver

def get_tokens():
    filename = os.path.join(app.static_folder, 'tokens.json')
    with open(filename) as json_file:
        return json.load(json_file)

def google_sheets_upload(dataframe, sheet_name, sheet_range=None):
    filename = os.path.join(app.static_folder, 'google_creds.json')
    with open(filename) as json_file:
        creds = json.load(json_file)
    creds["project_id"] = os.environ.get("PROJECT_ID")
    creds["private_key_id"] = os.environ.get("PRIVATE_KEY_ID")
    creds["private_key"] = os.environ.get("PRIVATE_KEY").replace("\\n", "\n")
    creds["client_email"] = os.environ.get("CLIENT_EMAIL")
    creds["client_id"] = os.environ.get("CLIENT_ID")
    creds["client_x509_cert_url"] = os.environ.get("CERT_URL")

    try:
        gc = gspread.service_account_from_dict(creds)
        sht1 = gc.open_by_key(os.environ.get("SPREADSHEET_KEY"))
        worksheet = sht1.worksheet(sheet_name)
        row, col = xlsxwriter.utility.xl_cell_to_rowcol(sheet_range)
        if sheet_range is not None:
            set_with_dataframe(worksheet, dataframe, row=row, col=col)
            # worksheet.update(sheet_range, [dataframe.columns.values.tolist()] + dataframe.values.tolist())
        else:
            # worksheet.update([dataframe.index.name] + dataframe.index.values.tolist())
            set_with_dataframe(worksheet, dataframe)
    except Exception as e:
        raise Exception(f"Error at sheets data upload: {e}")
