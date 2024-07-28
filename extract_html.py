import os

from bs4 import BeautifulSoup as BS

import json
import pandas as pd

element_l = []

def main():

    json_to_xlsx()
    return


    path = "D:/Python/KW - eKW pobieracz/scraped_KW/"

    file_names = os.listdir(path)

    print(*file_names)

    for file_name in file_names:

        if file_name.endswith("1o.html"):
            get_html_data(f"{path}/{file_name}", path)


    path_without_ext = f"{path}/_dzial_1o.xlsx"
    df = pd.DataFrame(element_l)
    # header = False if os.path.exists("output.csv") else True
    header = True
    # df.to_csv(path_without_ext, mode='w', index=False, header=header, sep=';', encoding="utf-8-sig")
    df.to_excel(path_without_ext, sheet_name=f'KW', header=header, index=False)

    with open(f'{path}_dzial_1o-test.json', 'w', encoding="utf-8") as file:
        json.dump(element_l, file, ensure_ascii=False) #, indent=1)


def get_html_data(file_name, path):

    with open(file_name, encoding="utf-8") as fp:
        soup = BS(fp, 'html.parser')

    elem = soup.findAll('td', separator='')

    my_data = []

    temp = []
    for el in elem:

        if el.text != '':
            # print(el.text)
            if el.text == '\n\n\n\n\n':
                continue
            temp.append(el.text)
        else:
            my_data.append(temp)
            temp = []
            # print('*')

    element = {}

    new_data = {}

    next = False
    last_name = ''
    i = 1

    name = os.path.basename(file_name).replace("_1o.html", "")
    print(name)
    # print(os.path.dirname(file_name))

    valid_tags = ["Numer działki", "Identyfikator działki", "Obręb ewidencyjny (numer, nazwa)", "Sposób korzystania",
                  "Przyłączenie (numer księgi wieczystej, z której odłączono działkę, obszar)", "Numer księgi dawnej",
                  "Oznaczenie zbioru dokumentów", "Przyłączenie (numer księgi wieczystej, z której odłączono działkę)",
                  "Przyłączenie (obszar)"]
    for md in my_data:
        if 'Numer działki' in md:
            new_data['id'] = f"{name}-{i}"
            for m in md:
                if next:
                    next = False
                    if last_name == "Przyłączenie (numer księgi wieczystej, z której odłączono działkę, obszar)":
                        splt = m.split(", ")
                        new_data['Numer księgi dawnej'] = splt[0].strip()
                        new_data['Przyłączenie (obszar)'] = splt[1].strip()

                    elif last_name == "Przyłączenie (numer księgi wieczystej, z której odłączono działkę)":
                        new_data['Numer księgi dawnej'] = m.strip()
                    else:
                        new_data[last_name] = m.strip()

                if m.strip() in valid_tags:
                    # print(m)
                    last_name = m
                    next = True

                else:
                    # print(m)
                    ...

            element[f"{name}-{i}"] = new_data
            element_l.append(new_data)
            i += 1
            new_data = {}
        elif 'Obszar całej nieruchomości' in md:
            new_data['id'] = f"{name}-{i}"
            for m in md:
                if next:
                    next = False
                    new_data['Obszar całej nieruchomości'] = m.strip()
                if m.strip() in 'Obszar całej nieruchomości':
                    # print(m)
                    last_name = m
                    next = True

            new_data["Numer działki"] = '---'
            element[f"{name}-X"] = new_data
            element_l.append(new_data)
            i += 1
            new_data = {}




    # print(*element, sep="\n")

    with open(f'{path}_dzial_1o.json', 'a', encoding="utf-8") as file:
        json.dump(element, file, ensure_ascii=False, indent=1)

def dz_from_page(file_name):

    with open(file_name, encoding="utf-8") as fp:
        soup = BS(fp, 'html.parser')

    elem = soup.findAll('td', separator='')

    my_data = []

    temp = []
    for el in elem:

        if el.text != '':
            if el.text == '\n\n\n\n\n':
                continue
            temp.append(el.text)
        else:
            my_data.append(temp)
            temp = []
            # print('*')

    element = {}
    new_data = {}
    next = False
    last_name = ''
    i = 1

    valid_tags = ["Numer działki", "Identyfikator działki"]
    for md in my_data:
        if 'Numer działki' in md:
            for m in md:
                if next:
                    next = False
                    new_data[last_name] = m.strip()

                if m.strip() in valid_tags:
                    last_name = m
                    next = True

                else:
                    ...

            element[f"{i}"] = new_data
            element_l.append(new_data)
            i += 1
            new_data = {}

    return element

def page_to_json(file_name, path, xlsx=False):


    with open(file_name, encoding="utf-8") as fp:
        soup = BS(fp, 'html.parser')

    elem = soup.findAll('td', separator='')

    my_data = []

    temp = []
    for el in elem:

        if el.text != '':
            # print(el.text)
            if el.text == '\n\n\n\n\n':
                continue
            temp.append(el.text)
        else:
            my_data.append(temp)
            temp = []
            # print('*')

    element = {}

    new_data = {}

    next = False
    last_name = ''
    i = 1

    name = os.path.basename(file_name).replace("_1o.html", "")
    # print(name)

    valid_tags = ["Numer działki", "Identyfikator działki", "Obręb ewidencyjny (numer, nazwa)", "Sposób korzystania",
                  "Przyłączenie (numer księgi wieczystej, z której odłączono działkę, obszar)", "Numer księgi dawnej",
                  "Oznaczenie zbioru dokumentów", "Przyłączenie (numer księgi wieczystej, z której odłączono działkę)",
                  "Przyłączenie (obszar)"]
    for md in my_data:
        if 'Numer działki' in md:
            new_data['id'] = f"{name}-{i}"
            for m in md:
                if next:
                    next = False
                    if last_name == "Przyłączenie (numer księgi wieczystej, z której odłączono działkę, obszar)":
                        splt = m.split(", ")
                        new_data['Numer księgi dawnej'] = splt[0].strip()
                        new_data['Przyłączenie (obszar)'] = splt[1].strip()

                    elif last_name == "Przyłączenie (numer księgi wieczystej, z której odłączono działkę)":
                        new_data['Numer księgi dawnej'] = m.strip()
                    else:
                        new_data[last_name] = m.strip()

                if m.strip() in valid_tags:
                    # print(m)
                    last_name = m
                    next = True

                else:
                    # print(m)
                    ...

            element[f"{name}-{i}"] = new_data
            element_l.append(new_data)
            i += 1
            new_data = {}
        elif 'Obszar całej nieruchomości' in md:
            new_data['id'] = f"{name}-X"
            for m in md:
                if next:
                    next = False
                    new_data['Obszar całej nieruchomości'] = m.strip()
                if m.strip() in 'Obszar całej nieruchomości':
                    # print(m)
                    last_name = m
                    next = True

            new_data["Numer działki"] = '---'
            element[f"{name}-X"] = new_data
            element_l.append(new_data)
            i += 1
            new_data = {}




    # print(*element, sep="\n")

    """with open(f'{path}/_dzial_1o.json', 'a', encoding="utf-8") as file:
        json.dump(element, file, ensure_ascii=False, indent=1)"""


    if os.path.exists(f'{path}/_dzial_1o.json'):
        with open(f'{path}/_dzial_1o.json', 'r', encoding="utf-8") as f:
            data = json.load(f)

        data.update(element)

        with open(f'{path}/_dzial_1o.json', 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    else:
        with open(f'{path}/_dzial_1o.json', 'w', encoding="utf-8") as f:
            json.dump(element, f, ensure_ascii=False, indent=1)

    if xlsx:
        try:
            json_to_xlsx(f'{path}/_dzial_1o.json')
        except:
            ...

def json_to_xlsx(path: str = r"D:\lukasz\python\KW - eKW pobieracz\scraped_KW\goraszka\_dzial_1o.json" ):

    jsonloaded = ''
    line = ''
    with open(path, "r", encoding="utf-8") as file:
        jsonloaded  = json.load(file)
        #line = file.readlines()
        #jsonloaded = json.load(file)

    #print(type(line))
    #print(line)
    #print(*list(line))

    #return

    #jsonloaded = json.loads(line)

    dictionary = jsonloaded.values()

    path_without_ext = path.replace(".json", ".xlsx")
    df = pd.DataFrame(dictionary)
    # header = False if os.path.exists("output.csv") else True
    header = True
    # df.to_csv(path_without_ext, mode='w', index=False, header=header, sep=';', encoding="utf-8-sig")
    df.to_excel(path_without_ext, sheet_name=f'KW', header=header, index=False)



if __name__ == "__main__":
    main()