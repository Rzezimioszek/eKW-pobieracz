
rep_dict = {"X": "10", "A": "11", "B": "12", "C": "13", "D": "14", "E": "15",
                        "F": "16", "G": "17", "H": "18", "I": "19", "J": "20", "K": "21",
                        "L": "22", "M": "23", "N": "24", "O": "25", "P": "26", "R": "27",
                        "S": "28", "T": "29", "U": "30", "W": "31", "Y": "32", "Z": "33",
                        "0":"0", "1":"1", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8", "9":"9"}


def kw_from_range(sad: str, bot: int, top: int, last: int = -1, control: int = -1) -> str:
    """ Generowanie numerów ksiąg wieczystych z zakresu
        sad - oznaczenie sądu
        bot - wartość początkowa zakresu
        top - wartość końcowa zakresu
        Parametry opcjonalne:
        last - ostatnia cyfra numeru
        control - znana cyfra kontrolna
    """
    sad_value = [rep_dict[s] for s in sad]
    wei = 4 * [1, 3, 7]
    params = [True, True]

    if bot > top:
        bot, top = top, bot

    for number in range(bot, (top + 1)):

        number = f'{number:08}'
        temp_kw = sad_value + [*number]
        ctlr_dig = 0

        for w, t in zip(wei, temp_kw):
            ctlr_dig += w * int(t)

        ctlr_dig = ctlr_dig % 10

        skw = f"{sad}/{number}/{ctlr_dig}"

        params[0] = (skw[-3] == str(last)) if (last != - 1) else True
        params[1] = (skw[-1] == str(control)) if (control != - 1) else True

        if params[0] and params[1]:
            yield skw


def main():
    x = [y for y in kw_from_range("BB1B", 5, 500, control=9, last=7)]
    print(x, len(x))


if __name__ == "__main__":
    main()