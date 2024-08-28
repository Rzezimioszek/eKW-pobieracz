
from tkinter import filedialog

def open_file():
    filetypes_option = (("pliki txt", "*.txt"), ("pliki kw", "*.kw"), ("Wszystkie pliki", "*.*"))
    path = filedialog.askopenfilenames(title="Wybierz plik lub pliki", filetypes=filetypes_option)
    if path is not None:
        path = str(path).replace("('", "")
        path = path.replace("',)", "\t")
        path = path.replace("')", "\t")
        path = path.replace("', '", "\t")
        path = path.strip()

        return path

def open_dir():
    filetypes = (("dane wynikowe", ".xlsx .csv .pdf .json .txt"), ("Wszystkie pliki", "*.*"))
    path = filedialog.askdirectory(title="Wybierz folder")

    if path is not None:
        return path

if __name__ == "__main__":
    ...