from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from datetime import datetime
import logging
logging.basicConfig(format="%(message)s", level=logging.INFO)
from tkinter import messagebox as msg
import os
import webbrowser


def baner_click_event(*arg, **kwargs):
   webbrowser.open_new("https://wykop.pl/tag/ekwpobieraczek")
   # webbrowser.open_new("https://github.com/Rzezimioszek/eKW-pobieracz")

def insert_kw_number(browser, kw):
    """browser.find_element(By.ID, 'kodWydzialuInput').send_keys(kw[0])  # Find the search box
    browser.find_element(By.NAME, 'numerKw').send_keys(kw[1])  # Find the search box
    browser.find_element(By.NAME, 'cyfraKontrolna').send_keys(kw[2])  # Find the search box
    browser.find_element(By.NAME, 'wyszukaj').send_keys(Keys.RETURN)  # Find the search box"""

    retries = 0
    max_retries = 3


    while retries < max_retries:

        # print(f"Current: {retries}")

        try:

            find_wait(browser, "#kodWydzialuInput").send_keys(kw[0])
            find_wait(browser, "#numerKsiegiWieczystej").send_keys(kw[1])
            find_wait(browser, "#cyfraKontrolna").send_keys(kw[2])
            find_wait(browser, "#wyszukaj").click()

            break

        except Exception as e:
            retries += 1
            print(f"***\n{e}")


def find_wait(browser, value: str, by: By = By.CSS_SELECTOR, wait_seconds: int = 60):
    wdw = WebDriverWait(browser, wait_seconds)
    method = expected_conditions.presence_of_element_located
    return wdw.until(method((by, value)))


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


def gen_err(err: str = "Error", rise: bool = False, write=False, log=True):

    ct = datetime.now().strftime('%d.%m.%y %H:%M:%S')
    # print(f"[{ct}]\t{err}")
    logging.info(f"[{ct}]\t{err}")

    if write:
        with open("errors.txt", 'a', encoding="utf-8") as file:
            file.write(f"[{ct}]{err}\n")

    if log:
        with open('log.txt', 'a', encoding="utf-8") as file:
            file.write(f"[{ct}]\t{err}\n")

    if rise:
        msg.showerror("Error", err)

def clear_log():

    with open('log.txt', 'w', encoding="utf-8") as file:
        file.write(f"")

def get_wanted_dz(path) -> list:

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return [lin.replace("\n", "") for lin in lines]
    else:
        return ['']

def open_local_file(file):
    try:
        os.startfile(file)
    except:
        msg.showerror("Brak pliku", "Plik nieistnieje lub brak uprawnień do dostępu.")

def set_theme(light: bool):

    if light:
        value = 'light'
    else:
        value = 'dark'

    with open('theme.ekw', "w", encoding='utf-8') as file:
        file.write(value)


def get_theme():

    path = 'theme.ekw'
    if os.path.exists(path):
        with open('theme.ekw', "r", encoding='utf-8') as file:
            lines = file.readlines()
        if "dark" in lines:
            return False
        else:
            return True
    return False




if __name__ == "__main__":
    ...