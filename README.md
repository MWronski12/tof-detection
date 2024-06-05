
- [X] Obliczenie kątów i odległości na kartce
- [X] Sposob na ustawienie czujnika pod odpowiednim katem
- [X] Strategia wyboru dystansu z dwóch celów na strefę - confidence, closest, average
- [x] Output csv data filename as argument
- [x] Sprawdzenie maksymalnego zasięgu czujnika po zmroku z białym celem i normalnym
- [x] Wyznaczanie kąta pola widzenia czujnika w srodkowej strefie
- [ ] Protokół testu wraz z potrzebnym sprzetem, ustawieniem czujnika, kolejnoscia dzialan, liczba i rodzajem przejazdow
- [ ] Automatyczne matchowanie danych
    - [ ] GPS
    - [ ] video
- [x] Testy dzisiaj po zmroku - minimum 3 przejazdy ze znana predkoscia

- [ ] Better plotting:
    - [x] Plot depth map
    - [x] Add slider for t selection
    - [x] Add text input for t selection
    
TODO NOW:
    
- [ ] Remove event and add component methods with typehints
- [ ] Remove the buffering from GUI, just make it poll the data and only the amount it needs

- [ ] Add data transform proxy:
    - [ ] Separate it into a different class and make selectable
    - [ ] Think if we should couple distance selection strategy and other transformations like EMA smoothing

- [ ] Add SpeedEstimator component
    - [ ] Think if it should poll for batches of data like GUI or be updated 1 sample at a time (dev vs production)
    - [ ] SpeedEstimator output to GUI plot

- [ ] Make the buffer cleaner:
    - [ ] use numpy/pandas
    - [ ] parametrize rewind/fast-forward step
    - [ ] add getters by x last seconds

