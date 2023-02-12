# Analiza_podatkov_o_letih
Analizirala bom podatke o vseh letih v naslednjih 5 mesecih iz dveh večjih bližnjih italjanskih letališč, in sicer Venice Marco Polo in Bergamo Orio al Serio. 
Za obe letališči bom zajela podatke o možnih povezavah iz strani:
[Venice Marco Polo](https://www.veneziaairport.it/en/flights/seasonal-schedule/fdatefrom-15-10-2022/fdateto-25-03-2023/ftype-D/ftframe-alldaylong/page-1.html)
[Bergamo Orio al Serio](https://www.milanbergamoairport.it/en/seasonal-flights-timetable/)
Naredila bom tudi primerjavo med povezavami enega in drugega letališča.

Vsak let bo določen z:
* destinacijo
* letalsko družbo / *letalskimi družbami 
* datumom leta
* številko leta / *številkami leta 
* časom leta
*- nekatere lete upravlja več letalskih družb skupaj

bergamo.csv :
*  vsebuje podatke o letih v obdobju od novembra 2022 do marca 2023 iz Bergama in sicer za vsak let vsebuje: id-leta, destinacijo, datum in čas leta

venezia.csv :
*  vsebuje podatke o letih v obdobju od novembra 2022 do marca 2023 iz Benetk  in sicer za vsak let vsebuje: id-leta, destinacijo, datum in čas leta

Za vsak let pripadajoče letalske družbe in letala pa se nahajajo v datoteki 
letalska_druzba.csv

## Delovne hipoteze:
* Več letov je v obdobju praznikov (zadnji teden leta 2022 in prvi teden 2023).
* Največje število letov po državah iz letališča Marco Polo je v Italijo.
* Največ letov iz beneškega letališča je v soboto.
* V soboto je največja razlika v številu letov med letališčema.
* Ryanair predstavlja več kot polovico vseh letov iz Bergama.
* Največ letov iz obeh letališč je v eno izmed italijanskih letališč.
* Benetke imajo več direktnih letov v Severno Ameriko.
* Svetovno nogometno prvenstvo je vplivalo na število letov v Katar.