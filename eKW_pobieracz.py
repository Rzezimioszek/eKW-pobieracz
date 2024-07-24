from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType

from datetime import datetime
import asyncio

from pathlib import Path

import pandas as pd
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

import pypdf as pypdf
import logging
# from vlc import MediaPlayer


# #### ## Kod dla UI

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QStyle
)
from PyQt5.uic import loadUi

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import QThread, pyqtSignal, Qt

from PyQt5.QtGui import QPalette, QColor

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

from eKW_pobieracz_ui import Ui_MainWindow

import extract_html as eh

# #### ##

# eKW pobieracz 0.8
eKWp_ver = "1.0a"

logging.basicConfig(format="%(message)s", level=logging.INFO)

"""class MusicLooper(QThread):
    def __init__(self):
        super().__init__()
        self.play = True

    def run(self):
        music_path = "res/boss_time.mp3"
        if os.path.exists(music_path):
            while True:
                self.musicplayer = MediaPlayer(music_path)
                self.musicplayer.play()
                for _ in range(60):
                    if not self.play:
                        break
                    else:
                        time.sleep(1)
                if not self.play:
                    break

    def change(self):

        self.play = False
        self.musicplayer.stop()
        self.terminate()
        self.quit()"""



class GenerateStandard(QThread):
    progress = pyqtSignal(int)
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
            #gen_err(err, True)
            return

        try:
            sad_value = [win.rep_dict[s] for s in sad]
        except:
            err = f"Oznaczenie sądu {sad} nieprawidłowe"
            #gen_err(err, True)
            return

        if not bot.isdecimal() or not top.isdecimal():
            err = f"Nieporawny przedział dla wartości dolnej lub górnej"
            #gen_err(err, True)
            return

        bot = int(bot)
        top = int(top)

        if top > 99999999:
            err = f"Wartość górna {top} powyżej dozwolonego przedziału zmiana na 99999999"
            #gen_err(err)
            top = 99999999

        if bot < 1:
            err = f"Wartość dolna {bot} poniżejj dozwolonego przedziału zmiana na 1"
            #gen_err(err)
            bot = 1

        if bot > top:
            err = f"Wartość dolna {bot} większa od górnej {top}"
            #gen_err(err)
            return

        if not self.download:

            #gen_err(f"Generowanie listy Kw dla sądu {sad} i przedziału {bot} do {top}")

            filetypes = (("pliki txt", "*.txt"), ("Wszystkie pliki", "*.*"))
            path = filedialog.asksaveasfilename(title="Zapisz plik txt", filetypes=filetypes)
            if path is not None:
                if not path.endswith(".txt"):
                    path = path + ".txt"

            with open(path, "w") as file:
                file.write(f"")
        else:
            path = "c:/"
            #gen_err(f"Pobieranie KW dla: {sad}/{bot}-{top}/n")

        if path == "":
            err = f"Niepodano scięzki zapisu"
            #gen_err(err, True)
            return

        proc = 0
        end = top

        self.progress.emit(proc)


        for i in range(bot, (top + 1)):

            try:

                nk = win.correct_kw_number(sad, str(i))
                logging.info(nk)

                if self.download:
                    save_kw_to_pdf(nk) #without self
                else:
                    with open(path, "a") as file:
                        file.write(f"{nk}\n")


                proc = int(((i - bot)/(end - bot)) * 100)
                # logging.info(f"{proc}%\t{i}\t{end}")
                proc = 1 if proc <= 0 else proc
                proc = 100 if proc >= 100 else proc
                # win.progressBar.setValue(proc)
                self.progress.emit(proc)

            except:
                #gen_err(f"Bład generownaia w pozycji {i}", log=True, write=True)
                logging.info(f"Bład generownaia w pozycji {i}")
                return

            if self.is_killed:
                #gen_err(f"Wygenerowano {proc}% z zadanego zakresu", log=True)
                self.is_killed = False
                break
            while self.is_paused:
                time.sleep(1)

        if self.download:
            msg.showinfo("Generator", "Zakończono pobieranie z zadanego zakresu")
        else:
            msg.showinfo("Generator", "Zakończono generowanie z zadanego zakresu")
        # self.quit()
        # quit()

        # return

    def save_kw_to_pdf(self, value: str):  #

        save_path = win.lineSave.text()
        pdf_bg = win.chBg.isChecked()

        zupelna = False

        to_merge = []
        merge = win.chMerge.isChecked()

        gen_err(f"Wprowadzona wartość: {value}")

        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = win.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"Poprawiono cyfrę kontrolną: {value}")

            browser = get_driver(win.chImg.isChecked())

            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

            time.sleep(3)  #

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

            if win.save_raport or win.save_csv:

                info = get_dictionary(browser)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}"
                if win.save_raport:
                    save_json(info, path_without_ext)

                if win.save_csv:
                    save_csv(info, f"{save_path}/")

                # save_txt(browser, cur_path)

            if not win.save_pdf and not win.save_txt and not win.save_html:
                return

            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
            elem.send_keys(Keys.RETURN)

            ###
        except:
            zupelna = True
            err = f"Treść zwykła wydruku niedostępna dla: {value}"
            gen_err(err)

        try:
            if zupelna:
                if win.chError.isChecked():
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

            if win.ch1o.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])

                cur_path = f"{self.save_path}/{value.replace('/', '.')}_{i}o.pdf"
                with open(cur_path, "wb") as f:
                    f.write(pdf_data)

                if merge:
                    to_merge.append(cur_path)

            if win.ch1s.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])

                cur_path = f"{self.save_path}/{value.replace('/', '.')}_{i}s.pdf"
                with open(cur_path, "wb") as f:
                    f.write(pdf_data)

                if merge:
                    to_merge.append(cur_path)

            i = 2  # dział II

            if win.ch2.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])

                cur_path = f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf"
                with open(cur_path, "wb") as f:
                    f.write(pdf_data)

                if merge:
                    to_merge.append(cur_path)

            i = 3  # dział III

            if win.ch3.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])

                cur_path = f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf"
                with open(cur_path, "wb") as f:
                    f.write(pdf_data)

                if merge:
                    to_merge.append(cur_path)

            i = 4  # dział IV

            if win.ch4.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
                pdf_data = base64.b64decode(pdf["data"])

                cur_path = f"{self.save_path}/{value.replace('/', '.')}_{i}.pdf"
                with open(cur_path, "wb") as f:
                    f.write(pdf_data)

                if merge:
                    to_merge.append(cur_path)

            gen_err(f"Pobrano księgę: {value}")
        except:

            err = f"Błąd pobierania wybranych działów księgi: {value}"
            gen_err(err, write=True)

        try:
            if merge and len(to_merge) > 0:

                gen_err(f"Łączenie pojedynczych działów KW w jeden plik: {value}", log=True)

                out_pdf = pypdf.PdfWriter()
                dst_path = f"{self.save_path}/{value.replace('/', '.')}.pdf"

                for tm in to_merge:
                    src_pdf = pypdf.PdfReader(tm)
                    out_pdf.append_pages_from_reader(src_pdf)

                with open(dst_path, "wb") as file:
                    out_pdf.write(file)

                gen_err(f"Usuwanie pojedynczych działów KW: {value}", log=True)

                for tm in to_merge:
                    os.remove(tm)

        except:
            err = f"Błąd łączenia działów księgi: {value}"
            gen_err(err, write=True)

    def kill(self):
        self.is_killed = True

    def pause(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True

class GenerateTurbo(QThread):
    progress = pyqtSignal(int)
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


        sad = win.lineSign.text().strip().upper()
        bot = win.lineFloor.text().strip()
        top = win.lineRoof.text().strip()

        clear_log()

        if sad not in win.sady:
            err = f"Brak oznaczenia sądu [{sad}], sprawdz plik res/sady.kw"
            #gen_err(err, True)
            return

        try:
            sad_value = [win.rep_dict[s] for s in sad]
        except:
            err = f"Oznaczenie sądu {sad} nieprawidłowe"
            #gen_err(err, True)
            return

        if not bot.isdecimal() or not top.isdecimal():
            err = f"Nieporawny przedział dla wartości dolnej lub górnej"
            #gen_err(err, True)
            return

        bot = int(bot)
        top = int(top)

        if top > 99999999:
            err = f"Wartość górna {top} powyżej dozwolonego przedziału zmiana na 99999999"
            #gen_err(err)
            top = 99999999

        if bot < 1:
            err = f"Wartość dolna {bot} poniżejj dozwolonego przedziału zmiana na 1"
            #gen_err(err)
            bot = 1

        if bot > top:
            err = f"Wartość dolna {bot} większa od górnej {top}"
            #gen_err(err)
            return

        if not self.download:

            #gen_err(f"Generowanie listy Kw dla sądu {sad} i przedziału {bot} do {top}")

            filetypes = (("pliki txt", "*.txt"), ("Wszystkie pliki", "*.*"))
            path = filedialog.asksaveasfilename(title="Zapisz plik txt", filetypes=filetypes)
            if path is not None:
                if not path.endswith(".txt"):
                    path = path + ".txt"

            with open(path, "w") as file:
                file.write(f"")
        else:
            path = "c:/"
            #gen_err(f"Pobieranie KW dla: {sad}/{bot}-{top}/n")

        if path == "":
            err = f"Niepodano scięzki zapisu"
            #gen_err(err, True)
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
                logging.info(nk)

                task.append(asyncio.create_task(save_kw_to_pdf_turbo(nk)))
                j += 1

                if j == n or i == top:
                    k += 1
                    gen_err(f"Pętla: {k}")
                    await asyncio.gather(*task)
                    task.clear()

                    proc = int(((i - bot)/(end - bot)) * 100)
                    proc = 1 if proc <= 0 else proc
                    proc = 100 if proc >= 100 else proc

                    self.progress.emit(proc)

                    if self.is_killed:
                        break
                    while self.is_paused:
                        time.sleep(1)
                    # await asyncio.sleep(9 * j)
                    j = 0

            except:
                #gen_err(f"Bład generownaia w pozycji {i}", log=True, write=True)
                logging.info(f"Bład generownaia w pozycji {i}")
                return

            if self.is_killed:
                #gen_err(f"Wygenerowano {proc}% z zadanego zakresu", log=True)
                self.is_killed = False
                break
            while self.is_paused:
                time.sleep(1)


    def kill(self):
        self.is_killed = True

    def pause(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True

class ListStandard(QThread):
    progress = pyqtSignal(int)
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

        try:
            values = self.values
        except:
            msg.showerror("Zła lista", "Plik wejściowy z listą kw niepoprawny.")
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

            if self.is_killed:
                break
            while self.is_paused:
                time.sleep(1)

        if self.is_killed:
            gen_err(f"Zakończono pobieranie na: {proc}%")
            # win.progressBar.setValue(0)
            self.progress.emit(proc)
            msg.showinfo("Zakończono pobieranie", f"Pobrano {proc}% wybranych ksiąg")
        else:
            gen_err("Wszystkie księgi wieczyste z zadania zostały pobrane")
            msg.showinfo("Zakończono pobieranie", "Wszystkie księgi wieczyste z zadania zostały pobrane")

        msg.showinfo("Generator", "Zakończono pobieranie z listy")

    def save_kw_to_pdf(self, value: str):  #

        self.save_path = win.lineSave.text()
        self.pdf_bg = win.chBg.isChecked()

        zupelna = False

        to_merge = []
        merge = win.chMerge.isChecked()

        gen_err(f"Wprowadzona wartość: {value}")

        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = win.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"Poprawiono cyfrę kontrolną: {value}")

            browser = get_driver(win.chImg.isChecked())

            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

            time.sleep(3)  #

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

            if win.save_raport:

                info = get_dictionary(browser)

                path_without_ext = f"{self.save_path}/{value.replace('/', '.')}"

                save_json(info, path_without_ext)
                save_csv(info, path_without_ext)

            if not win.save_pdf and not win.save_txt and not win.save_html:
                return

            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
            elem.send_keys(Keys.RETURN)

            ###
        except:
            zupelna = True
            err = f"Treść zwykła wydruku niedostępna dla: {value}"
            gen_err(err)

        try:
            if zupelna:
                if win.chError.isChecked():
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

            if win.ch1o.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{self.save_path}/{value.replace('/', '.')}_{i}o"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:

                    save_pdf(browser, path_without_ext)

                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            if win.ch1s.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{self.save_path}/{value.replace('/', '.')}_{i}s"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:

                    save_pdf(browser, path_without_ext)

                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            i = 2  # dział II

            if win.ch2.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{self.save_path}/{value.replace('/', '.')}_{i}"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:

                    save_pdf(browser, path_without_ext)

                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            i = 3  # dział III

            if win.ch3.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{self.save_path}/{value.replace('/', '.')}_{i}"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:

                    save_pdf(browser, path_without_ext)

                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            i = 4  # dział IV

            if win.ch4.isChecked():

                time.sleep(2)  #

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{self.save_path}/{value.replace('/', '.')}_{i}"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:

                    save_pdf(browser, path_without_ext)

                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            gen_err(f"Pobrano księgę: {value}")
        except:

            err = f"Błąd pobierania wybranych działów księgi: {value}"
            gen_err(err, write=True)

        try:
            if merge and len(to_merge) > 0:

                gen_err(f"Łączenie pojedynczych działów KW w jeden plik: {value}", log=True)

                out_pdf = pypdf.PdfWriter()
                dst_path = f"{self.save_path}/{value.replace('/', '.')}.pdf"

                for tm in to_merge:
                    src_pdf = pypdf.PdfReader(tm)
                    out_pdf.append_pages_from_reader(src_pdf)

                with open(dst_path, "wb") as file:
                    out_pdf.write(file)

                gen_err(f"Usuwanie pojedynczych działów KW: {value}", log=True)

                for tm in to_merge:
                    os.remove(tm)

        except:
            err = f"Błąd łączenia działów księgi: {value}"
            gen_err(err, write=True)

    def kill(self):
        self.is_killed = True

    def pause(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True

class ListTurbo(QThread):
    progress = pyqtSignal(int)
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

    async def generator(self):

        self.progress.emit(0)

        sad = win.lineSign.text().strip().upper()
        bot = win.lineFloor.text().strip()
        top = win.lineRoof.text().strip()

        clear_log()

        if sad not in win.sady:
            err = f"Brak oznaczenia sądu [{sad}], sprawdz plik res/sady.kw"
            # gen_err(err, True)
            return

        try:
            sad_value = [win.rep_dict[s] for s in sad]
        except:
            err = f"Oznaczenie sądu {sad} nieprawidłowe"
            # gen_err(err, True)
            return

        if not bot.isdecimal() or not top.isdecimal():
            err = f"Nieporawny przedział dla wartości dolnej lub górnej"
            # gen_err(err, True)
            return

        bot = int(bot)
        top = int(top)

        if top > 99999999:
            err = f"Wartość górna {top} powyżej dozwolonego przedziału zmiana na 99999999"
            # gen_err(err)
            top = 99999999

        if bot < 1:
            err = f"Wartość dolna {bot} poniżejj dozwolonego przedziału zmiana na 1"
            # gen_err(err)
            bot = 1

        if bot > top:
            err = f"Wartość dolna {bot} większa od górnej {top}"
            # gen_err(err)
            return

        if not self.download:

            # gen_err(f"Generowanie listy Kw dla sądu {sad} i przedziału {bot} do {top}")

            filetypes = (("pliki txt", "*.txt"), ("Wszystkie pliki", "*.*"))
            path = filedialog.asksaveasfilename(title="Zapisz plik txt", filetypes=filetypes)
            if path is not None:
                if not path.endswith(".txt"):
                    path = path + ".txt"

            with open(path, "w") as file:
                file.write(f"")
        else:
            path = "c:/"
            # gen_err(f"Pobieranie KW dla: {sad}/{bot}-{top}/n")

        if path == "":
            err = f"Niepodano scięzki zapisu"
            # gen_err(err, True)
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
                logging.info(nk)

                task.append(asyncio.create_task(self.save_kw_to_pdf_turbo(nk)))
                j += 1

                if j == n or i == top:
                    k += 1
                    gen_err(f"Pętla: {k}")
                    await asyncio.gather(*task)
                    task.clear()

                    proc = int(((i - bot) / (end - bot)) * 100)
                    proc = 1 if proc <= 0 else proc
                    proc = 100 if proc >= 100 else proc

                    self.progress.emit(proc)

                    if self.is_killed:
                        break
                    while self.is_paused:
                        time.sleep(1)
                    # await asyncio.sleep(9 * j)
                    j = 0

            except:
                # gen_err(f"Bład generownaia w pozycji {i}", log=True, write=True)
                logging.info(f"Bład generownaia w pozycji {i}")
                return

            if self.is_killed:
                # gen_err(f"Wygenerowano {proc}% z zadanego zakresu", log=True)
                self.is_killed = False
                break
            while self.is_paused:
                time.sleep(1)
        # self.quit()
        # quit()

        # return
    async def run_by_list_turbo(self, values=[]):

        self.progress.emit(0)

        try:
            if len(values) < 1:
                values = win.get_list()
        except:
            msg.showerror("Zła lista", "Plik wejściowy z listą kw niepoprawny.")
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
                gen_err(f"Pętla: {k}")
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

        gen_err("Wszystkie księgi wieczyste z zadania zostały pobrane")
        msg.showinfo("Zakończono pobieranie", "Wszystkie księgi wieczyste z zadania zostały pobrane")




    def kill(self):
        self.is_killed = True

    def pause(self):
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True


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

        self.setting['Music'] = False # self.exist_setting('Music', True)

        self.save_pdf = self.exist_setting('Save')['save_pdf']
        self.save_html = self.exist_setting('Save')['save_html']
        self.save_txt = self.exist_setting('Save')['save_txt']
        self.save_raport = self.exist_setting('Save')['save_raport']
        self.save_csv = self.exist_setting('Save')['save_csv']
        self.save_json1o = self.exist_setting('Save')['save_json1o']

        self.chSkip.setChecked(self.exist_setting('Skip', True))
        self.chProxy.setChecked(self.exist_setting('Proxy', True))
        self.lineProxy.setText(self.exist_setting('ProxyIP'))


        self.load_format_checks()

        self.lineSign.setText(self.exist_setting('sign'))
        self.lineFloor.setText(self.exist_setting('startnum'))
        self.lineRoof.setText(self.exist_setting('endnum'))


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

        """self.btnRun.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.btnGenSave.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))"""

        self.btnGen.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btnList.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.btnSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btnLog.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.btnErr.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))


        gen_err(err="Uruchomiono program", log=True)

        """ self.music_looper = MusicLooper()

        if self.setting['Music']:
            self.music_looper.start()"""

        self.runner = ListStandard([])
    def connectSignalsSlots(self):

        # self.btnRun.clicked.connect(self.run_by_list)
        self.btnRun.clicked.connect(lambda: self.download_standard())
        # self.btnTurbo.clicked.connect(lambda x: asyncio.run(self.run_by_list_turbo()))
        self.btnTurbo.clicked.connect(lambda: self.download_turbo())

        self.btnList.clicked.connect(self.open_file)
        self.btnOpenDzList.clicked.connect(self.open_file_dz)
        self.btnSave.clicked.connect(self.open_dir)

        # self.btnGen.clicked.connect(self.generate_kws)
        self.btnGen.clicked.connect(lambda: self.generate_standard())
        #self.btnGenSave.clicked.connect(lambda x: self.generate_kws(True))
        self.btnGenSave.clicked.connect(lambda: self.generate_standard(True))
        # self.btnGenSaveTurbo.clicked.connect(lambda x: self.generate_kws(True, True))
        self.btnGenSaveTurbo.clicked.connect(lambda: self.generate_turbo(True))
        # self.btnGenSaveTurbo.clicked.connect(lambda: self.download_turbo(True))

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

        # self.action_muzyka.triggered.connect(lambda x: self.music_switch())

    def music_switch(self):
        """if self.setting['Music']:
            self.music_looper.change()
        else:
            self.music_looper.start()

        self.setting['Music'] = not self.setting['Music']"""
    def download_standard(self):
        self.runner = ListStandard(self.get_list())
        self.runner.progress.connect(self.update_progress)
        self.runner.start()

    def download_turbo(self, generate=False):

        if generate:
            self.runner = ListTurbo([], True)
        else:
            self.runner = ListTurbo(self.get_list())
        self.runner.progress.connect(self.update_progress)
        self.runner.start()

    def generate_standard(self, save=False):
        self.runner = GenerateStandard(save)
        self.runner.progress.connect(self.update_progress)
        self.runner.start()

    def generate_turbo(self, save=True):
        self.runner = GenerateTurbo(save)
        self.runner.progress.connect(self.update_progress)
        self.runner.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def load_format_checks(self):
        self.chPDF.setChecked(self.save_pdf)
        self.chHTML.setChecked(self.save_html)
        self.chTXT.setChecked(self.save_txt)
        self.chJSON.setChecked(self.save_raport)
        self.chCSV.setChecked(self.save_csv)
        self.chJSON1o.setChecked(self.save_json1o)

    def update_values(self):
        self.save_pdf = self.chPDF.isChecked()
        self.save_html = self.chHTML.isChecked()
        self.save_txt = self.chTXT.isChecked()
        self.save_raport = self.chJSON.isChecked()
        self.save_csv = self.chCSV.isChecked()

    def generate_kws(self, download: bool = False, turbo: bool = False):

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


            if turbo:

                asyncio.run(self.run_by_list_turbo(new_kw))

            else:

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

    def open_file_dz(self):

        filetypes_option = (("pliki txt", "*.txt"), ("pliki kw", "*.kw"), ("Wszystkie pliki", "*.*"))
        path = filedialog.askopenfilenames(title="Wybierz plik lub pliki", filetypes=filetypes_option)
        if path is not None:
            path = str(path).replace("('", "")
            path = path.replace("',)", "\t")
            path = path.replace("')", "\t")
            path = path.replace("', '", "\t")
            path = path.strip()


            self.lineDzList.setText(path)

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

                if not img:
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    options.add_experimental_option("prefs", prefs)


                if win.chProxy.isChecked():
                    proxy = win.lineProxy.text()
                    options.add_argument(f"--proxy-server={proxy}")

                """        WINDOW_SIZE = "1920,1080"
                options.add_argument("--headless=new")
                options.add_argument("--window-size=%s" % WINDOW_SIZE)"""

                service = Service()
                browser = webdriver.Chrome(service=service, options=options)

                return browser

            except:

                return get_driver(main_browser="edge")

        case "e": # Edge
            try:

                options = webdriver.EdgeOptions()

                if not img:
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    options.add_experimental_option("prefs", prefs)

                if win.chProxy.isChecked():
                    proxy = win.lineProxy.text()
                    options.add_argument(f"--proxy-server={proxy}")

                service = Service()
                browser = webdriver.Edge(service=service, options=options)
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

                return browser

            except:

                print("Error")
                return get_driver(main_browser="error")
        case "s": # Safari
            ...
        case _:
            return ''

def clear_log():

    with open('log.txt', 'w', encoding="utf-8") as file:
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
        with open("errors.txt", 'a', encoding="utf-8") as file:
            file.write(f"[{ct}]{err}\n")

    if log:
        with open('log.txt', 'a', encoding="utf-8") as file:
            file.write(f"[{ct}]\t{err}\n")

    if rise:
        msg.showerror("Error", err)
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

    with open(win.config, "w", encoding="utf-8") as file:
        json.dump(win.setting, file, ensure_ascii=False)

    sys.exit(app.exec())

def baner_click_event(*arg, **kwargs):
   webbrowser.open_new("https://wykop.pl/tag/ekwpobieraczek")
   # webbrowser.open_new("https://github.com/Rzezimioszek/eKW-pobieracz")

def save_html(browser, path_without_ext):

    path = f"{path_without_ext}.html"

    with open(path, "w", encoding='utf-8') as f:
        f.write(browser.page_source)

    if '1o.html' in path and win.chJSON1o.isChecked():
        eh.page_to_json(path, os.path.dirname(path), win.chXlsx.isChecked())

    print(path, win.chHTML.isChecked())

    if not win.chHTML.isChecked():
        print('-delete')
        os.remove(path)

def save_txt(browser, path_without_ext):

   with open(f"{path_without_ext}.txt", "w", encoding='utf-8') as f:
       f.write(browser.find_element(By.XPATH, "//body").text)

def save_pdf(browser, path_without_ext):
    print('pdf')

    pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": win.pdf_bg})
    # pdf = browser.print_page(background=win.pdf_bg)
    pdf_data = base64.b64decode(pdf["data"])

    single_pdf_path = f"{path_without_ext}.pdf"
    with open(single_pdf_path, "wb") as f:
        f.write(pdf_data)

def save_json(info, path_without_ext):

    with open(f"{path_without_ext}.json", "w", encoding="utf-8") as file:
        json.dump(info, file, ensure_ascii=False, indent=1)

def save_csv(info, path_without_ext):

    path_without_ext = f"{path_without_ext}_raport.csv"
    df = pd.DataFrame(info)
    head = True if not os.path.exists(path_without_ext) else False
    df.to_csv(path_without_ext, mode='a', index=False, header=head, sep=';', encoding="utf-8-sig")

def get_dictionary(browser) -> dict:
    elements = browser.find_elements(By.XPATH, "//div[@class='left']")
    i = 1
    info = {}
    keys = ['Numer', 'Typ', 'Oznaczenie', 'Zapis', 'Zamknięcie', 'Położenie', 'Właściciel']

    for el in elements:
        val = str(el.get_attribute('innerHTML'))
        while "  " in val:
            val = val.replace("  ", " ")
        val = val.replace("\n", "")

        if i > 6:
            if keys[-1] not in info.keys():
                info[keys[-1]] = []

            if "</p>" in val:
                splt = val.split("</p>")
                for spl in splt:
                    spl = spl.replace("<p>", "")
                    spl = spl.replace("</p>", "")
                    spl = spl.strip()
                    if spl != "":
                        info[keys[-1]].append(spl)

        else:
            val = val.replace("<p>", "")
            val = val.replace("</p>", "")
            info[keys[i - 1]] = val.strip()

        i += 1
    return info

def save_kw_to_pdf(value: str):  #

    save_path = win.lineSave.text()
    pdf_bg = win.chBg.isChecked()

    zupelna = False

    to_merge = []
    merge = win.chMerge.isChecked()

    gen_err(f"Wprowadzona wartość: {value}")

    try:
        kw = value.split('/')

        if 2 <= len(kw) < 3:
            value = win.correct_kw_number(kw[0], kw[1])
            kw = value.split('/')
            gen_err(f"Poprawiono cyfrę kontrolną: {value}")


        if win.chSkip.isChecked():

            ext_list = [str(Path(p).stem)[0:16] for p in os.listdir(save_path)]
            if value.replace('/', '.') in ext_list:
                return

        browser = get_driver(win.chImg.isChecked())

        browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

        time.sleep(3)  #

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

        if win.save_raport or win.save_csv:

            info = get_dictionary(browser)

            path_without_ext = f"{save_path}/{value.replace('/', '.')}"
            if win.save_raport:
                save_json(info, path_without_ext)

            if win.save_csv:
                save_csv(info, f"{save_path}/")

        if not win.save_pdf and not win.save_txt and not win.save_html and not win.chJSON1o:
            browser.quit()
            return

        elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
        elem.send_keys(Keys.RETURN)

        ###
    except:
        zupelna = True
        err = f"Treść zwykła wydruku niedostępna dla: {value}"
        gen_err(err)

    try:
        if zupelna:
            if win.chError.isChecked():
                elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                elem.send_keys(Keys.RETURN)
                gen_err("Pobieranie treści zupełnej")
            else:
                err = f"Błąd pobierania treści zupełnej księgi: {value}"
                gen_err(err, write=True)
                browser.quit()
                return
    except:
        err = f"Błąd pobierania księgi: {value}"
        gen_err(err, write=True)
        return

    try:
        i = 1  # dział I-O

        if win.ch1o.isChecked():

            time.sleep(2)  #

            elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
            elem.send_keys(Keys.RETURN)

            path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}o"

            if win.save_html or win.save_json1o or win.chDzList.isChecked():
                save_html(browser, path_without_ext)

                if win.chDzList.isChecked():
                    dzs = eh.dz_from_page(f"{path_without_ext}.html").values()
                    dz = [x['Numer działki'] for x in dzs]
                    wanted = get_wanted_dz()

                    # print([x['Numer działki'] for x in dzs])

                    skip = True
                    for w in wanted:
                        if w in dz:
                            skip = False
                    if skip:
                        # print("Download skiped")
                        browser.quit()
                        return



            if win.save_txt: save_txt(browser, path_without_ext)
            if win.save_pdf:

                save_pdf(browser, path_without_ext)

                if merge:
                    to_merge.append(f"{path_without_ext}.pdf")

        if win.ch1s.isChecked():

            time.sleep(2)  #

            elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
            elem.send_keys(Keys.RETURN)

            path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}s"

            if win.save_html: save_html(browser, path_without_ext)
            if win.save_txt: save_txt(browser, path_without_ext)
            if win.save_pdf:

                save_pdf(browser, path_without_ext)

                if merge:
                    to_merge.append(f"{path_without_ext}.pdf")

        i = 2  # dział II

        if win.ch2.isChecked():

            time.sleep(2)  #

            elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
            elem.send_keys(Keys.RETURN)

            path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}"

            if win.save_html: save_html(browser, path_without_ext)
            if win.save_txt: save_txt(browser, path_without_ext)
            if win.save_pdf:
                save_pdf(browser, path_without_ext)
                if merge:
                    to_merge.append(f"{path_without_ext}.pdf")

        i = 3  # dział III

        if win.ch3.isChecked():

            time.sleep(2)  #

            elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
            elem.send_keys(Keys.RETURN)

            path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}"

            if win.save_html: save_html(browser, path_without_ext)
            if win.save_txt: save_txt(browser, path_without_ext)
            if win.save_pdf:

                save_pdf(browser, path_without_ext)

                if merge:
                    to_merge.append(f"{path_without_ext}.pdf")

        i = 4  # dział IV

        if win.ch4.isChecked():

            time.sleep(2)  #

            elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
            elem.send_keys(Keys.RETURN)

            path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}"

            if win.save_html: save_html(browser, path_without_ext)
            if win.save_txt: save_txt(browser, path_without_ext)
            if win.save_pdf:

                save_pdf(browser, path_without_ext)

                if merge:
                    to_merge.append(f"{path_without_ext}.pdf")

        gen_err(f"Pobrano księgę: {value}")
    except:

        err = f"Błąd pobierania wybranych działów księgi: {value}"
        gen_err(err, write=True)

    try:
        if merge and len(to_merge) > 0:

            gen_err(f"Łączenie pojedynczych działów KW w jeden plik: {value}", log=True)

            out_pdf = pypdf.PdfWriter()
            dst_path = f"{save_path}/{value.replace('/', '.')}.pdf"

            for tm in to_merge:
                src_pdf = pypdf.PdfReader(tm)
                out_pdf.append_pages_from_reader(src_pdf)

            with open(dst_path, "wb") as file:
                out_pdf.write(file)

            gen_err(f"Usuwanie pojedynczych działów KW: {value}", log=True)

            for tm in to_merge:
                os.remove(tm)

    except:
        err = f"Błąd łączenia działów księgi: {value}"
        gen_err(err, write=True)

async def save_kw_to_pdf_turbo(value: str): #

        save_path = win.lineSave.text()

        to_merge = []
        merge = win.chMerge.isChecked()

        zupelna = False

        gen_err(f"Wprowadzona wartość: {value}")

        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = win.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"Poprawiono cyfrę kontrolną: {value}")


            if win.chSkip.isChecked():

                ext_list = [Path(p).stem for p in os.listdir(save_path)]
                if value.replace('/', '.') in ext_list:
                    logging.info(f"Skiped {value}")
                    return

            browser = get_driver(win.chImg.isChecked())

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

            if win.save_raport or win.save_csv:

                info = get_dictionary(browser)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}"
                if win.save_raport:
                    save_json(info, path_without_ext)

                if win.save_csv:
                    save_csv(info, f"{save_path}/")

            if not win.save_pdf and not win.save_txt and not win.save_html and not win.chJSON1o:
                browser.quit()
                return

            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')  # Find the search box
            elem.send_keys(Keys.RETURN)

            ###
        except:
            zupelna = True
            err = f"Treść zwykła wydruku niedostępna dla: {value}"
            gen_err(err)

        try:
            if zupelna:
                if win.chError.isChecked():
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
            browser.quit()
            return

        try:
            i = 1  # dział I-O

            if win.ch1o.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-O"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}o"

                if win.save_html or win.save_json1o or win.chDzList.isChecked():
                    save_html(browser, path_without_ext)

                    if win.chDzList.isChecked():
                        dzs = eh.dz_from_page(f"{path_without_ext}.html").values()
                        dz = [x['Numer działki'] for x in dzs]
                        wanted = get_wanted_dz()

                        # print([x['Numer działki'] for x in dzs])

                        skip = True
                        for w in wanted:
                            if w in dz:
                                skip = False
                        if skip:
                            # print("Download skiped")
                            browser.quit()
                            return

                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:
                    save_pdf(browser, path_without_ext)
                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            if win.ch1s.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział I-Sp"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}s"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:
                    save_pdf(browser, path_without_ext)
                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            i = 2  # dział II

            if win.ch2.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział II"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:
                    save_pdf(browser, path_without_ext)
                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            i = 3  # dział III

            if win.ch3.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział III"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:
                    save_pdf(browser, path_without_ext)
                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            i = 4  # dział IV

            if win.ch4.isChecked():

                await asyncio.sleep(2)

                elem = browser.find_element(By.CSS_SELECTOR, '[value="Dział IV"]')  # Find the search box
                elem.send_keys(Keys.RETURN)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}_{i}"

                if win.save_html: save_html(browser, path_without_ext)
                if win.save_txt: save_txt(browser, path_without_ext)
                if win.save_pdf:
                    save_pdf(browser, path_without_ext)
                    if merge:
                        to_merge.append(f"{path_without_ext}.pdf")

            gen_err(f"Pobrano księgę: {value}")
        except:

            err = f"Błąd pobierania wybranych działów księgi: {value}"
            gen_err(err, write=True)


        try:
            if merge and len(to_merge) > 0:

                await asyncio.sleep(2)

                gen_err(f"Łączenie pojedynczych działów KW w jeden plik: {value}", log=True)

                out_pdf = pypdf.PdfWriter()
                dst_path = f"{save_path}/{value.replace('/', '.')}.pdf"

                for tm in to_merge:
                    src_pdf = pypdf.PdfReader(tm)
                    out_pdf.append_pages_from_reader(src_pdf)

                with open(dst_path, "wb") as file:
                    out_pdf.write(file)

                gen_err(f"Usuwanie pojedynczych działów KW: {value}", log=True)

                for tm in to_merge:
                    os.remove(tm)

        except:
            err = f"Błąd łączenia działów księgi: {value}"
            gen_err(err, write=True)

def get_wanted_dz() -> list:
    path = win.lineDzList.text()

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return [lin.replace("\n", "") for lin in lines]
    else:
        return ['']

def set_fusion():
    app.setStyle('Fusion')

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
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)

    set_fusion()

    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(save_settings)
    # app.setWindowIcon(QIcon(":/main/eKw.jpg"))
    win = Window()
    win.show()
    #asyncio.run(sys.exit(app.exec()))
    sys.exit(app.exec())

