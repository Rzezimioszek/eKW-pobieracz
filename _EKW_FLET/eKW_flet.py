from idlelib.iomenu import encoding
from importlib.resources import contents

import logging
import flet as ft
import concurrent.futures
import threading
from threading import Event
import webbrowser

from scipy.constants import value

from eKW_engine import *
from eKW_functions import *
from eKW_save import *
from eKW_settings import *
from eKW_generator import *
from eKW_dialogs import *


import pyperclip as pp

logging.basicConfig(format="%(message)s", level=logging.INFO)


class FileItem:
    """
    Element wejściowy taska
    """
    def __init__(self, value: dict):
        self.name = value['name']
        self.path = value['path']


class LinkButton(ft.OutlinedButton):
    """
    OutlinedButton, ale z moimi ustawienaimi
    """
    def __init__(self, label, url):
        super().__init__()

        self.col = {"xs": 12, "sm": 6, "md": 3, "xl": 3}
        self.text = label
        self.expand = 1
        self.on_click = lambda x: webbrowser.open_new(url)


class EkwAbout(ft.Container):
    """
    Karta o programie
    """
    def __init__(self, title):
        super().__init__()

        self.bgcolor = ft.colors.WHITE12
        self.border_radius = ft.border_radius.all(5)
        self.padding = 5
        self.expand = 1

        ekw_version = ft.Text(f"Program: {title}", col=12)

        # Linki

        links = [
                ft.Text(f"Linki:", col=12, italic=True),
                LinkButton("Github", "https://github.com/Rzezimioszek/eKW-pobieracz"),
                LinkButton("Wykop", "https://wykop.pl/tag/ekwpobieraczek"),
                LinkButton("QGIS Plugins", "https://plugins.qgis.org/plugins/author/%C5%81ukasz%20%C5%9Awi%C4%85tek/"),
                LinkButton("Donacje", "https://www.paypal.com/donate/?hosted_button_id=2AFDC9PRMGN3Q"),
                LinkButton("Kontakt mailowy", f"mailto:{'lukasz.swiatek1996@gmail.com'}?subject={'eKW-pobieraczek'}&body={''}"),
                LinkButton("Dokumentacja Flet",f"https://flet.dev/"),
            ]

        yt = LinkButton("Tutorial YT", "https://www.youtube.com/")
        yt.visible = False

        col = {"xs": 12, "sm": 6, "md": 3, "xl": 3}  # zachowanie kolumny w rzędzie
        pdf = ft.ElevatedButton("Instrukcja", col=col,
                                on_click=lambda x: open_local_file('eKW pobieraczek 2 - instrukcja.pdf'))

        rrow = ft.ResponsiveRow(controls=[ekw_version, *links, yt, pdf])

        self.content = ft.Column(controls=[rrow],
                                 scroll=ft.ScrollMode.ALWAYS, expand=1,)


class EkwSettings(ft.Container):
    """
    Karta ustawień programu (do podziału na wygląd, zachowanie przy pobieraniu
    """
    def __init__(self, theme_on_change, light_on_change):
        super().__init__()

        self.bgcolor = ft.colors.WHITE12
        self.border_radius = ft.border_radius.all(5)
        self.padding = 5
        self.expand = 1
        col = {"xs": 12, "sm": 12, "md": 6, "xl": 6}
        stg = read_settings()

        def dual_color(x):
            theme_on_change(x.data)
            self.dump_settings()
        def dual_theme(x):
            light_on_change(x.data)
            self.dump_settings()

        self.color_drop = ft.Dropdown(
            value=stg['color'],
            label="Kolor",
            padding=5,
            options=[
                ft.dropdown.Option("Red"),
                ft.dropdown.Option("Green"),
                ft.dropdown.Option("Blue"),
                ft.dropdown.Option("Yellow"),
                ft.dropdown.Option("Purple"),
            ],
            on_change=lambda x: dual_color(x),
            expand=1
        )

        self.theme_drop = ft.Dropdown(
            value=stg['theme'],
            label="Motyw",
            padding=5,
            options=[
                ft.dropdown.Option("System"),
                ft.dropdown.Option("Jasny"),
                ft.dropdown.Option("Ciemny"),
            ],
            on_change=lambda x: dual_theme(x),
            expand=1
        )

        theme_on_change(self.color_drop.value)
        light_on_change(self.theme_drop.value)

        theme_color_drop = ft.Column(col=col, controls=[self.color_drop])
        theme_light_drop = ft.Column(col=col, controls=[self.theme_drop])

        self.engine_drop = ft.Dropdown(
            value=stg['browser'],
            label="Przeglądarka",
            padding=5,
            options=[
                ft.dropdown.Option("chrome"),
                ft.dropdown.Option("edge"),
                ft.dropdown.Option("firefox"),
            ],
            on_change=lambda _: self.dump_settings(),
            expand=1
        )

        engine_column = ft.Column(col=12, controls=[self.engine_drop])

        def correct_caption(v) -> str:
            caption = f"Liczba wątków [{v:0.0f}]"
            while len(caption) < 19:
                caption = caption[:15] + "0" + caption[15:]
            return caption


        def slider_changed(e):
            t.value = correct_caption(e.control.value)
            self.update()

        def slider_add(i: int = 1):

            value = self.slider.value + i

            if self.slider.min <= value <= self.slider.max:
                self.slider.value = value
            t.value = correct_caption(self.slider.value)
            self.update()

        t = ft.Text(correct_caption(stg['threads']))
        slider_m = ft.IconButton(icon=ft.icons.EXPOSURE_MINUS_1, on_click=lambda x: slider_add(-1))
        slider_p = ft.IconButton(icon=ft.icons.EXPOSURE_PLUS_1, on_click=lambda x: slider_add(+1))

        self.slider = ft.Slider(value=stg['threads'], expand=1, on_change=slider_changed,
                                on_change_end=lambda _: self.dump_settings(),
                                round=0, min=1, max=50, divisions=49, label="{value}")

        self.threads_slider = ft.Column(col=12,controls=[
            ft.Row(controls=[t, slider_m, slider_p]), self.slider])

        self.spdf = ft.Switch(label="PDF", value=stg['save_pdf'],
                                                             on_change=lambda _: self.dump_settings())
        self.shtml = ft.Switch(label="HTML", value=stg['save_html'],
                                                             on_change=lambda _: self.dump_settings())
        self.stxt = ft.Switch(label="TXT", value=stg['save_txt'],
                                                             on_change=lambda _: self.dump_settings())
        self.sjsonR = ft.Switch(label="JSON (wyszukiwanie)", value=stg['save_report_json'],
                                                             on_change=lambda _: self.dump_settings())
        self.scsv = ft.Switch(label="CSV", value=stg['save_report_csv'],
                                                             on_change=lambda _: self.dump_settings())
        self.sjson = ft.Switch(label="JSON (działy)", value=stg['save_json'],
                                                             on_change=lambda _: self.dump_settings())
        self.sxlsx = ft.Switch(label="XLSX", value=stg['save_xlsx'],
                                                             on_change=lambda _: self.dump_settings())

        colf = {"xs": 6, "sm": 4, "md": 4, "xl": 3}
        save_formats = [ft.Text("Format zapisu", italic=True),
                        ft.Column(col=colf, controls=[self.spdf]),
                        ft.Column(col=colf, controls=[self.shtml]),
                        ft.Column(col=colf, controls=[self.stxt]),
                        ft.Column(col=colf, controls=[self.sjsonR]),
                        ft.Column(col=colf, controls=[self.scsv]),
                        ft.Column(col=colf, controls=[self.sjson]),
                        ft.Column(col=colf, controls=[self.sxlsx])
                        ]

        self.d_1o = ft.Switch(label="Dział I-O", value=stg['dzial_1o'],
                                                             on_change=lambda _: self.dump_settings())
        self.d_1s = ft.Switch(label="Dział I-S", value=stg['dzial_1s'],
                                                             on_change=lambda _: self.dump_settings())
        self.d_2 = ft.Switch(label="Dział II", value=stg['dzial_2'],
                                                             on_change=lambda _: self.dump_settings())
        self.d_3 = ft.Switch(label="Dział III", value=stg['dzial_3'],
                                                             on_change=lambda _: self.dump_settings())
        self.d_4 = ft.Switch(label="Dział IV", value=stg['dzial_4'],
                                                             on_change=lambda _: self.dump_settings())

        save_dzial = [ft.Text("Wybrane działy", italic=True),
                        ft.Column(col=colf, controls=[self.d_1o]),
                        ft.Column(col=colf, controls=[self.d_1s]),
                        ft.Column(col=colf, controls=[self.d_2]),
                        ft.Column(col=colf, controls=[self.d_3]),
                        ft.Column(col=colf, controls=[self.d_4])
                        ]

        self.ae = ft.Switch(label="Pomiń pobrane", value=stg['already_exist'],
                                                             on_change=lambda _: self.dump_settings())

        self.page_bg = ft.Switch(label="Zapis z tłem", value=stg['page_background'],
                                                             on_change=lambda _: self.dump_settings())

        self.page_img = ft.Switch(label="Ładuj obrazy", value=stg['page_image'],
                                                             on_change=lambda _: self.dump_settings())

        self.pdf_merge = ft.Switch(label="Scal PDFy z działów", value=stg['pdf_merge'],
                                                             on_change=lambda _: self.dump_settings())

        self.try_zupelna = ft.Switch(label="Pobieraj treść zupełną jeśli brak zwykłej", value=stg['try_zupelna'],
                                                             on_change=lambda _: self.dump_settings())

        self.proxy = ft.Switch(label="Używaj proxy", value=stg['use_proxy'],
                                                             on_change=lambda _: self.dump_settings())

        self.edit_proxy = ft.ElevatedButton(text="Edytuj listę proxy", on_click=lambda x: os.startfile(os.path.dirname(__file__) + stg['proxy_value']))

        self.dz_in_kw = ft.Switch(label="Pobieraj tylko gdy zawiera działki", value=stg['check_dz_in_kw'],
                                                             on_change=lambda _: self.dump_settings())

        # stg['wanted_id'] # path
        self.wanted_id = ft.TextField(label="Szukane działki (ścieżka do listy)", value=stg['wanted_id'],
                                                             on_change=lambda _: self.dump_settings())

        def set_wanted_list():
            self.wanted_id.value = open_file()
            self.dump_settings()
            self.update()

        wanted_button = ft.IconButton(icon=ft.icons.FOLDER_OPEN, tooltip="Wybierz listę działek", expand=1,
                                          on_click=lambda x: set_wanted_list())

        colf = {"xs": 6, "sm": 4, "md": 4, "xl": 2}


        other_parms = [ft.Text("Pozostałe ustawienia", italic=True),
                        ft.Column(col=colf, controls=[self.ae]),
                        ft.Column(col=colf, controls=[self.page_bg]),
                        ft.Column(col=colf, controls=[self.page_img]),
                        ft.Column(col=colf, controls=[self.pdf_merge]),
                        ft.Column(col=12, controls=[self.try_zupelna]),
                        #ft.Column(col=6, controls=[self.proxy]),
                        #ft.Column(col=6, controls=[self.edit_proxy]),
                        ft.Column(col=12, controls=[self.dz_in_kw]),
                        ft.Column(col={"xs": 10, "sm": 11, "md": 11, "xl": 11}, controls=[self.wanted_id]),
                        ft.Column(col={"xs": 2, "sm": 1, "md": 1, "xl": 1},
                                  controls=[ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[wanted_button])]),
                      ]

        self.label_path = ft.TextField(label="Ścieżka zapisu", value=stg['save_path'],
                                       expand=1)
        btn_open_path = ft.IconButton(icon=ft.icons.FOLDER_OPEN, tooltip="Wybierz ścieżkę zapisu", expand=1,
                                      on_click=lambda x: file_picker.get_directory_path())
        file_picker = ft.FilePicker(on_result=self.on_dialog_result)

        save_path = [
                        ft.Column(col={"xs": 10, "sm": 11, "md": 11, "xl": 11}, controls=[self.label_path]),
                        ft.Column(col={"xs": 2, "sm": 1, "md": 1, "xl": 1},
                                  controls=[ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[btn_open_path])]),
                        file_picker
                    ]

        theme_list = [theme_color_drop, theme_light_drop]

        row_stg = ft.ResponsiveRow(controls=[
                                            *save_path,
                                            self.threads_slider,
                                            engine_column,
                                            *save_formats,
                                            *save_dzial,
                                            *other_parms,
                                            *theme_list],
                              alignment=ft.MainAxisAlignment.START)

        self.content = ft.Column(controls=[ft.Text("Ustawienia:"), row_stg],
                                 scroll=ft.ScrollMode.ALWAYS, expand=1,)


    def dump_settings(self):
        stg = dict()
        stg['color'] = self.color_drop.value
        stg['theme'] = self.theme_drop.value

        stg['threads'] = int(self.slider.value)
        stg['save_path'] = self.label_path.value
        stg['already_exist'] = self.ae.value
        stg['page_background'] = self.page_bg.value
        stg['page_image'] = self.page_img.value
        stg['pdf_merge'] = self.pdf_merge.value
        stg['browser'] = str(self.engine_drop.value)
        stg['use_proxy'] = self.proxy.value
        stg['proxy_value'] = "/src/proxy.txt"
        stg['try_zupelna'] = self.try_zupelna.value
        stg['check_dz_in_kw'] = self.dz_in_kw.value
        stg['wanted_id'] = self.wanted_id.value
        stg['save_report_json'] = self.sjsonR.value
        stg['save_report_csv'] = self.scsv.value
        stg['save_pdf'] = self.spdf.value
        stg['save_txt'] = self.stxt.value
        stg['save_html'] = self.shtml.value
        stg['save_json'] = self.sjson.value
        stg['save_xlsx'] = self.sxlsx.value
        stg['dzial_1o'] = self.d_1o.value
        stg['dzial_1s'] = self.d_1s.value
        stg['dzial_2'] = self.d_2.value
        stg['dzial_3'] = self.d_3.value
        stg['dzial_4'] = self.d_4.value

        write_settings(stg)

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        try:
            print("Selected path:", e.path)
            self.label_path.value = e.path
            self.update()
        except TypeError:
            print("File not selected")
        finally:
            self.dump_settings()


class Task(ft.Container):
    def __init__(self, value, task_delete, ttask="list", genval = ""):
        super().__init__()

        self.event = Event()
        self.event_kill = Event()
        self.ttask = ttask
        self.completed = False
        self.value = value
        self.stop = False
        self.pause = False
        self.task_delete = task_delete
        self.border = ft.border.all(1)
        self.bgcolor = ft.colors.WHITE10
        self.border_radius = ft.border_radius.all(5)
        self.padding = 5
        self.file_name = ""

        self.pb = ft.ProgressBar(bgcolor="#eeeeee", expand=1, value=0, bar_height=6,
                                 border_radius=ft.border_radius.all(5))


        def generator_filerow():
            temp = f"Zakres: {self.cbot.value} - {self.ctop.value}"
            self.file_name = temp
            self.value.name = temp
            self.file_row.value = temp
            self.update()

        col = {"xs": 12, "sm": 6, "md": 6, "xl": 4}
        colsub = {"xs": 12, "sm": 6, "md": 6, "xl": 6}

        singiel_digit_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9]?$", replacement_string="")
        digit_filter = ft.InputFilter(allow=True, regex_string=r"^([0-9]{0,8})$",
                                                             replacement_string="")
        sad_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9A-Za-z]{0,4}$",
                                                             replacement_string="")
        self.sad2 = ft.TextField(label="Oznaczenie sądu", hint_text="np. BB1B", col=12,
                                    input_filter=sad_filter)
        self.cbot = ft.TextField(label="Start", hint_text="00000001", col=colsub,
                                 on_change=lambda x: generator_filerow(),
                                    input_filter=digit_filter)
        self.ctop = ft.TextField(label="Koniec", hint_text="99999999", col=colsub,
                                 on_change=lambda x: generator_filerow(),
                                    input_filter=digit_filter)
        self.last = ft.TextField(label="Ostatnia cyfra", hint_text="0", col=colsub,
                                    input_filter=singiel_digit_filter)
        self.control = ft.TextField(label="Cyfra kontrolna", hint_text="0", col=colsub,
                                    input_filter=singiel_digit_filter)

        def close_anchor(e):
            text = f"{e.control.data}"
            self.sad.close_view(text.split("\t")[0])

        def handle_change(e):

            lv.controls.clear()
            lv.controls = [ft.ListTile(title=ft.Text(f"{i.split('\t')[0]}"), on_click=close_anchor, data=i,
                                       subtitle=ft.Text(f"{i.split('\t')[1]}")) for i in sad_list(str(e.data))]
            self.update()

        def handle_tap(e):
            self.sad.open_view()

        def handle_submit(e):
            print(f"handle_submit e.data: {e.data}")

        lv = ft.ListView(clip_behavior=ft.ClipBehavior.ANTI_ALIAS)

        lv.controls = [ft.ListTile(title=ft.Text(f"{i.split('\t')[0]}"), on_click=close_anchor, data=i,
                                   subtitle=ft.Text(f"{i.split('\t')[1]}")) for i in sad_list()]

        self.sad = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.colors.AMBER,
            bar_hint_text="Wybierz oznaczenie sądu",
            view_hint_text="Wybierz sąd z dostępnych",
            on_change=handle_change,
            on_tap=handle_tap,
            on_submit=handle_submit,
            controls=[
                lv
            ],)

        if type(genval) != str:
            self.sad.value = genval['sad']
            self.cbot.value  = genval['cbot']
            self.ctop.value  = genval['ctop']
            self.last.value  = genval['last']
            self.control.value  = genval['control']


        self.subrow = ft.ResponsiveRow(alignment=ft.MainAxisAlignment.CENTER,
                               controls=[
                                   ft.Text("Zakres", italic=True, col=12),
                                   self.sad, self.cbot, self.ctop
                               ])

        self.subrow2 = ft.ResponsiveRow(alignment=ft.MainAxisAlignment.CENTER,
                               controls=[
                                   ft.Text("Parametry", italic=True, col=12),
                                   self.last, self.control
                               ])

        self.subrow.visible = False
        self.subrow2.visible = False

        generator_buttons = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                    ft.IconButton(ft.icons.EDIT, tooltip="Zakres",
                                                  on_click=lambda x: self.show_hide_gen()),
                                    ft.IconButton(ft.icons.LIST, tooltip="Parametry",
                                                  on_click=lambda x: self.show_hide_parms()),
                               ])

        self.generator_row = ft.Column(alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=5,
                               controls=[self.subrow, self.subrow2])

        file_picker = ft.FilePicker(on_result=lambda x: self.change_file(x))

        list_buttons = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                    ft.IconButton(ft.icons.EDIT, tooltip="Zmiana pliku",
                                                 on_click=lambda x: file_picker.pick_files(allow_multiple=False)),
                                    file_picker,
                                    ft.IconButton(ft.icons.LIST, tooltip="Parametry",
                                                  on_click=lambda x: self.show_hide_gen()),
                                    ft.IconButton(ft.icons.PASTE, tooltip="Wklej ze schowka",
                                                  on_click=lambda x: self.list_from_clipboard())
                               ])

        self.btn_play = ft.IconButton(
                icon=ft.icons.PLAY_ARROW,
                tooltip="Rozpocznij pobieranie",
                on_click=lambda _: self.download_list(self.value.path))

        self.btn_play_gen = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            tooltip="Generowanie i pobieranie",
            on_click=lambda _: self.download_generator(self.value.path))

        self.btn_gen_gen = ft.IconButton(
            icon=ft.icons.PLAY_ARROW_OUTLINED,
            tooltip="Generowanie do pliku txt",
            on_click=lambda _: self.download_generator(self.value.path, True))

        btn_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=[generator_buttons, list_buttons,
            self.btn_play, self.btn_play_gen, self.btn_gen_gen,
            ft.IconButton(
                icon=ft.icons.PAUSE,
                tooltip="Pauza",
                on_click=self.pause_clicked(),
            ),
            ft.IconButton(
                icon=ft.icons.STOP,
                tooltip="Zatrzymaj pobieranie",
                on_click=self.stop_clicked(),
            ),
            ft.IconButton(
                ft.icons.DELETE_OUTLINE,
                tooltip="Usuń",
                on_click=self.delete_clicked)
        ])

        self.file_row = ft.Text(f"{self.file_name}")

        if ttask == "list" or ttask == "clip":

            self.file_name = value.name
            self.file_row = ft.Text(f"{self.file_name}")

            if ttask == "list":
                kw_count = self.count_kw(value.path)
                self.kw_count_text = ft.Text(f"Ksiąg na liście: {kw_count}", italic=True)
            else:
                self.kw_count_text = ft.Text(f"Ksiąg na liście: 0", italic=True)
                self.list_from_clipboard(False)


            title_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                               controls=[
                                   ft.Text("Pobieranie z listy", italic=True),
                                   self.kw_count_text

                               ])
            self.file_row.visible = True
            self.generator_row.visible = False
            generator_buttons.visible = False
            list_buttons.visible = True
            self.btn_play.visible = True
            self.btn_play_gen.visible = False
            self.btn_gen_gen.visible = False

        else:

            self.file_name = self.value.name
            self.file_row = ft.Text(f"{self.file_name}")

            self.kw_count_text = ft.Text(f"", italic=True)

            title_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                               controls=[
                                   ft.Text("Generowanie listy", italic=True),
                                   self.kw_count_text

                               ])
            self.file_row.visible = True
            self.generator_row.visible = True
            generator_buttons.visible = True
            list_buttons.visible = False
            self.btn_play.visible = False
            self.btn_play_gen.visible = True
            self.btn_gen_gen.visible = True

        self.status = ft.Text("Zadanie gotowe do rozpoczecia", italic=True)

        self.display_view = [
                        title_row,
                        self.file_row,
                        self.generator_row,
                        btn_row,
                        self.status,
                        self.pb]

        self.col = col

        self.content = ft.Column(controls=[*self.display_view], alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=5)


    def list_from_clipboard(self, update: bool = True):


        cb = pp.paste()

        # print(type(cb))

        value = {
            'path': "src/temp_list.txt",
            'name': "Lista wczytana ze schowka"
        }

        with open(value['path'], "w", encoding="utf-8") as file:
            file.write(cb.replace("\n", ""))

        value = FileItem(value)

        self.value = value
        self.file_row.value = "Lista wczytana ze schowka"
        kw_count = self.count_kw(self.value.path)
        self.kw_count_text.value = f"Ksiąg na liście: {kw_count}"
        if update:
            self.update()


    def change_file(self, e: ft.FilePickerResultEvent):

        try:
            self.value = e.files[0]
            self.file_row.value = e.files[0].name
            kw_count = self.count_kw(self.value.path)
            self.kw_count_text.value = f"Ksiąg na liście: {kw_count}"
            self.update()
        except TypeError:
            gen_err("Nie wybrano poprawnego pliku")

    def show_hide_gen(self):
        self.subrow.visible = not self.subrow.visible
        self.update()

    def show_hide_parms(self):
        self.subrow2.visible = not self.subrow2.visible
        self.update()


    def stop_clicked(self):
        self.stop = not self.stop

        if self.stop:
            self.event_kill.clear()
        else:
            self.event_kill.set()

    def pause_clicked(self):

        self.pause = not self.pause

        if self.pause:
            self.event.clear()
        else:
            self.event.set()


    def edit_clicked(self, e):

        clrs = [ft.colors.WHITE, ft.colors.BLACK]

        self.border = ft.border.all(2, ft.colors.BLACK)
        self.update()

        for i in range(0, 101):
            self.pb.value = i * 0.01
            time.sleep(0.1)
            self.border = ft.border.all(2, clrs[i % 2])
            self.update()

        self.border = ft.border.all(1, ft.colors.GREEN)
        self.update()


    def save_clicked(self, e):
        self.update()

    def delete_clicked(self, e):
        self.task_delete(self)

    def count_kw(self, path: str) -> int:
        result = 0
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
                result = len(lines)
        except Exception as ex:
            print(ex)
        finally:
            return result

    def download_list(self, path: str):

        values = []

        self.event.set()
        self.event_kill.set()
        self.pb.value = None
        self.status.value = f"Rozpoczęto pobieranie"
        self.update()

        with open(path, "r", encoding="utf-8") as file:
            values = file.readlines()

        params = read_settings()
        workers = params['threads']

        self.p = 0
        self.count = len(values)

        def progress_indicator(task):
            self.p += 1
            progres = self.p / self.count
            self.pb.value = progres
            self.status.value = f"Przetworzono: {self.p}/{self.count}"
            self.update()



        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            tasks = [
                executor.submit(save_kw, value.replace("\n", ""),
                                event=self.event, event_kill=self.event_kill)
                for value in values]

            for task in tasks:
                task.add_done_callback(progress_indicator)

            concurrent.futures.wait(tasks)


        # self.pb.value = 100
        self.status.value = f"Zakończono pobieranie"
        self.update()
        gen_err("Zakończono zadanie")

    def download_generator(self, path: str, only_generate=False):

        self.event.set()
        self.event_kill.set()
        self.pb.value = None

        params = read_settings()
        workers = params['threads']

        if not self.last.value.isdecimal():
            last = -1
        else:
            last = int(self.last.value)

        if not self.control.value.isdecimal():
            control = -1
        else:
            control = int(self.control.value)


        try:
            sad = str(self.sad.value).upper()
            bot = int(self.cbot.value)
            top = int(self.ctop.value)
        except ValueError as e:
            gen_err(str(e))


        if (len(sad) < 4) or (bot < 1) or (top > 99999999):
            return


        self.p = 0
        self.count = top - bot

        if self.count < 0:
            self.count = - self.count

        self.kw_count_text.value = f"Zakres: {self.count}"

        if only_generate:

            spath = save_file()

            if spath == ".txt":
                self.status.value = f"Nie wybrano miejsca zapisu"
                self.pb.value = 0
                self.update()
                return

            with open(spath, "w") as file:
                file.write(f"")

            self.status.value = f"Generowanie listy"
            self.update()

            for value in kw_from_range(sad, bot, top, last, control):
                #print(value)
                with open(spath, "a") as file:
                    file.write(f"{value}\n")

            self.pb.value = 0
            self.status.value = f"Wygenerowano listę"
            self.update()

            return

        self.status.value = f"Rozpoczęto pobieranie"
        self.update()




        def progress_indicator(task):
            self.p += 1
            # progres = self.p / self.count
            # self.pb.value = progres
            self.status.value = f"Przetworzono: {self.p}/{self.count}"
            self.update()

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:

            tasks = [executor.submit(save_kw, value, event=self.event, event_kill=self.event_kill) for value in
                     kw_from_range(sad, bot, top, last, control)]

            for task in tasks:
                task.add_done_callback(progress_indicator)

            concurrent.futures.wait(tasks)




        self.pb.value = 100
        self.status.value = f"Zakończono pobieranie"
        self.update()
        gen_err("Zakończono zadanie")


class EkwTabDownload(ft.Container):
    """
    Karta pobierania
    """
    def __init__(self, page):
        super().__init__()



        self.instance = None
        # self.tasks = ft.Column(expand=1)
        self.tasks = ft.ResponsiveRow()
        self.expand = 1

        def add_other(ttask):
            try:

                self.tasks.controls.append(Task(FileItem({"name": f"{ttask}", "path": "src/temp_list.txt"}),
                                                self.task_delete, ttask))
                self.update()
            except TypeError:
                print("File not selected")
            finally:
                page.close(bs)


        bs = ft.BottomSheet(
            content=ft.Container(
                padding=5,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Row(controls=[ft.ElevatedButton(text="Lista z pliku txt", icon=ft.icons.LIST, expand=1,
                                          on_click=lambda x: file_picker.pick_files(allow_multiple=False))]),
                        ft.Row(controls=[ft.ElevatedButton(text="Lista ze schowka", icon=ft.icons.PASTE, expand=1,
                                                           on_click=lambda x: add_other('clip'))]),
                        ft.Row(controls=[ft.ElevatedButton(text="Generator", icon=ft.icons.ROCKET, expand=1,
                                          on_click=lambda x: add_other('generator'))]),
                        ft.Row(controls=[ft.ElevatedButton("Anuluj", expand=1, on_click=lambda _: page.close(bs))]),
                    ],
                ),
            ),
        )

        def on_dialog_result(e: ft.FilePickerResultEvent):
            try:
                print("Selected file:", e.files[0])

                self.tasks.controls.append(Task(e.files[0], self.task_delete))
                self.update()
            except TypeError:
                print("File not selected")
            finally:
                page.close(bs)



        file_picker = ft.FilePicker(on_result=on_dialog_result)

        self.bgcolor = ft.colors.WHITE10
        self.border_radius = ft.border_radius.all(5)
        self.padding = 5


        add_task_button = ft.FloatingActionButton(icon=ft.icons.ADD, tooltip="Dodaj nowe zadanie",
                                                   on_click=lambda x: page.open(bs))

        self.content = ft.Column(
            controls=[
                    ft.Text("Lista zadań:"),
                    ft.Column(
                        scroll=ft.ScrollMode.ALWAYS,
                        expand=1,
                    controls=[self.tasks],
                    alignment=ft.MainAxisAlignment.CENTER),
                file_picker,
                ft.Row(controls=[add_task_button], alignment=ft.MainAxisAlignment.CENTER),
                ],
            )

        self.load_unfinished_tasks()

    def load_unfinished_tasks(self):
        un_tasks = read_unfinished_tasks()

        if len(un_tasks) < 1:
            return

        for ut in un_tasks.values():
            self.tasks.controls.append(Task(FileItem(ut['value']), self.task_delete, ut['ttask'], ut['genval']))

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()


def main(page: ft.Page):
    """
    Głowne okno programu
    """
    page.title = "eKW - Pobieraczek 2.0"

    clear_log()
    gen_err(f"Start programu:\t{page.title}")

    # Ustawienia rozmaru okna startowego
    w, h = 450, 700
    page.window.width = w
    page.window.height = h
    page.window.min_width = w
    page.window.min_height = h

    page.window.resizable = True  # Zezwolenie na zmianę wielkości okna
    page.adaptive = True  # Ustawienia adaptacyjne kontrolek, tak na przyszłość

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    # defy idące do wnętrza kontrolek
    def theme_on_change(e):
        page.theme = ft.theme.Theme(color_scheme_seed=e.lower())
        page.update()

    def light_on_change(e):
        if str(e) == "Jasny":
            page.theme_mode = ft.ThemeMode.LIGHT
        elif str(e) == "System":
            page.theme_mode = ft.ThemeMode.SYSTEM
        else:
            page.theme_mode = ft.ThemeMode.DARK
        page.update()

    # Inicjalizacja kart
    tab_download = EkwTabDownload(page)
    tab_download.visible = True

    gen_err("Wczytano karte:\tPobieranie")

    tab_settings = EkwSettings(theme_on_change=theme_on_change, light_on_change=light_on_change)
    tab_settings.visible = False

    gen_err("Wczytano karte:\tUstawienia")

    tab_about = EkwAbout(page.title)
    tab_about.visible = False

    gen_err("Wczytano karte:\tO programie")

    page.add(tab_download, tab_settings, tab_about)

    def change_tab(e):
        idx = e.control.selected_index

        tab_download.visible = True if idx == 0 else False
        tab_settings.visible = True if idx == 1 else False
        tab_about.visible = True if idx == 2 else False

        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.DOWNLOAD_OUTLINED, selected_icon=ft.icons.DOWNLOAD, label="Pobieranie"),
            ft.NavigationBarDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="Ustawienia"),
            ft.NavigationBarDestination(icon=ft.icons.HELP_OUTLINE, selected_icon=ft.icons.HELP, label="O programie"),
        ],
        on_change=change_tab,
    )

    def on_close_event(e):
        if e.data == "close":
            # print("Saving unfinished tasks...")
            gen_err(f"Zamykanie programu z zapisem zadań na później")
            un_tasks = dict()
            i = 0
            for tt in tab_download.tasks.controls:
                un_tasks[i] = {"ttask": tt.ttask,
                               "value": {"name": tt.value.name, "path": tt.value.path},
                               "genval": {"sad": tt.sad.value,
                                          "cbot": tt.cbot.value,
                                          "ctop": tt.ctop.value,
                                          "last": tt.last.value,
                                          "control": tt.control.value}
                               }
                i += 1

            # print(*un_tasks.values())
            gen_err(f"Zapisano zadania na później:\t{i}")
            write_unfinished_tasks(un_tasks)
            # print("...tasks saved.")

            page.window.prevent_close = False
            page.window.on_event = None
            page.update()
            page.window.close()

    page.window.prevent_close = True
    page.window.on_event = lambda e: on_close_event(e)

    """
    Niewykorszytane opcje do dodania pózniej 
    jako opcje nowej karty ustawień programu 
    wydzielonej z ustawień
    """
    # page.window.opacity = 0.9
    # page.window.skip_task_bar = True
    # page.window.always_on_top = True

    page.update()

    gen_err("Wczytano wszystkie kontrolki UI")



if __name__ == "__main__":
    # main()
    ekw = ft.app(main)