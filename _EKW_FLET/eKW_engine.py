from dataclasses import replace
from idlelib.iomenu import encoding

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

from random import randint
from threading import Event

from eKW_functions import *
from eKW_save import *
from eKW_settings import *

import time as time
import os as os
from pathlib import Path
import pypdf as pypdf
import extract_html as eh

import threading
rep_dict = {"X": "10", "A": "11", "B": "12", "C": "13", "D": "14", "E": "15",
                 "F": "16", "G": "17", "H": "18", "I": "19", "J": "20", "K": "21",
                 "L": "22", "M": "23", "N": "24", "O": "25", "P": "26", "R": "27",
                 "S": "28", "T": "29", "U": "30", "W": "31", "Y": "32", "Z": "33",
                 "0": "0", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9"}

lock = threading.Lock()


def sad_list(parametr: str = ""):
    path = "src/sady.kw"

    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    parametr = parametr.upper()

    for line in lines:
        if parametr in line.upper() or parametr == "":
            yield line.replace("\n", "")

def get_proxy(path):

    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        i = randint(0, len(lines) - 1)

        return lines[i].replace("\n", "")

def save_page(browser, dzial, path_without_ext, i, parms:dict = read_settings()):

    shtml = parms['save_html']
    sjson = parms['save_json']
    sxlsx = parms['save_xlsx']
    stxt = parms['save_txt']
    spdf = parms['save_pdf']

    dz_in_kw = parms['check_dz_in_kw']

    wid = parms['wanted_id']

    page_background = parms['page_background']

    find_wait(browser, f'input[value="{dzial}"]').click()

    path_without_ext = f"{path_without_ext}_{i}"

    if dzial == 'Dział I-O':
        path_without_ext = f"{path_without_ext}o"
    elif dzial == 'Dział I-Sp':
        path_without_ext = f"{path_without_ext}s"

    global lock
    # miejsce na lock

    with lock:

        if dzial == 'Dział I-O':
            if shtml or sjson or dz_in_kw:
                save_html(browser,
                          path_without_ext,
                          sjson,
                          True,
                          sxlsx)

                if dz_in_kw:


                    dzs = eh.dz_from_page(f"{path_without_ext}.html").values()
                    dz = [x['Numer działki'] for x in dzs]
                    wanted = get_wanted_dz(wid)

                    if not shtml:
                        os.remove(f"{path_without_ext}.html")

                    skip = True
                    #print(f'{path_without_ext}', *dz)
                    for w in wanted:
                        #print(f"Wanted: {w}")
                        if w in dz:
                            skip = False
                    if skip:
                        gen_err("Pomijanie pobierania, brak działki w KW")
                        # browser.quit()
                        return False
        else:
            if shtml:
                save_html(browser,
                          path_without_ext,
                          sjson,
                          shtml,
                          sxlsx)

        if stxt: save_txt(browser, path_without_ext)
        if spdf:
            save_pdf(browser, path_without_ext, page_background)
            return f"{path_without_ext}.pdf"


    return None

def save_kw(value: str, flag: int = 0, event=Event().set(), event_kill=Event().set()):  #

    parms = read_settings()

    spdf = parms['save_pdf']
    stxt = parms['save_txt']
    shtml = parms['save_html']
    sjson = parms['save_json']

    report_json = parms['save_report_json']
    report_csv = parms['save_report_csv']

    ae = parms['already_exist']

    d_1o = parms['dzial_1o']
    d_1s = parms['dzial_1s']
    d_2 = parms['dzial_2']
    d_3 = parms['dzial_3']
    d_4 = parms['dzial_4']

    try_zupelna = parms['try_zupelna']

    if not event.is_set():
        event.wait()

    if not event_kill.is_set():
        return


    save_path = parms['save_path']
    pdf_bg = parms['page_background']

    zupelna = False

    to_merge = []
    merge = parms['pdf_merge']

    gen_err(f"{value}\t- Wprowadzona wartość")

    max_retries = 5
    retries = 0
    browser = None
    while retries < max_retries:
        browser = None
        try:
            kw = value.split('/')

            if 2 <= len(kw) < 3:
                value = correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                gen_err(f"{value}\t- Poprawiono cyfrę kontrolną")



            if ae:

                ext_list = [str(Path(p).stem)[0:16] for p in os.listdir(save_path)]
                if value.replace('/', '.') in ext_list:
                    return

            browser = get_driver(str(parms["browser"])[0], img=True)
            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

            time.sleep(1)  # 3 -> 1

            insert_kw_number(browser, kw)

            time.sleep(1)

            if report_json or report_csv:

                info = get_dictionary(browser)

                path_without_ext = f"{save_path}/{value.replace('/', '.')}"
                if report_json:
                    save_json(info, path_without_ext)

                if report_csv:
                    save_csv(info, f"{save_path}/")



            if not spdf and not stxt and not shtml and not sjson:
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

            if try_zupelna:
                elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')  # Find the search box
                elem.send_keys(Keys.RETURN)
                gen_err(f"{value}\t- Pobieranie treści zupełnej")
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


        if d_1o:

            time.sleep(t_s)
            cur_page = save_page(browser, "Dział I-O", path_without_ext, 1, parms)

            if type(cur_page) is bool:
                safe_quit_browser(browser, value)
                return

            to_merge.append(cur_page)

        if d_1s:

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział I-Sp", path_without_ext, 1, parms))

        if d_2:

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział II", path_without_ext, 2, parms))

        if d_3:

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział III", path_without_ext, 3, parms))

        if d_4:

            time.sleep(t_s)
            to_merge.append(save_page(browser, "Dział IV", path_without_ext, 4, parms))

        gen_err(f"{value}\t- Pobrano księgę")
    except Exception as e:

        err = f"{value}\t- Błąd pobierania wybranych działów księgi: {str(e)}"
        gen_err(err, write=True)

        if flag < 3:

            safe_quit_browser(browser, value)

            flag += 1
            gen_err(f"{value}\t- próba pobrania numer {flag + 1}", log=True)
            save_kw(value, flag)


        return

    finally:
        safe_quit_browser(browser)

    try:
        if spdf and merge and len(to_merge) > 0:

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


def correct_kw_number(sad, number):
    sad_value = [rep_dict[s] for s in sad]

    wei = 4 * [1, 3, 7]

    while len(number) < 8:
        number = f"0{number}"

    temp_kw = sad_value + [x for x in number]
    ctlr_dig = 0
    for k in range(len(wei)):
        ctlr_dig += (wei[k] * int(temp_kw[k]))

    ctlr_dig = ctlr_dig % 10

    skw = f"{sad}/{number}/{ctlr_dig}"

    return skw

def get_driver(main_browser = "c", img: bool = True):

    ### Params dict: browser
    stg = read_settings()

    # main_browser = stg['browser']
    use_proxy = stg['use_proxy']
    proxy_value = stg['proxy_value']

    # print(main_browser)

    match main_browser:
        case "c":  # Chrome
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


                if use_proxy:
                    proxy = get_proxy(proxy_value)
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


                if use_proxy:
                    proxy = get_proxy(proxy_value)
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

                if use_proxy:
                    proxy = get_proxy(proxy_value)
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

def safe_quit_browser(browser, value: str = ""):
    """Bezpieczne zamknięcie przeglądarki."""
    if browser:
        try:
            browser.close()
            browser.quit()
        except Exception as e:
            print(f"Błąd podczas zamykania przeglądarki{value}: {e}")


if __name__ == "__main__":
    for i in sad_list("bb"):
        print(i)