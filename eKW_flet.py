import flet as ft



class EkwSettings(ft.Container):
    def __init__(self, theme_on_change, light_on_change):
        super().__init__()

        theme_on_change

        self.bgcolor = ft.colors.WHITE12
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        # Theme

        theme_color_drop = ft.Dropdown(
            value = "Red",
            label="Kolor",
            options=[
                ft.dropdown.Option("Red"),
                ft.dropdown.Option("Green"),
                ft.dropdown.Option("Blue"),
                ft.dropdown.Option("Yellow"),
                ft.dropdown.Option("Purple"),
            ],
            on_change=theme_on_change,
            expand=1
        )

        theme_light_drop = ft.Dropdown(
            value = "Light",
            label="Oświetlenie",
            options=[
                ft.dropdown.Option("Light"),
                ft.dropdown.Option("Dark"),
            ],
            on_change=light_on_change,
            expand=1
        )

        row_theme = ft.Row(controls=[theme_color_drop, theme_light_drop],
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Save paths

        label = ft.Text("<ścieżka zapisu>", text_align=ft.TextAlign.CENTER, expand=1)
        result = ft.TextField(value="abc", expand=2, height=40, border_radius=ft.border_radius.all(20), text_size=12)
        btn_save_path = ft.ElevatedButton(text="Wybierz", on_click=lambda x: pp.copy(self.result.value), expand=1)
        btn_paste_path = ft.ElevatedButton(text="Wklej", on_click=lambda x: self.paste_path(), expand=1)

        row_path = ft.Row(controls=[label, btn_save_path, btn_paste_path],
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN)


        self.content = ft.Column(controls=[row_theme, row_path])

    def paste_path(self):
        self.result.value = pp.paste()


class EkwTabDownload(ft.Container):
    def __init__(self):
        super().__init__()



        self.instance = None
        self.tasks = ft.Column()
        self.expand = 1

        def on_dialog_result(e: ft.FilePickerResultEvent):
            print("Selected files:", e.files)
            print("Selected file or directory:", e.path)
            self.tasks.controls.append(ft.Text(value=e.files))
            self.update()

        file_picker = ft.FilePicker(on_result=on_dialog_result)


        # self.width = 1000
        self.bgcolor = ft.colors.WHITE12
        self.border_radius = ft.border_radius.all(20)
        self.padding = 5
        self.content = ft.Column(
            controls=[
                    ft.Row(controls=[
                        file_picker,
                        ft.ElevatedButton(text="Dodaj listę", on_click= lambda x: file_picker.pick_files(allow_multiple=False), expand=1),
                        ft.ElevatedButton(text="Pobierz", on_click=lambda x: self.save_changes(), expand=1),
                        ft.ElevatedButton(text="Pobierz Turbo", on_click=lambda x: self.add_new(), expand=1)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Column(
                        scroll=ft.ScrollMode.ALWAYS,
                        expand=1,
                    controls=[self.tasks])
                ]
            )


def main(page: ft.Page):
    page.title = "eKW - Pobieraczek 1.3"


    page.window.width = 422  # window's width is 200 px
    page.window.height = 750  # window's height is 200 px
    page.window.resizable = True  # window is not resizable

    page.window.min_width = 422
    page.window.min_height = 500

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    def theme_on_change(e):
        # print(e.data)
        page.theme = ft.theme.Theme(color_scheme_seed=str(e.data).lower())
        page.update()

    def light_on_change(e):
        # print(e.data)
        if str(e.data) == "Light":
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK

        page.update()


    # Tabs init

    tab_download = EkwTabDownload()
    tab_download.visible = True

    tab_settings = EkwSettings(theme_on_change=theme_on_change, light_on_change=light_on_change)
    tab_settings.visible = False

    page.update()
    def change_tab(e):
        idx = e.control.selected_index

        tab_download.visible = True if idx == 0 else False
        # capp.visible = True if idx == 1 else False
        # capp.visible = True if idx == 2 else False
        tab_settings.visible = True if idx == 3 else False
        # capp.visible = True if idx == 4 else False
        page.update()


    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.DOWNLOAD_OUTLINED, selected_icon=ft.icons.DOWNLOAD, label="Pobieranie\n z listy txt"),
            ft.NavigationBarDestination(icon=ft.icons.DRAW_OUTLINED, selected_icon=ft.icons.DRAW, label="Generator\n"),
            ft.NavigationBarDestination(icon=ft.icons.MENU_OUTLINED, selected_icon=ft.icons.MENU, label="Menedżer\nzadań"),
            ft.NavigationBarDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="Ustawienia\n"),
            ft.NavigationBarDestination(icon=ft.icons.HELP_OUTLINE, selected_icon=ft.icons.HELP, label="O programie\n"),
        ],
        on_change=change_tab,
    )

    page.theme = ft.theme.Theme(color_scheme_seed="red")
    page.update()
    page.add(tab_download, tab_settings)



if __name__ == "__main__":
    # main()
    ft.app(main)