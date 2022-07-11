# kurek.py
**kurek** to skrypt pozwalający na bardzo szybkie ściąganie danych z serwisu [zbiornik.com](https://zbiornik.com).

Skrypt loguje się na Twoje konto w serwisie i zaczyna ściągać to, co mu każesz. Używa API udostępnionego przez serwery i odnajduje linki do mediów udostępnionych przez inne profile, a następnie ściąga pliki na dysk - asynchronicznie i równolegle. 

Aktualnie projekt jest w fazie ciężkiego developmentu - kod tworzony jest na podstawie prototypu niedostępnego publicznie.

# Ficzery
- Napisany w Pythonie 3. 
- Używa bibliotek opartych na *asyncio* - ściąganie plików nigdy nie było tak szybkie.
- Dostępny jako obraz Dockerowy - nie musisz bawić się w instalację.
- Umożliwia dostęp do mediów z lat, które nie są dostępne przez stronę WWW - wybierz dowolny datę i zacznij ściągać.
