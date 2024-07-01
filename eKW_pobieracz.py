from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from datetime import datetime
import asyncio
#
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#

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
    QApplication, QDialog, QMainWindow, QMessageBox, QStyle
)
from PyQt5.uic import loadUi

from PyQt5.QtGui import QIcon

from eKW_pobieracz_ui import Ui_MainWindow

# #### ##

# eKW pobieracz 0.5
eKWp_ver = "0.5"


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
        self.setting['sign'] = ""
        self.setting['startnum'] = ""
        self.setting['endnum'] = ""

        if os.path.exists(self.config):
            with open(self.config, "r", encoding="utf-8") as file:
                line = file.readline()

                try:
                    self.setting = json.loads(line)
                except:
                    self.setting['kwlist'] = ""
                    self.setting['savepath'] = "C:/"
                    self.setting['startnum'] = ""
                    self.setting['endnum'] = ""

        self.kw_list = self.setting['kwlist']
        self.save_path = self.setting['savepath']

        self.lineSign.setText(self.setting['sign'])
        self.lineFloor.setText(self.setting['startnum'])
        self.lineRoof.setText(self.setting['endnum'])


        self.lineList.setText(self.kw_list)
        self.lineSave.setText(self.save_path)

        self.pdf_bg = self.chBg.isChecked()

        self.sady = []
        if os.path.exists('res/sady.kw'):

            with open('res/sady.kw', 'r') as file:
                lines = file.readlines()
            self.sady = [x.replace("\n","") for x in lines]

        self.rep_dict = {"X": "10", "A": "11", "B": "12", "C": "13", "D": "14", "E": "15",
                        "F": "16", "G": "17", "H": "18", "I": "19", "J": "20", "K": "21",
                        "L": "22", "M": "23", "N": "24", "O": "25", "P": "26", "R": "27",
                        "S": "28", "T": "29", "U": "30", "W": "31", "Y": "32", "Z": "33",
                        "0":"0", "1":"1", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8", "9":"9"}

        ### icons
        self.btnRun.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.btnGen.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btnGenSave.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.btnList.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.btnSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btnLog.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.btnErr.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))

        gen_err(err="Uruchomiono program", log=True)







    def connectSignalsSlots(self):

        self.btnRun.clicked.connect(self.run_by_list)
        self.btnTurbo.clicked.connect(lambda x: asyncio.run(self.run_by_list_turbo()))


        self.btnList.clicked.connect(self.open_file)
        self.btnSave.clicked.connect(self.open_dir)

        self.btnGen.clicked.connect(self.generate_kws)
        self.btnGenSave.clicked.connect(lambda x: self.generate_kws(True))

        self.btnLog.clicked.connect(lambda x: open_local_file('log.txt'))
        self.btnErr.clicked.connect(lambda x: open_local_file('errors.txt'))


        self.action_github.triggered.connect(
            lambda: webbrowser.open_new('https://github.com/Rzezimioszek/eKW-pobieracz'))
        self.action_Wsparcie.triggered.connect(
            lambda: webbrowser.open_new('https://www.paypal.com/donate/?hosted_button_id=2AFDC9PRMGN3Q'))

    def generate_kws(self, download: bool = False):

        sad = self.lineSign.text().strip().upper()
        bot = self.lineFloor.text().strip()
        top = self.lineRoof.text().strip()

        clear_log()

        if sad not in self.sady:
            err = f"Brak oznaczenia sądu [{sad}], sprawdz plik res/sady.kw"
            gen_err(err, True)
            return

        try:
            sad_value = [self.rep_dict[s] for s in sad]
        except:
            err = f"Oznaczenie sądu {sad} nieprawidłowe"
            gen_err(err, True)
            return

        if not bot.isdecimal() or not top.isdecimal():
            err = f"Nieporawny przedział dla wartości dolnej lub górnej"
            gen_err(err, True)
            return

        bot = int(bot)
        top = int(top)

        if top > 99999999:
            err = f"Wartość górna {top} powyżej dozwolonego przedziału zmiana na 99999999"
            gen_err(err)
            top = 99999999

        if bot < 1:
            err = f"Wartość dolna {bot} poniżejj dozwolonego przedziału zmiana na 1"
            gen_err(err)
            bot = 1

        if bot > top:
            err = f"Wartość dolna {bot} większa od górnej {top}"
            gen_err(err)
            return

        if not download:

            gen_err(f"Generowanie listy Kw dla sądu {sad} i przedziału {bot} do {top}")

            filetypes = (("pliki txt", "*.txt"), ("Wszystkie pliki", "*.*"))
            path = filedialog.asksaveasfilename(title="Zapisz plik txt", filetypes=filetypes)
            if path is not None:
                if not path.endswith(".txt"):
                    path = path + ".txt"
        else:
            path = "c:/"
            gen_err(f"Pobieranie KW dla: {sad}/{bot}-{top}/n")

        if path == "":
            err = f"Niepodano scięzki zapisu"
            gen_err(err, True)
            return

        new_kw = []

        for i in range(bot, (top + 1)):

            new_kw.append(self.correct_kw_number(sad, str(i)))

        if download:
            for value in new_kw:
                if "/" not in value:
                    continue

                value = value.replace("\n", "")
                self.save_kw_to_pdf(value)
            gen_err("Pobrano księgi z wygenerowanej listy KW", log=True)
            msg.showinfo("Generator KW", f"Pobrano księgi z wygenerowanej listy KW")

        else:

            with open(path, "w") as file:
                for nk in new_kw:
                    file.write(f"{nk}\n")

            msg.showinfo("Generator KW", f"Wygenerowano listę KW\n{path}")

    def correct_kw_number(self, sad, number):

        sad_value = [self.rep_dict[s] for s in sad]

        wei = [1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7]

        while len(number) < 8:
            number = f"0{number}"

        j_value = [x for x in number]

        temp_kw = sad_value + j_value
        ctlr_dig = 0
        for k in range(len(wei)):
            ctlr_dig = ctlr_dig + (wei[k] * int(temp_kw[k]))

        ctlr_dig = ctlr_dig % 10

        skw = sad + "/" + number + f"/{ctlr_dig}"

        return skw

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

    def get_list(self):

        self.kw_list = self.lineList.text()

        with open(self.kw_list, 'r') as file:
            values = file.readlines()
        # value = 'OP1U/00004102/3'

        distinct = set(values)

        return_value = sorted(distinct)

        return return_value

    async def run_by_list_turbo(self):

        try:
            values = self.get_list()
        except:
            msg.showerror("Zła lista", "Plik wejściowy z listą kw niepoprawny.")
            return

        clear_log()

        task = []
        i = 0
        j = 0
        k = 0

        # n = 5

        n = self.spN.value()

        for value in values:

            if "/" not in value:
                continue

            value = value.replace("\n", "")

            task.append(asyncio.create_task(self.save_kw_to_pdf_turbo(value)))
            j += 1
            i += 1


            if j == n or i == len(values):
                k += 1
                gen_err(f"Pętla: {k}")
                await asyncio.gather(*task)
                task.clear()
                # await asyncio.sleep(9 * j)
                j = 0


        gen_err("Wszystkie księgi wieczyste z zadania zostały pobrane")
        msg.showinfo("Zakończono pobieranie", "Wszystkie księgi wieczyste z zadania zostały pobrane")



    def run_by_list(self):

        try:
            values = self.get_list()
        except:
            msg.showerror("Zła lista", "Plik wejściowy z listą kw niepoprawny.")
            return

        clear_log()
        for value in values:

            if "/" not in value:
                continue

            value = value.replace("\n", "")
            self.save_kw_to_pdf(value)

        gen_err("Wszystkie księgi wieczyste z zadania zostały pobrane")
        msg.showinfo("Zakończono pobieranie", "Wszystkie księgi wieczyste z zadania zostały pobrane")

    async def save_kw_to_pdf_turbo(self, value: str): #

        self.save_path = self.lineSave.text()
        self.pdf_bg = self.chBg.isChecked()

        zupelna = False

        gen_err(f"Wprowadzona wartość: {value}")

        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = self.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"Poprawiono cyfrę kontrolną: {value}")

            options = webdriver.ChromeOptions()
            service = Service()
            browser = webdriver.Chrome(service=service, options=options)

            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

            await asyncio.sleep(3)

            ### insert KW number

            elem = browser.find_element(By.ID, 'kodWydzialuInput')  # Find the search box
            elem.send_keys(kw[0])

            elem = browser.find_element(By.NAME, 'numerKw')  # Find the search box
            elem.send_keys(kw[1])

            elem = browser.find_element(By.NAME, 'cyfraKontrolna')  # Find the search box
            elem.send_keys(kw[2])

            elem = browser.find_element(By.NAME, 'wyszukaj')  # Find the search box
            elem.send_keys(Keys.RETURN)

            await asyncio.sleep(1)

            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
            elem.send_keys(Keys.RETURN)

            ###
        except:
            zupelna = True
            err = f"Treść zwykła wydruku niedostępna dla: {value}"
            gen_err(err)

        try:
            if zupelna:
                if self.chError.isChecked():
                    elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                    elem.send_keys(Keys.RETURN)
                    gen_err("Pobieranie treści zupełnej")
                else:
                    err = f"Błąd pobierania treści zupełnej księgi: {value}"
                    gen_err(err, write=True)
                    return
        except:
            err = f"Błąd pobierania księgi: {value}"
            gen_err(err, write=True)
            return

        try:
            i = 1  # dział I-O

            if self.ch1o.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}o.pdf", "wb") as f:
                    f.write(pdf_data)

            if self.ch1s.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}s.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 2  # dział II

            if self.ch2.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 3  # dział III

            if self.ch3.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 4  # dział IV

            if self.ch4.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            gen_err(f"Pobrano księgę: {value}")
        except:

            err = f"Błąd pobierania wybranych działów księgi: {value}"
            gen_err(err, write=True)

    def save_kw_to_pdf(self, value: str): #

        self.save_path = self.lineSave.text()
        self.pdf_bg = self.chBg.isChecked()

        zupelna = False

        gen_err(f"Wprowadzona wartość: {value}")

        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = self.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"Poprawiono cyfrę kontrolną: {value}")

            options = webdriver.ChromeOptions()
            service = Service()
            browser = webdriver.Chrome(service=service, options=options)

            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

            time.sleep(3) #

            # elem = WebDriverWait(webdriver, 10).until(
            #     EC.presence_of_element_located((By.ID, 'kodWydzialuInput')))

            # time.sleep(3)

            ### insert KW number

            elem = browser.find_element(By.ID, 'kodWydzialuInput')  # Find the search box
            elem.send_keys(kw[0])

            elem = browser.find_element(By.NAME, 'numerKw')  # Find the search box
            elem.send_keys(kw[1])

            elem = browser.find_element(By.NAME, 'cyfraKontrolna')  # Find the search box
            elem.send_keys(kw[2])

            elem = browser.find_element(By.NAME, 'wyszukaj')  # Find the search box
            elem.send_keys(Keys.RETURN)

            time.sleep(1)

            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
            elem.send_keys(Keys.RETURN)

            ###
        except:
            zupelna = True
            err = f"Treść zwykła wydruku niedostępna dla: {value}"
            gen_err(err)

        try:
            if zupelna:
                if self.chError.isChecked():
                    elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                    elem.send_keys(Keys.RETURN)
                    gen_err("Pobieranie treści zupełnej")
                else:
                    err = f"Błąd pobierania treści zupełnej księgi: {value}"
                    gen_err(err, write=True)
                    return
        except:
            err = f"Błąd pobierania księgi: {value}"
            gen_err(err, write=True)
            return

        try:
            i = 1  # dział I-O

            if self.ch1o.isChecked():

                time.sleep(2) #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}o.pdf", "wb") as f:
                    f.write(pdf_data)

            if self.ch1s.isChecked():

                time.sleep(2) #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}s.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 2  # dział II

            if self.ch2.isChecked():

                time.sleep(2) #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 3  # dział III

            if self.ch3.isChecked():

                time.sleep(2) #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            i = 4  # dział IV

            if self.ch4.isChecked():

                time.sleep(2) #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])
                with open(f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf", "wb") as f:
                    f.write(pdf_data)

            # yield  # <-------------------

            gen_err(f"Pobrano księgę: {value}")
        except:

            err = f"Błąd pobierania wybranych działów księgi: {value}"
            gen_err(err, write=True)


def clear_log():

    with open('log.txt', 'w') as file:
        file.write(f"")

def open_local_file(file):
    try:
        os.startfile(file)
    except:
        msg.showerror("Brak pliku", "Plik nieistnieje lub brak uprawnień do dostępu.")

def gen_err(err: str = "Error", rise: bool = False, write = False, log = True):

    ct = datetime.now().strftime('%d.%m.%y %H:%M:%S')
    print(f"[{ct}]\t{err}")

    if write:
        with open("errors.txt", 'a') as file:
            file.write(f"[{ct}]{err}\n")

    if log:
        with open('log.txt', 'a') as file:
            file.write(f"[{ct}]\t{err}\n")

    if rise:
        msg.showerror("Error", err)
def save_settings():
    win.setting['kwlist'] = win.lineList.text()
    win.setting['savepath'] = win.lineSave.text()

    win.setting['sign'] = win.lineSign.text()
    win.setting['startnum'] = win.lineFloor.text()
    win.setting['endnum'] = win.lineRoof.text()

    with open(win.config, "w", encoding="utf-8") as file:
        json.dump(win.setting, file, ensure_ascii=False)

    asyncio.run(sys.exit(app.exec()))


if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(save_settings)
    # app.setWindowIcon(QIcon(":/main/eKw.jpg"))
    win = Window()
    win.show()
    asyncio.run(sys.exit(app.exec()))

