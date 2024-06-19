from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.service import Service
import base64

import time
import sys
import os
import json

from tkinter import filedialog
from tkinter import messagebox as msg

import webbrowser


# #### ## Kod dla UI

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)
from PyQt5.uic import loadUi

from eKW_pobieracz_ui import Ui_MainWindow

# #### ##

# eKW pobieracz 0.1
eKWp_ver = "0.1"


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        # self.kw_count = 0

        self.config = 'eKW.json'
        self.setting = dict()

        self.setting['kwlist'] = ""
        self.setting['savepath'] = "C:/"

        if os.path.exists(self.config):
            with open(self.config, "r", encoding="utf-8") as file:
                line = file.readline()

                try:
                    self.setting = json.loads(line)
                except:
                    self.setting['kwlist'] = ""
                    self.setting['savepath'] = "C:/"

        self.kw_list = self.setting['kwlist']
        self.save_path = self.setting['savepath']

        self.lineList.setText(self.kw_list)
        self.lineSave.setText(self.save_path)

        self.pdf_bg = self.chBg.isChecked()





    def connectSignalsSlots(self):
        self.btnRun.clicked.connect(self.run_by_list)
        self.btnList.clicked.connect(self.open_file)
        self.btnSave.clicked.connect(self.open_dir)
        self.action_github.triggered.connect(
            lambda: webbrowser.open_new('https://github.com/Rzezimioszek/eKW-pobieracz'))
        self.action_Wsparcie.triggered.connect(
            lambda: webbrowser.open_new('https://www.paypal.com/donate/?hosted_button_id=2AFDC9PRMGN3Q'))


    def test_print(self):
        print("Aqq")





    def open_file(self):

        filetypes_option = (("pliki txt", "*.txt"), ("pliki kw", "*.kw"), ("Wszystkie pliki", "*.*"))
        path = filedialog.askopenfilenames(title="Wybierz plik lub pliki", filetypes=filetypes_option)
        if path is not None:
            path = str(path).replace("('", "")
            path = path.replace("',)", "\t")
            path = path.replace("')", "\t")
            path = path.replace("', '", "\t")
            path = path.strip()


            self.kw_list = path
            self.lineList.setText(path)
            # self.kw_count = len(self.get_list())

    def open_dir(self):
        path = filedialog.askdirectory(title="Wybierz folder")

        if path is not None:
            self.save_path = path
            self.lineSave.setText(path)




    def get_list(self) -> set:

        self.kw_list = self.lineList.text()

        with open(self.kw_list, 'r') as file:
            values = file.readlines()
        # value = 'OP1U/00004102/3'

        distinct = set(values)

        return distinct
        # run_by_list(distinct)


    def run_by_list(self):
        
        try:
            values = self.get_list()
        except:
            msg.showerror("Zła lista", "Plik wejściowy z listą kw niepoprawny.")
            return

        tasks = []

        bigtic = time.perf_counter()
        for value in values:

            if "/" not in value:
                continue

            tic = time.perf_counter()

            value = value.replace("\n", "")
            self.save_kw_to_pdf(value)

            # tasks.append(save_kw_to_pdf(value))  # <----------
            toc = time.perf_counter()

            print(f"Czas: {toc - tic:0.4f} s\n")

        bigtoc = time.perf_counter()

        passed_time = bigtoc - bigtic

        op_time = f"{passed_time:0.2f}s"

        if passed_time > 3600:
            passed_time = passed_time/3600
            op_time = f"{passed_time:0.2f}h"
        if passed_time > 60:
            passed_time = passed_time / 60
            op_time = f"{passed_time:0.2f}min"


        msg.showinfo("Zakończono pobieranie", f"Księgi wieczyste zostały pobrane\nOpracja zajeła: {op_time}")

        """# Run the tasks
            done = False
            while not done:
                for t in tasks:
                    try:
                        next(t)
                    except StopIteration:
                        tasks.remove(t)
                    if len(tasks) == 0:
                        done = True"""




    def save_kw_to_pdf(self, value: str):

        self.save_path = self.lineSave.text()
        self.pdf_bg = self.chBg.isChecked()
        try:
            kw = value.split('/')

            options = webdriver.ChromeOptions()
            service = Service()

            browser = webdriver.Chrome(service=service, options=options)

            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')
            # assert 'OP1U'

            # time.sleep(5)
            time.sleep(3)

            ### insert KW number

            elem = browser.find_element(By.ID, 'kodWydzialuInput')  # Find the search box
            elem.send_keys(kw[0])

            elem = browser.find_element(By.NAME, 'numerKw')  # Find the search box
            elem.send_keys(kw[1])

            elem = browser.find_element(By.NAME, 'cyfraKontrolna')  # Find the search box
            elem.send_keys(kw[2])

            elem = browser.find_element(By.NAME, 'wyszukaj')  # Find the search box
            elem.send_keys(Keys.RETURN)

            # time.sleep(1)

            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
            elem.send_keys(Keys.RETURN)

            ###
        except:
            if self.chError.isChecked():
                elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                elem.send_keys(Keys.RETURN)
            else:
                with open("errors.txt", 'a') as file:
                    er = f"Error on KW: {value}"
                    print(er)
                    file.write(f"{er}\n")
                return

        try:
            i = 1  # dział I-O

            if self.ch1o.isChecked():

                time.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}o.pdf", "wb") as f:
                    f.write(pdf_data)

            if self.ch1s.isChecked():

                time.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}s.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 2  # dział II

            if self.ch2.isChecked():

                time.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 3  # dział III

            if self.ch3.isChecked():

                time.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 4  # dział IV

            if self.ch4.isChecked():

                time.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            # yield  # <-------------------

            print(f"{value} --saved successfull")
        except:

            with open("errors.txt", 'a') as file:
                er = f"Error on KW: {value}"
                print(er)
                file.write(f"{er}\n")

def save_settings():
    win.setting['kwlist'] = win.lineList.text()
    win.setting['savepath'] = win.lineSave.text()

    with open(win.config, "w", encoding="utf-8") as file:
        json.dump(win.setting, file, ensure_ascii=False)

    sys.exit(app.exec())


if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(save_settings)
    win = Window()
    win.show()
    sys.exit(app.exec())

