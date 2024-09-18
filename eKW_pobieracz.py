from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException, WebDriverException, NoSuchElementException
)
from urllib3.exceptions import MaxRetryError, NewConnectionError
import time

from eKW_functions import *
from eKW_save import *
from eKW_dialogs import *

import asyncio
from pathlib import Path
import time
import sys
import os
import json
import extract_html as eh

from tkinter import filedialog
from tkinter import messagebox as msg

import webbrowser
import pypdf as pypdf
import logging

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStyle
)

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtMultimedia import QSound

# from PyQt5.uic import loadUi
# from PyQt5.QtGui import QIcon

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons
#CE_0001-D.pdf

from eKW_pobieracz_ui import Ui_MainWindow

eKWp_ver = "1.2.01"

logging.basicConfig(format="%(message)s", level=logging.INFO)

theme = get_theme()


class GenerateStandard(QThread):
    progress = pyqtSignal(int)
    stat = pyqtSignal(str)
    def __init__(self, download):
        super().__init__()
        self.is_paused = False
        self.is_killed = False
        self.save_path = ""
        self.download = download
        self.pdf_bg = ""

    # @pyqtSlot()
    def run(self):
        self.is_killed = False
        self.is_paused = False

        sad = win.lineSign.text().strip().upper()
        bot = win.lineFloor.text().strip()
        top = win.lineRoof.text().strip()

        clear_log()

        if sad not in win.sady:
            err = f"Brak oznaczenia sądu [{sad}], sprawdz plik res/sady.kw"
            gen_err(err, True)
            return

        try:
            sad_value = [win.rep_dict[s] for s in sad]
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
            #gen_err(err)
            bot = 1

        if bot > top:
            err = f"Wartość dolna {bot} większa od górnej {top}"
            gen_err(err)
            return

        if not self.download:

            gen_err(f"Generowanie listy Kw dla sądu {sad} i przedziału {bot} do {top}")

            filetypes = (("pliki txt", "*.txt"), ("Wszystkie pliki", "*.*"))
            path = filedialog.asksaveasfilename(title="Zapisz plik txt", filetypes=filetypes)
            if path is not None:
                if not path.endswith(".txt"):
                    path = path + ".txt"

            with open(path, "w") as file:
                file.write(f"")
        else:
            path = "c:/"
            gen_err(f"Pobieranie KW dla: {sad}/{bot}-{top}/n")

        if path == "":
            err = f"Niepodano scięzki zapisu"
            gen_err(err, True)
            return

        proc = 0
        end = top

        self.progress.emit(proc)


        for i in range(bot, (top + 1)):

            try:

                nk = win.correct_kw_number(sad, str(i))

                if self.download:
                    # save_kw_to_pdf(nk) #without self

                    if win.chParams.isChecked():
                        if win.lineControl.text().isdecimal() and win.lineLast.text().isdecimal():
                            if nk[-1] == win.lineControl.text() and nk[-3] == win.lineLast.text():
                                save_kw_to_pdf(nk)
                        elif win.lineControl.text().isdecimal() and not win.lineLast.text().isdecimal():
                            if nk[-1] == win.lineControl.text():
                                save_kw_to_pdf(nk)
                        elif not win.lineControl.text().isdecimal() and win.lineLast.text().isdecimal():
                            if nk[-3] == win.lineLast.text():
                                save_kw_to_pdf(nk)
                    else:
                        save_kw_to_pdf(nk)
                else:
                    if win.chParams.isChecked():
                        if win.lineControl.text().isdecimal() and win.lineLast.text().isdecimal():
                            if nk[-1] != win.lineControl.text() or nk[-3] != win.lineLast.text():
                                continue
                        elif win.lineControl.text().isdecimal() and not win.lineLast.text().isdecimal():
                            if nk[-1] != win.lineControl.text():
                                continue
                        elif not win.lineControl.text().isdecimal() and win.lineLast.text().isdecimal():
                            if nk[-3] != win.lineLast.text():
                                continue
                    with open(path, "a") as file:
                        file.write(f"{nk}\n")


                proc = int(((i - bot)/(end - bot)) * 100)
                # logging.info(f"{proc}%\t{i}\t{end}")
                proc = 1 if proc <= 0 else proc
                proc = 100 if proc >= 100 else proc
                # win.progressBar.setValue(proc)
                self.progress.emit(proc)

            except:
                gen_err(f"Bład generownaia w pozycji {i}", log=True, write=True)
                return


            while self.is_paused:
                self.stat.emit("Pauza")
                time.sleep(1)
                self.stat.emit('')

            if self.is_killed:
                gen_err(f"Wygenerowano {proc}% z zadanego zakresu", log=True)
                self.is_killed = False
                self.is_paused = False
                break

        if self.download:
            mess = f"Zakończono pobieranie: {sad} {bot}-{top}"
            msg.showinfo("Generator", "Zakończono pobieranie z zadanego zakresu")
            self.stat.emit(mess)
        else:
            mess = f"Zakończono generowanie: {sad} {bot}-{top}"
            msg.showinfo("Generator", "Zakończono generowanie z zadanego zakresu")
            self.stat.emit(mess)
        # self.quit()
        # quit()

        # return

    def kill(self):
        self.is_killed = True
        self.is_paused = False
        self.stat.emit("Kończenie działania przez użytkownika")

    def pause(self):
        if self.is_paused:
            self.is_paused = False
            self.stat.emit("Wznowiono")
        else:
            self.is_paused = True
            self.stat.emit("Wstrzymywanie działania")


class GenerateTurbo(QThread):
    progress = pyqtSignal(int)
    stat = pyqtSignal(str)
    def __init__(self, download):
        super().__init__()
        self.is_paused = False
        self.is_killed = False
        self.save_path = ""
        self.download = download
        self.pdf_bg = ""

    # @pyqtSlot()
    def run(self):
        self.is_killed = False
        self.is_paused = False

        asyncio.run(self.generator())

        msg.showinfo("Generator", "Zakończono pobieranie z zadanego zakresu")

    async def generator(self):

        self.progress.emit(0)
        mess = "Start turbogeneratora numerów KW"
        self.stat.emit(mess)


        sad = win.lineSign.text().strip().upper()
        bot = win.lineFloor.text().strip()
        top = win.lineRoof.text().strip()

        clear_log()

        if sad not in win.sady:
            err = f"Brak oznaczenia sądu [{sad}], sprawdz plik res/sady.kw"
            self.stat.emit(err)
            gen_err(err, True)
            return

        try:
            sad_value = [win.rep_dict[s] for s in sad]
        except:
            err = f"Oznaczenie sądu {sad} nieprawidłowe"
            self.stat.emit(err)
            gen_err(err, True)
            return

        if not bot.isdecimal() or not top.isdecimal():
            err = f"Nieporawny przedział dla wartości dolnej lub górnej"
            self.stat.emit(err)
            gen_err(err, True)
            return

        bot = int(bot)
        top = int(top)

        if top > 99999999:
            err = f"Wartość górna {top} powyżej dozwolonego przedziału zmiana na 99999999"
            self.stat.emit(err)
            gen_err(err)
            top = 99999999

        if bot < 1:
            err = f"Wartość dolna {bot} poniżej dozwolonego przedziału zmiana na 1"
            self.stat.emit(err)
            gen_err(err)
            bot = 1

        if bot > top:
            err = f"Wartość dolna {bot} większa od górnej {top}"
            self.stat.emit(err)
            gen_err(err)
            return

        if not self.download:
            err = f"Generowanie listy KW: {sad} {bot}-{top}"
            gen_err(err)
            self.stat.emit(err)

            filetypes = (("pliki txt", "*.txt"), ("Wszystkie pliki", "*.*"))
            path = filedialog.asksaveasfilename(title="Zapisz plik txt", filetypes=filetypes)
            if path is not None:
                if not path.endswith(".txt"):
                    path = path + ".txt"

            with open(path, "w") as file:
                file.write(f"")
        else:
            path = "c:/"
            err = f"Pobieranie KW dla: {sad} {bot}-{top}"
            gen_err(err)
            self.stat.emit(err)

        if path == "":
            err = f"Niepodano scięzki zapisu"
            self.stat.emit(err)
            gen_err(err, True)
            return

        proc = 0
        end = top

        j = 0
        k = 0

        self.progress.emit(proc)
        n = win.spN.value()

        task = []

        for i in range(bot, (top + 1)):

            try:

                nk = win.correct_kw_number(sad, str(i))

                if win.chParams.isChecked():
                    if win.lineControl.text().isdecimal() and win.lineLast.text().isdecimal():
                        if nk[-1] == win.lineControl.text() and nk[-3] == win.lineLast.text():
                            task.append(asyncio.create_task(save_kw_to_pdf_turbo(nk)))
                            j += 1
                    elif win.lineControl.text().isdecimal() and not win.lineLast.text().isdecimal():
                        if nk[-1] == win.lineControl.text():
                            task.append(asyncio.create_task(save_kw_to_pdf_turbo(nk)))
                            j += 1
                    elif not win.lineControl.text().isdecimal() and win.lineLast.text().isdecimal():
                        if nk[-3] == win.lineLast.text():
                            task.append(asyncio.create_task(save_kw_to_pdf_turbo(nk)))
                            j += 1

                else:
                    task.append(asyncio.create_task(save_kw_to_pdf_turbo(nk)))
                    j += 1

                if j == n or i == top:
                    k += 1
                    err = f"Pętla: {k} Liczba tasków: {j}"
                    gen_err(f"Pętla: {k} Liczba tasków: {j}")
                    self.stat.emit(err)
                    await asyncio.gather(*task)
                    task.clear()

                    proc = int(((i - bot)/(end - bot)) * 100)
                    proc = 1 if proc <= 0 else proc
                    proc = 100 if proc >= 100 else proc

                    self.progress.emit(proc)


                    while self.is_paused:
                        self.stat.emit("Pauza")
                        time.sleep(1)
                        self.stat.emit('')

                    if self.is_killed:
                        self.is_paused = False
                        break

                    # await asyncio.sleep(9 * j)
                    j = 0

            except:
                err = f"Bład generownaia w pozycji {i}"
                gen_err(err, log=True, write=True)
                self.stat.emit(err)
                return


            while self.is_paused:
                self.stat.emit("Pauza")
                time.sleep(1)
                self.stat.emit('')

            if self.is_killed:
                #gen_err(f"Wygenerowano {proc}% z zadanego zakresu", log=True)
                self.is_killed = False
                self.is_paused = False
                break

    def kill(self):
        self.is_killed = True
        self.is_paused = False
        self.stat.emit("Kończenie działania przez użytkownika")

    def pause(self):
        if self.is_paused:
            self.is_paused = False
            self.stat.emit("Wznowiono")
        else:
            self.is_paused = True
            self.stat.emit("Wstrzymywanie działania")


class ListStandard(QThread):
    progress = pyqtSignal(int)
    stat = pyqtSignal(str)
    def __init__(self, values):
        super().__init__()
        self.is_paused = False
        self.is_killed = False
        self.values = values
        self.save_path = ""
        self.pdf_bg = ""

    # @pyqtSlot()
    def run(self):
        self.is_killed = False
        self.is_paused = False

        mess = "Start pobieranie standardowe"
        self.stat.emit(mess)

        try:
            values = self.values
        except:
            err = "Plik wejściowy z listą kw niepoprawny."
            self.stat.emit(err)
            msg.showerror("Zła lista", err)
            return

        clear_log()
        i = 0
        end = len(values)

        proc = 0

        self.progress.emit(proc)

        for value in values:

            if "/" not in value:
                continue

            value = value.replace("\n", "")
            save_kw_to_pdf(value) # without self

            i += 1

            proc = int((i/end) * 100)
            proc = 1 if proc <= 0 else proc
            proc = 100 if proc >= 100 else proc
            self.progress.emit(proc)

            while self.is_paused:
                self.stat.emit('Pauza')
                time.sleep(1)
                self.stat.emit('')
                time.sleep(1)

            if self.is_killed:
                self.is_paused = False
                self.stat.emit('Zakończono')
                break

        if self.is_killed:
            err = f"Zakończono pobieranie na: {proc}%"
            gen_err(err)
            # win.progressBar.setValue(0)
            self.stat.emit(err)
            self.progress.emit(proc)
            msg.showinfo("Zakończono pobieranie", f"Pobrano {proc}% wybranych ksiąg")
        else:
            err = "Wszystkie księgi wieczyste z zadania zostały pobrane"
            gen_err(err)
            self.stat.emit(err)
            msg.showinfo("Zakończono pobieranie", "Wszystkie księgi wieczyste z zadania zostały pobrane")

        msg.showinfo("Generator", "Zakończono pobieranie z listy")

    def kill(self):
        self.is_killed = True
        self.is_paused = False
        self.stat.emit("Kończenie działania przez użytkownika")

    def pause(self):
        if self.is_paused:
            self.is_paused = False
            self.stat.emit("Wznowiono")
        else:
            self.is_paused = True
            self.stat.emit("Wstrzymywanie działania")


class ListTurbo(QThread):
    progress = pyqtSignal(int)
    stat = pyqtSignal(str)
    def __init__(self, values, generate=False):
        super().__init__()
        self.is_paused = False
        self.is_killed = False
        self.generate = generate
        self.values = values
        self.save_path = ""
        self.pdf_bg = ""

    # @pyqtSlot()
    def run(self):
        self.is_killed = False
        self.is_paused = False

        if self.generate:

            asyncio.run(self.generator())
            msg.showinfo("Generator", "Zakończono pobieranie z zadanego zakresu")

        else:

            asyncio.run(self.run_by_list_turbo())
            msg.showinfo("Generator", "Zakończono pobieranie z listy")
    async def run_by_list_turbo(self, values=[]):

        self.progress.emit(0)

        mess = "Start turbopobieranie"
        self.stat.emit(mess)

        try:
            if len(values) < 1:
                values = win.get_list()
        except:
            err = "Plik wejściowy z listą kw niepoprawny."
            msg.showerror("Zła lista", err)
            self.stat.emit(err)
            return

        clear_log()

        task = []
        i = 0
        j = 0
        k = 0

        # n = 5

        n = win.spN.value()
        end = len(values)

        for value in values:

            if "/" not in value:
                continue

            value = value.replace("\n", "")

            # task.append(asyncio.create_task(self.save_kw_to_pdf_turbo(value)))
            task.append(asyncio.create_task(save_kw_to_pdf_turbo(value)))
            j += 1
            i += 1

            if j == n or i == len(values):
                k += 1
                err = f"Pętla: {k} Liczba tasków: {j}"
                gen_err(err)
                self.stat.emit(err)
                await asyncio.gather(*task)
                task.clear()

                proc = int((i/end)*100)
                proc = 1 if proc <= 0 else proc
                proc = 100 if proc >= 100 else proc

                self.progress.emit(proc)

                if self.is_killed:
                    break
                while self.is_paused:
                    time.sleep(1)
                # await asyncio.sleep(9 * j)
                j = 0
        err = "Wszystkie księgi wieczyste z zadania zostały pobrane"
        gen_err(err)
        self.stat.emit(err)
        msg.showinfo("Zakończono pobieranie", err)

    def kill(self):
        self.is_killed = True
        self.stat.emit("Zakończono działanie przez użytkownika")

    def pause(self):
        if self.is_paused:
            self.is_paused = False
            self.stat.emit("Wznowiono")
        else:
            self.is_paused = True
            self.stat.emit("WWstrzymywanie działania")

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

        self.load_config()



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

        """self.btnRun.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.btnGenSave.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))"""

        self.btnGen.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btnList.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.btnSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btnLog.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.btnErr.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))


        gen_err(err="Uruchomiono program", log=True)

        self.runner = ListStandard([])
    def connectSignalsSlots(self):

        self.btnRun.clicked.connect(lambda: self.start_runer('ds'))
        self.btnTurbo.clicked.connect(lambda: self.start_runer('dt'))

        self.btnList.clicked.connect(lambda: self.lineList.setText(open_file()))
        self.btnOpenDzList.clicked.connect(lambda: self.lineDzList.setText(open_file()))
        self.btnSave.clicked.connect(lambda: self.lineSave.setText(open_dir()))

        self.btnGen.clicked.connect(lambda: self.start_runer('gs'))
        self.btnGenSave.clicked.connect(lambda: self.start_runer('gsd'))
        self.btnGenSaveTurbo.clicked.connect(lambda: self.start_runer('gtd'))

        self.btnLog.clicked.connect(lambda x: open_local_file('log.txt'))
        self.btnErr.clicked.connect(lambda x: open_local_file('errors.txt'))

        self.btnPause.clicked.connect(lambda: self.runner.pause())
        self.btnStop.clicked.connect(lambda: self.runner.kill())

        self.lblBanner.mousePressEvent = baner_click_event

        self.chPDF.clicked.connect(lambda: self.update_values())
        self.chHTML.clicked.connect(lambda: self.update_values())
        self.chTXT.clicked.connect(lambda: self.update_values())
        self.chJSON.clicked.connect(lambda: self.update_values())
        self.chCSV.clicked.connect(lambda: self.update_values())

        self.action_github.triggered.connect(
            lambda: webbrowser.open_new('https://github.com/Rzezimioszek/eKW-pobieracz'))
        self.action_Wsparcie.triggered.connect(
            lambda: webbrowser.open_new('https://www.paypal.com/donate/?hosted_button_id=2AFDC9PRMGN3Q'))

        self.action_Instrukcja.triggered.connect(
            lambda x: open_local_file('eKW pobieraczek - instrukcja.pdf'))

        self.btn_Github.clicked.connect(lambda: webbrowser.open_new('https://github.com/Rzezimioszek/eKW-pobieracz'))
        self.btn_Coffe.clicked.connect(lambda: webbrowser.open_new('https://www.paypal.com/donate/?hosted_button_id=2AFDC9PRMGN3Q'))
        self.btn_Instrukcja.clicked.connect(lambda x: open_local_file('eKW pobieraczek - instrukcja.pdf'))

        self.action_muzyka.triggered.connect(lambda x: self.music_switch())

    def load_config(self):
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

        self.kw_list = self.exist_setting('kwlist')
        self.save_path = self.exist_setting('savepath')

        if 'Save' not in self.setting.keys():
            self.setting['Save'] = {'save_pdf': True,
                                    'save_html': True,
                                    'save_txt': True,
                                    'save_raport': True,
                                    'save_csv': True,
                                    'save_json1o': True
                                    }

        self.setting['Music'] = self.exist_setting('Music', True)

        if not self.setting['Music']:
            sound.stop()

        self.save_pdf = self.exist_setting('Save')['save_pdf']
        self.save_html = self.exist_setting('Save')['save_html']
        self.save_txt = self.exist_setting('Save')['save_txt']
        self.save_raport = self.exist_setting('Save')['save_raport']
        self.save_csv = self.exist_setting('Save')['save_csv']
        self.save_json1o = self.exist_setting('Save')['save_json1o']

        self.ch1o.setChecked(self.exist_setting('dzial_1o', True))
        self.ch1s.setChecked(self.exist_setting('dzial_1s', True))
        self.ch2.setChecked(self.exist_setting('dzial_2', True))
        self.ch3.setChecked(self.exist_setting('dzial_3', True))
        self.ch4.setChecked(self.exist_setting('dzial_4', True))

        self.chSkip.setChecked(self.exist_setting('Skip', True))
        self.chProxy.setChecked(self.exist_setting('Proxy', True))
        self.lineProxy.setText(self.exist_setting('ProxyIP'))

        self.load_format_checks()

        self.lineSign.setText(self.exist_setting('sign'))
        self.lineFloor.setText(self.exist_setting('startnum'))
        self.lineRoof.setText(self.exist_setting('endnum'))

        self.lineLast.setText(self.exist_setting('parms_last'))
        self.lineControl.setText(self.exist_setting('parms_control'))

        self.lineList.setText(self.kw_list)
        self.lineSave.setText(self.save_path)

        self.cbBrowser.setCurrentText(self.exist_setting('engine'))
        self.chImg.setChecked(self.exist_setting('image'))

    def music_switch(self):

        self.setting['Music'] = not self.setting['Music']

        if self.setting['Music']:
            sound.play()
        else:
            sound.stop()

    def start_runer(self, action):

        match action:
            case "ds":
                self.runner = ListStandard(self.get_list())
            case "dt":
                self.runner = ListTurbo(self.get_list())
            case 'gs':
                self.runner = GenerateStandard(False)
            case 'gsd':
                self.runner = GenerateStandard(True)
            case 'gtd':
                self.runner = GenerateTurbo(True)
            case _:
                return

        self.runner.progress.connect(self.update_progress)
        self.runner.stat.connect(self.update_status)
        self.runner.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def update_status(self, value):
        self.lblStatus.setText(value)

    def load_format_checks(self):
        self.chPDF.setChecked(self.save_pdf)
        self.chHTML.setChecked(self.save_html)
        self.chTXT.setChecked(self.save_txt)
        self.chJSON.setChecked(self.save_raport)
        self.chCSV.setChecked(self.save_csv)
        self.chJSON1o.setChecked(self.save_json1o)

        self.chTheme.setChecked(get_theme())

    def update_values(self):
        self.save_pdf = self.chPDF.isChecked()
        self.save_html = self.chHTML.isChecked()
        self.save_txt = self.chTXT.isChecked()
        self.save_raport = self.chJSON.isChecked()
        self.save_csv = self.chCSV.isChecked()

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

    def get_list(self):

        self.kw_list = self.lineList.text()

        with open(self.kw_list, 'r') as file:
            values = file.readlines()
        # value = 'OP1U/00004102/3'

        distinct = set(values)

        return_value = sorted(distinct)

        return return_value

    def exist_setting(self, key, bool=False):
        if key in self.setting.keys():
            return self.setting[key]
        else:
            if bool:
                return False
            else:
                return ""


def get_driver(img: bool = True):


    main_browser = str(win.cbBrowser.currentText())[0]

    # print(main_browser)

    match main_browser:
        case "c": # Chrome
            try:
                options = webdriver.ChromeOptions()

                ###
                # Uwzgędniono poprawki od tisher2
                prefs = {"profile.managed_default_content_settings.images":  2 if not img else 1, # Wyłącza obrazy, jeśli img=False
                         "disk-cache-size": 4096,  # Optymalizuje cache
                         "profile.default_content_setting_values.notifications": 2,  # Wyłącza powiadomienia
                         "profile.default_content_setting_values.geolocation": 2,  # Wyłącza geolokalizację
                         "credentials_enable_service": False,  # Wyłącza zapisywanie haseł
                         "profile.password_manager_enabled": False  # Wyłącza menedżera haseł
                         }



                options.add_experimental_option("prefs", prefs)


                if win.chProxy.isChecked():
                    proxy = win.lineProxy.text()
                    options.add_argument(f"--proxy-server={proxy}")

                options.add_argument("--disable-extensions")  # Wyłącza rozszerzenia
                options.add_argument("--disable-gpu")  # Wyłącza GPU (ważne przy problemach z GPU)
                options.add_argument("--disable-webgl")  # Wyłącza WebGL
                options.add_argument("--disable-infobars")  # Ukrywa informacje
                options.add_argument("--no-sandbox")  # Wyłącza piaskownicę
                options.add_argument("--disable-dev-shm-usage")  # Optymalizuje pamięć dzieloną
                options.add_argument("--disable-popup-blocking")  # Wyłącza blokowanie wyskakujących okienek
                options.add_argument("--disable-software-rasterizer")  # Wyłącza rasteryzację software'ową
                options.add_argument("--disable-features=TranslateUI")  # Wyłącza tłumaczenie stron
                options.add_argument("--disable-sync")  # Wyłącza synchronizację
                options.add_argument(
                    "--disable-background-timer-throttling")  # Wyłącza ograniczanie liczby timerów w tle
                options.add_argument("--renderer-process-limit=2")  # Ograniczenie liczby procesów renderowania

                ###

                """        WINDOW_SIZE = "1920,1080"
                options.add_argument("--headless=new")
                options.add_argument("--window-size=%s" % WINDOW_SIZE)
                options.add_argument("disable-gpu")"""

                # options.add_argument("--start-minimized")
                options.add_argument("--disable-search-engine-choice-screen")

                service = Service()
                browser = webdriver.Chrome(service=service, options=options)
                browser.minimize_window()

                return browser

            except:

                return get_driver(main_browser="edge")

        case "e": # Edge
            try:

                options = webdriver.EdgeOptions()

                ###
                # Uwzgędniono poprawki od tisher2
                prefs = {"profile.managed_default_content_settings.images": 2 if not img else 1,
                             # Wyłącza obrazy, jeśli img=False
                             "disk-cache-size": 4096,  # Optymalizuje cache
                             "profile.default_content_setting_values.notifications": 2,  # Wyłącza powiadomienia
                             "profile.default_content_setting_values.geolocation": 2,  # Wyłącza geolokalizację
                             "credentials_enable_service": False,  # Wyłącza zapisywanie haseł
                             "profile.password_manager_enabled": False  # Wyłącza menedżera haseł
                             }
                options.add_experimental_option("prefs", prefs)


                if win.chProxy.isChecked():
                    proxy = win.lineProxy.text()
                    options.add_argument(f"--proxy-server={proxy}")


                options.add_argument("--disable-extensions")  # Wyłącza rozszerzenia
                options.add_argument("--disable-gpu")  # Wyłącza GPU (ważne przy problemach z GPU)
                options.add_argument("--disable-webgl")  # Wyłącza WebGL
                options.add_argument("--disable-infobars")  # Ukrywa informacje
                options.add_argument("--no-sandbox")  # Wyłącza piaskownicę
                options.add_argument("--disable-dev-shm-usage")  # Optymalizuje pamięć dzieloną
                options.add_argument("--disable-popup-blocking")  # Wyłącza blokowanie wyskakujących okienek
                options.add_argument("--disable-software-rasterizer")  # Wyłącza rasteryzację software'ową
                options.add_argument("--disable-features=TranslateUI")  # Wyłącza tłumaczenie stron
                options.add_argument("--disable-sync")  # Wyłącza synchronizację
                options.add_argument(
                    "--disable-background-timer-throttling")  # Wyłącza ograniczanie liczby timerów w tle
                options.add_argument("--renderer-process-limit=2")  # Ograniczenie liczby procesów renderowania

                ###


                service = Service()
                browser = webdriver.Edge(service=service, options=options)
                browser.minimize_window()
                return browser

            except:

                return get_driver(main_browser="firefox")


        case "f": # Firefox
            try:
                options = webdriver.FirefoxOptions()

                if not img:
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    options.set_preference("permissions.default.image", 2)

                if win.chProxy.isChecked():
                    proxy = win.lineProxy.text()
                    options.add_argument(f"--proxy-server={proxy}")

                service = Service()
                browser = webdriver.Firefox(service=service, options=options)
                browser.minimize_window()

                return browser

            except:

                print("Error")
                return get_driver(main_browser="error")
        case "s": # Safari
            ...
        case _:
            return ''

def safe_quit_browser(browser):
    """Bezpieczne zamknięcie przeglądarki."""
    if browser:
        try:
            browser.close()
            browser.quit()
        except Exception as e:
            print(f"Błąd podczas zamykania przeglądarki: {e}")


def save_settings():
    win.setting['kwlist'] = win.lineList.text()
    win.setting['savepath'] = win.lineSave.text()

    win.setting['sign'] = win.lineSign.text()
    win.setting['startnum'] = win.lineFloor.text()
    win.setting['endnum'] = win.lineRoof.text()
    win.setting['Save'] = {'save_pdf': win.chPDF.isChecked(),
                           'save_html': win.chHTML.isChecked(),
                           'save_txt': win.chTXT.isChecked(),
                           'save_raport': win.chJSON.isChecked(),
                           'save_csv': win.chCSV.isChecked(),
                           'save_json1o': win.chJSON1o.isChecked()}
    win.setting['Skip'] = win.chSkip.isChecked()
    win.setting['Proxy'] = win.chProxy.isChecked()
    win.setting['ProxyIP'] = win.lineProxy.text()

    # save chapters preferences

    win.setting['dzial_1o'] = win.ch1o.isChecked()
    win.setting['dzial_1s'] = win.ch1s.isChecked()
    win.setting['dzial_2'] = win.ch2.isChecked()
    win.setting['dzial_3'] = win.ch3.isChecked()
    win.setting['dzial_4'] = win.ch4.isChecked()

    win.setting['parms_last'] = win.lineLast.text()
    win.setting['parms_control'] = win.lineControl.text()

    win.setting['engine'] = win.cbBrowser.currentText()

    win.setting['image'] = win.chImg.isChecked()


    with open(win.config, "w", encoding="utf-8") as file:
        json.dump(win.setting, file, ensure_ascii=False)

    set_theme(win.chTheme.isChecked())

    sys.exit(app.exec())


def save_kw_to_pdf(value: str):  #

    save_path = win.lineSave.text()
    pdf_bg = win.chBg.isChecked()

    zupelna = False

    to_merge = []
    merge = win.chMerge.isChecked()

    gen_err(f"{value}\t- Wprowadzona wartość")

    max_retries = 5
    retries = 0
    browser = None
    while retries < max_retries:
        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = win.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"{value}\t- Poprawiono cyfrę kontrolną")


            if win.chSkip.isChecked():

                ext_list = [str(Path(p).stem)[0:16] for p in os.listdir(save_path)]
                if value.replace('/', '.') in ext_list:
                    return

            browser = get_driver(win.chImg.isChecked())
            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

            time.sleep(1)  # 3 -> 1

            insert_kw_number(browser, kw)

            time.sleep(1)

            if win.save_raport or win.save_csv:

                info = get_dictionary(browser)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}"
                if win.save_raport:
                    save_json(info, path_without_ext)

                if win.save_csv:
                    save_csv(info, f"{save_path}/")

            if not win.save_pdf and not win.save_txt and not win.save_html and not win.chJSON1o:
                safe_quit_browser(browser)
                return

            # Sprawdzenie i próba pobrania

            try:
                elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
                elem.send_keys(Keys.RETURN)

            except NoSuchElementException:
                zupelna = True
                err = f"{value}\t- Treść zwykła wydruku niedostępna dla"
                gen_err(err)
                break  # Wyjście z pętli, przejście do obsługi treści zupełnej

            break  # Wszystko przebiegło pomyślnie, wyjście z pętli

        except (TimeoutException, WebDriverException, MaxRetryError, NewConnectionError) as e:
            # Błędy sieciowe lub przeglądarki
            retries += 1
            gen_err(f"Błąd przeglądarki lub sieci: {str(e)}. Ponawianie próby {retries}/{max_retries}...", log=True)
            safe_quit_browser(browser)
            time.sleep(10)  # Poczekaj przed ponowną próbą


            if retries == max_retries:
                gen_err(f"Przekroczono maksymalną liczbę prób pobierania danych dla {value}.", write=True)
                return

    # Drugi blok try/except dla obsługi wyjątków specyficznych dla treści księgi
    try:
        if zupelna:
            if win.chError.isChecked():
                elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                elem.send_keys(Keys.RETURN)
                gen_err("{value}\t- Pobieranie treści zupełnej")
            else:
                err = f"{value}\t- Błąd pobierania treści zupełnej księgi"
                gen_err(err, write=True)
                browser.close()
                browser.quit()
                return
    except Exception as e:
        err = f"{value}\t- Błąd pobierania księgi: {str(e)}"
        gen_err(err, write=True)
        safe_quit_browser(browser)
        return

    try:

        path_without_ext = f"{save_path}/{value.replace('/', '.')}"
        t_s = 1

        if win.ch1o.isChecked():

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział I-O", path_without_ext, 1))

        if win.ch1s.isChecked():

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział I-Sp", path_without_ext, 1))

        if win.ch2.isChecked():

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział II", path_without_ext, 2))

        if win.ch3.isChecked():

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział III", path_without_ext, 3))

        if win.ch4.isChecked():

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział IV", path_without_ext, 4))

        gen_err(f"{value}\t- Pobrano księgę")
    except Exception as e:

        err = f"{value}\t- Błąd pobierania wybranych działów księgi: {str(e)}"
        gen_err(err, write=True)
        safe_quit_browser(browser)
        return

    finally:
        safe_quit_browser(browser)

    try:
        if win.save_pdf and merge and len(to_merge) > 0:

            gen_err(f"{value}\t- Łączenie pojedynczych działów KW w jeden plik", log=True)

            out_pdf = pypdf.PdfWriter()
            dst_path = f"{save_path}/{value.replace('/', '.')}.pdf"

            for tm in to_merge:
                src_pdf = pypdf.PdfReader(tm)
                out_pdf.append_pages_from_reader(src_pdf)

            with open(dst_path, "wb") as file:
                out_pdf.write(file)

            gen_err(f"{value}\t- Usuwanie pojedynczych działów KW", log=True)

            for tm in to_merge:
                os.remove(tm)

    except Exception as e:
        err = f"{value}\t- Błąd łączenia działów księgi: {str(e)}"
        gen_err(err, write=True)


async def save_kw_to_pdf_turbo(value: str):

        save_path: str = win.lineSave.text()
        to_merge = []
        merge = win.chMerge.isChecked()
        zupelna = False

        gen_err(f"{value}\t- Wprowadzona wartość")

        max_retries = 5
        retries = 0
        browser = None

        while retries < max_retries:
            try:
                kw = value.split('/')

                if 2 <= len(kw) < 3:
                    value = win.correct_kw_number(kw[0], kw[1])
                    kw = value.split('/')
                    gen_err(f"{value}\t- Poprawiono cyfrę kontrolną")

                value = value.strip()


                if win.chSkip.isChecked():

                    ext_list = [Path(p).stem for p in os.listdir(save_path)]
                    if value.replace('/', '.') in ext_list:
                        logging.info(f"Skiped {value}")
                        safe_quit_browser(browser)
                        return

                browser = get_driver(win.chImg.isChecked())

                tries = 0

                while True:
                    if tries > 3:
                        gen_err(f"{value} - Nieudane połącznie po liczbie prób: {tries}", log=True)
                        return

                    tries += 1
                    browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')
                    if browser.page_source.find("The requested URL was rejected") > 0:
                        gen_err(f"{value} - Odrzucono żądanie {tries}. Chwila przerwy...", log=True)

                        await asyncio.sleep(30)
                        continue
                    break

                await asyncio.sleep(1) # 3 -> 1

                insert_kw_number(browser, kw)

                await asyncio.sleep(1) # Czekaj na załadowanie wyników

                if win.save_raport or win.save_csv:

                    info = get_dictionary(browser)

                    path_without_ext = f"{save_path}/{value.replace('/', '.')}"
                    if win.save_raport:
                        save_json(info, path_without_ext)

                    if win.save_csv:
                        save_csv(info, f"{save_path}/")

                if not win.save_pdf and not win.save_txt and not win.save_html and not win.chJSON1o:
                    safe_quit_browser(browser)
                    return

                # Sprawdzenie i próba pobrania
                try:
                    elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
                    elem.send_keys(Keys.RETURN)
                except NoSuchElementException:
                    zupelna = True
                    err = f"{value}\t- Treść zwykła wydruku niedostępna dla"
                    gen_err(err)
                    break  # Wyjście z pętli, przejście do obsługi treści zupełnej

                break  # Wszystko przebiegło pomyślnie, wyjście z pętli



            except (TimeoutException, WebDriverException, MaxRetryError, NewConnectionError) as e:

                # Błędy sieciowe lub przeglądarki
                retries += 1
                gen_err(f"Błąd przeglądarki lub sieci: {str(e)}. Ponawianie próby {retries}/{max_retries}...", log=True)
                safe_quit_browser(browser)
                await asyncio.sleep(10)  # Poczekaj przed ponowną próbą

                if retries == max_retries:
                    gen_err(f"Przekroczono maksymalną liczbę prób pobierania danych dla {value}.", write=True)
                    return

        # Drugi blok try/except dla obsługi wyjątków specyficznych dla treści księgi
        try:
            if zupelna:
                if win.chError.isChecked():
                    elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                    elem.send_keys(Keys.RETURN)
                    gen_err(f"{value}\t- Pobieranie treści zupełnej")
                else:
                    err = f"{value}\t- Błąd pobierania treści zupełnej księgi"
                    gen_err(err, write=True)
                    safe_quit_browser(browser)
                    return
        except Exception as e:
            err = f"{value}\t- Błąd pobierania księgi"
            gen_err(err, write=True)
            safe_quit_browser(browser)
            return

        try:
            path_without_ext = f"{save_path}/{value.replace('/', '.')}"

            t_s = 1

            if win.ch1o.isChecked():

                await asyncio.sleep(t_s)
                to_merge.append(save_page(browser, "Dział I-O", path_without_ext, 1))

            if win.ch1s.isChecked():

                await asyncio.sleep(t_s)
                to_merge.append(save_page(browser, "Dział I-Sp", path_without_ext, 1))

            if win.ch2.isChecked():

                await asyncio.sleep(t_s)
                to_merge.append(save_page(browser, "Dział II", path_without_ext, 2))

            if win.ch3.isChecked():

                await asyncio.sleep(t_s)
                to_merge.append(save_page(browser, "Dział III", path_without_ext, 3))

            if win.ch4.isChecked():

                await asyncio.sleep(t_s)
                to_merge.append(save_page(browser, "Dział IV", path_without_ext, 4))

            gen_err(f"{value}\t- Pobrano księgę")
        except Exception as e:

            err = f"{value}\t- Błąd pobierania wybranych działów księgi: {str(e)}"
            gen_err(err, write=True)
            safe_quit_browser(browser)
            return

        finally:
            safe_quit_browser(browser)


        try:
            if merge and win.save_pdf and len(to_merge) > 0:

                await asyncio.sleep(2)

                gen_err(f"{value}\t- Łączenie pojedynczych działów KW w jeden plik", log=True)

                out_pdf = pypdf.PdfWriter()
                dst_path = f"{save_path}/{value.replace('/', '.')}.pdf"

                for tm in to_merge:
                    src_pdf = pypdf.PdfReader(tm)
                    out_pdf.append_pages_from_reader(src_pdf)

                with open(dst_path, "wb") as file:
                    out_pdf.write(file)

                gen_err(f"{value}\t- Usuwanie pojedynczych działów KW", log=True)

                for tm in to_merge:
                    os.remove(tm)

        except Exception as e:
            err = f"{value}\t- Błąd łączenia działów księgi: {str(e)}"
            gen_err(err, write=True, log=True)




def save_page(browser, dzial, path_without_ext, i):

    find_wait(browser, f'input[value="{dzial}"]').click()

    path_without_ext = f"{path_without_ext}_{i}"

    if dzial == 'Dział I-O':
        path_without_ext = f"{path_without_ext}o"
    elif dzial == 'Dział I-Sp':
        path_without_ext = f"{path_without_ext}s"


    if dzial == 'Dział I-O':
        if win.save_html or win.chJSON1o.isChecked() or win.chDzList.isChecked():
            save_html(browser,
                      path_without_ext,
                      win.chJSON1o.isChecked(),
                      win.chHTML.isChecked(),
                      win.chXlsx.isChecked())

            if win.chDzList.isChecked():
                dzs = eh.dz_from_page(f"{path_without_ext}.html").values()
                dz = [x['Numer działki'] for x in dzs]
                wanted = get_wanted_dz(win.lineDzList.text())

                # print([x['Numer działki'] for x in dzs])

                skip = True
                for w in wanted:
                    if w in dz:
                        skip = False
                if skip:
                    # print("Download skiped")
                    browser.quit()
                    return
    else:
        if win.save_html:
            save_html(browser,
                      path_without_ext,
                      win.chJSON1o.isChecked(),
                      win.chHTML.isChecked(),
                      win.chXlsx.isChecked())

    if win.save_txt: save_txt(browser, path_without_ext)
    if win.save_pdf:
        save_pdf(browser, path_without_ext, win.chBg.isChecked())
        return f"{path_without_ext}.pdf"
    return None


def set_fusion(light=False):
    app.setStyle('Fusion')

    if light:
        return
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(210, 10, 255))
    dark_palette.setColor(QPalette.Highlight, QColor(210, 10, 255))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #d20aff; border: 1px solid white; }")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    set_fusion(get_theme())

    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(save_settings)

    sound = QSound("res/boss_time.wav")
    sound.setLoops(QSound.Infinite)
    sound.play()

    win = Window()
    win.show()

    sys.exit(app.exec())

