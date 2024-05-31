
- [X] Obliczenie kątów i odległości na kartce
- [X] Sposob na ustawienie czujnika pod odpowiednim katem
- [X] Strategia wyboru dystansu z dwóch celów na strefę - confidence, closest, average
- [x] Output csv data filename as argument
- [x] Sprawdzenie maksymalnego zasięgu czujnika po zmroku z białym celem i normalnym
- [x] Wyznaczanie kąta pola widzenia czujnika w srodkowej strefie
- [ ] Rozwiazanie problemu niewiadomej odleglosci od rzeczywistego ruchu rowerzysty
- [ ] Protokół testu wraz z potrzebnym sprzetem, ustawieniem czujnika, kolejnoscia dzialan, liczba i rodzajem przejazdow
- [ ] Automatyczne matchowanie danych
    - [ ] GPS
    - [ ] video
- [ ] Testy dzisiaj po zmroku - minimum 3 przejazdy ze znana predkoscia

- [ ] Better plotting:
    - [x] Plot depth map
    - [ ] Add slider for t selection
    - [ ] Add text input for t selection
    - [ ] Handle big csv
    
    TODO NOW:
    - [ ] get_data(last x seconds)
    - [ ] separate ETL

        Extract - Load csv file or receive TCP input stream
        Transform - Zone distance picking strategy, auto velocity labeling, extra features, formats, output DataFrame
        Load - Feed data to visualization and detection algorithm

    - [ ] Add seek, rewind, fast-forward, goto timestamp, pause, play to data provider interface
