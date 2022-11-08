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
*  vsebuje podatke o letih v naslednjih 5 mesecih iz Bergama  in sicer za vsak let vsebuje: id-leta, destinacijo, datum in čas leta,
venezia.csv :
*  vsebuje podatke o letih v naslednjih 5 mesecih iz Benetk  in sicer za vsak let vsebuje: id-leta, destinacijo, datum in čas leta
Za vsak let pripadajoče letalske družbe in letala pa se nahajajo v datoteki 
letalska_druzba.csv

## Delovne hipoteze:
* Ali je res, da je več letov ob koncu leta (za čas praznikov)?
* Kateri dan v tednu je največ letov?
* Katero od letališč ponuja več destinacij in kateri ima večje število letov na teden kot drugi?
* Katero letališče ima več letov v Severno Ameriko?
* Ali so najbolj pogosti notranji leti (znotraj Italije)?