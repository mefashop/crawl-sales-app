from flask import Flask
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
import time
from datetime import datetime

app = Flask(__name__)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os
import json

key_json = os.environ.get("SERVICE_ACCOUNT_JSON")
creds_dict = json.loads(key_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1ZaouruB_Utz--TpXtLFv91RAfxxDbFjfoC1r8DoFxmI").worksheet("Shop")

@app.route("/")
def crawl_sales():
    try:
        start_row = 2
        urls = sheet.col_values(1)[start_row - 1:]
        results = []

        for i, url in enumerate(urls):
            if not url.strip():
                results.append([""])
                continue

            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                target = soup.find("div", class_="wt-mt-lg-5 wt-pt-lg-2 wt-bt-xs-1")
                if target:
                    text = target.text.strip().replace("sales", "").strip()
                    results.append([text])
                else:
                    results.append([""])
            except Exception as e:
                print(f"Lỗi ở dòng {start_row + i}: {e}")
                results.append(["ERROR"])

            time.sleep(1)

        sheet.update(f"B{start_row}:B{start_row + len(results) - 1}", results)
        sheet.update_acell("C1", f"Cập nhật lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "Đã cập nhật!"
    except Exception as e:
        return f"Lỗi toàn cục: {e}"

if __name__ == "__main__":
    app.run(debug=True)
