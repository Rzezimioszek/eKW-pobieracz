import json
import pandas as pd
import os
import base64
from selenium.webdriver.common.by import By

import extract_html as eh

def save_json(info, path_without_ext):

    with open(f"{path_without_ext}.json", "w", encoding="utf-8") as file:
        json.dump(info, file, ensure_ascii=False, indent=1)

def save_csv(info, path_without_ext):

    path_without_ext = f"{path_without_ext}_raport.csv"
    df = pd.DataFrame(info)
    head = True if not os.path.exists(path_without_ext) else False
    df.to_csv(path_without_ext, mode='a', index=False, header=head, sep=';', encoding="utf-8-sig")

def save_pdf(browser, path_without_ext, bg=True):

    pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": bg, })
    # pdf = browser.print_page(background=win.pdf_bg)
    pdf_data = base64.b64decode(pdf["data"])

    pdf_path = f"{path_without_ext}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_data)

def save_txt(browser, path_without_ext):

   with open(f"{path_without_ext}.txt", "w", encoding='utf-8') as f:
       f.write(browser.find_element(By.XPATH, "//body").text)

def save_html(browser, path_without_ext, sj, sh, sx):

    path = f"{path_without_ext}.html"

    with open(path, "w", encoding='utf-8') as f:
        f.write(browser.page_source)

    if '1o.html' in path and sj:
        eh.page_to_json(path, os.path.dirname(path), sx)

    # print(path, win.chHTML.isChecked(), win.chXlsx.isChecked())

    if not sh:
        print('-delete')
        os.remove(path)


if __name__ == "__main__":
    ...