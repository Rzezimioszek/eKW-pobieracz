# eKW-pobieracz
Program służący do masowego pobierania ksiąg wieczystych z serwisu ekw.ms.gov.pl

	Do poprawnego działania program potrzebuje istneijącego numeru księgi wieczystej w formacie AA1A/NNNNNNNN/K, 
	gdzie:
		AA1A - oznaczenie sądu
		NNNNNNNN - numer księgi
		K - cyfra kontrolna
	Lista powinna znajdować się w pliku tekstowym w którym każda księga zaczyna się od nowej linii.
	Miejscem zapisu jest folder, gdzie zostaną zapisane księgi (podzielone na działy) w postaci: AA1A.NNNNNNNN.K_d.pdf
	
	Funkcje, które będą wporwadzane sukcesywnie:
		*	Generowanie listy dostępnych KW w danym sądzie rejonowym
		*	Zapis do jednego połączonego pliku
		*	Tryb turbo (wiele ksiąg zapisywanych na raz)
		
	Jeśli brakuje jakiejś funkcji, a chciałbyś ją zobaczyć w programie to zapraszam do kontaktu.
