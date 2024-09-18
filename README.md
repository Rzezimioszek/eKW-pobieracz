# eKW pobieraczek (eKW-pobieracz)

UWAGA !
Program oparty na QT jest dalej rozwijany w branch Legacy.
W main pojawi się wersja oparta na UI FLET. Kiedy? Kiedy będę miał czas ją skończyć.

Wątek na wykopie https://wykop.pl/tag/ekwpobieraczek
Program służący do masowego pobierania ksiąg wieczystych z serwisu ekw.ms.gov.pl

Plik EXE po prawej stronie w Released

!wymagane:
- posiadanie przeglądarki Google Chrome lub EDGE!
-  Microsoft Visual C++ Redistributable (X86 i X64)

	Do poprawnego działania program potrzebuje istneijącego numeru księgi wieczystej w formacie 
 	AA1A/NNNNNNNN/K, 
	gdzie:
		AA1A - oznaczenie sądu
		NNNNNNNN - numer księgi
		K - cyfra kontrolna
	W przypadku braku cyfry kontrolnej program sobie ją obliczy :)
 
	Lista powinna znajdować się w pliku tekstowym w którym każda księga zaczyna się od nowej linii.
	Miejscem zapisu jest folder, gdzie zostaną zapisane księgi (podzielone na działy) w postaci: 
 	AA1A.NNNNNNNN.K_d.pdf

* Zapis do formatu HTML (na razie mam tekst i linki)
* Zapis do formatu TXT
* Zapis raportu z wyszukania dla każdej księgi osobno (z okienka po wpisaniu numeru, ale przed wybraniem treści)  do JSON
* Zapis raportu z wyszukania do jednego pliku(z okienka po wpisaniu numeru, ale przed wybraniem treści)  do CSV
* Baner przenoszący kliknięciem do tagu
* 8 bitowa muzyka (przywrcono w wersji 1.1)
* Pobieranie/generowanie numerów KW nie mrozi okna programu
* Tryb pauzy
* Zatrzymywanie pobierania
(Zatrzymywanie i pauza następują po zakończeniu obecnego taska np. jeśli pobierasz po 5 ksiąg na raz to dopiero po ich pobraniu się zatrzyma)
* w przypadku błędu pobierania przez Chrome program spróbuje poprać przez EDGE (chromium)
* możliwość wyłączenia wyświetlania grafik na pobieranych stronach
* poprawiono mniejsze błędy (skalowanie nadal nie poprawione przy innych ustawieniach niż 100%)
nadal stare UI, ale obudowane prawdziwy potwór Frankeisteina
* nowe nieznane błędy!!!
		
	Jeśli brakuje jakiejś funkcji, a chciałbyś ją zobaczyć w programie to zapraszam do kontaktu.


![1 1](https://github.com/user-attachments/assets/f82ceb67-87bb-47cd-917e-989d7ddaa6e9)




