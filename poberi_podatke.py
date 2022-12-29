from xml.sax.handler import feature_external_ges
import requests
import os
import sys
import re
import csv
import json
from datetime import datetime, timedelta

ST_STRANI = 110
PARI = [('11', '2022'),('12', '2022'), ('01', '2023'), ('02', '2023'), ('03', '2023')]
vzorec_bloka = re.compile(
    r'<div class="table-responsive">.*?<th>FLIGHT</th>.*?<tbody>(.*?)</tbody>',
    flags=re.DOTALL
)
vzorec_leta = re.compile(
    r'<tr>.*?<td>(?P<letalo>.*?)</td>.*?'
    r'<td>(?P<druzba>.*?)</td>.*?'
    r'<td>(?P<destinacija>.*?)</td>.*?'
    r'<td>FROM (?P<od>.*?)<br>TO (?P<do>.*?)</td>.*?'
    r'<td>(?P<dnevi>.*?)</td>.*?'
    r'<td>(?P<odhod>.*?)</td>.*?'
    r'<td>(?P<prihod>.*?)</td>.*?</tr>',
    flags=re.DOTALL
)

vzorec_dest = re.compile(
    r'<a href="/en/seasonal-flights-timetable/calendar.*?/dep/(?P<dest>.*?)/" class',
    flags=re.DOTALL
)

bvzorec_leta = re.compile(
    r'<h4 class="modal-title".*?In partenza per (?P<destinacija>.*?) - (?P<datum>.*?)</h4>.*?'
    r'<th></th></tr><tr>.*?<td>(?P<druzba>.*?)</td><td>(?P<letalo>.*?)</td>.*?'
    r'<td>(?P<odhod>.*?)</td>.*?'
    r'<td>(?P<prihod>.*?)</td>',
     flags=re.DOTALL
)
def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)


def shrani_spletno_stran(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
        return None
    else:
        pripravi_imenik(ime_datoteke)
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(r.text)


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        # del kode, ki morda sproži napako
        page_content = requests.get(url)
    except requests.exceptions.ConnectionError:
        # koda, ki se izvede pri napaki
        # dovolj je če izpišemo opozorilo in prekinemo izvajanje funkcije
        print("Napaka pri povezovanju do:", url)
        return None
    # nadaljujemo s kodo če ni prišlo do napake
    return page_content.text

def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()
def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        writer.writerows(slovarji)


def zapisi_json(objekt, ime_datoteke):
    '''Iz danega objekta ustvari JSON datoteko.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as json_datoteka:
        json.dump(objekt, json_datoteka, indent=4, ensure_ascii=False)

def shrani_venezia():
    stran = 1
    while True:
        url = f'https://www.veneziaairport.it/en/flights/seasonal-schedule/fdatefrom-30-10-2022/fdateto-25-03-2023/ftype-D/ftframe-alldaylong/page-{stran}.html'
        besedilo = download_url_to_string(url)
        if najdi_lete_venezia(besedilo) == None:
            return None
        datoteka = f'venezia/{stran}.html'
        shrani_spletno_stran(url, datoteka)
        stran+=1    

def shrani_bergamo():
    url = 'https://www.milanbergamoairport.it/en/seasonal-flights-timetable/'
    datoteka = 'bergamo/frontpage.html'
    shrani_spletno_stran(url, datoteka)

def shrani_destinacije_bergamo():
    dat = 'bergamo/frontpage.html'
    prva_stran_vsebina = vsebina_datoteke(dat)
    destinacije = []
    for dest in vzorec_dest.finditer(prva_stran_vsebina):
        destinacije.append(dest.group(1))
    leti= []
    id_leta = 1
    for dest_id in destinacije:
        for par in PARI: 
            url = f'https://www.milanbergamoairport.it/en/seasonal-flights-timetable/calendar/linea/dep/{dest_id}/?m={par[0]}&y={par[1]}'
            dat = f'bergamo/{dest_id}/{par[0]}.html'
            shrani_spletno_stran(url, dat)
            vsebina = vsebina_datoteke(dat)
            for let_najdba in bvzorec_leta.finditer(vsebina):
                let = podatki_o_letu_izboljsaj(let_najdba.groupdict())
                let['id'] = 'b' + f'{id_leta}'
                koledar = ustvari_slovar_datumov()
                datum = let['datum'].split('/')
                print(datum)
                for x in koledar:
                    if x[0] == int(datum[0]) and x[1] == int(datum[1]):
                        let['dan'] = x[3]
                        print(let['dan'])
                leti.append(let)
                id_leta += 1
    zapisi_json(leti, 'obdelani_podatki/bergamo.json')
    return leti


def najdi_lete_venezia(vsebina_strani, id_leta):
    seznam_letov = vzorec_bloka.findall(vsebina_strani)
    if len(seznam_letov)==1:
       leti = []
       for let_podatki in vzorec_leta.finditer(seznam_letov[0]):
            let = let_podatki.groupdict()
            vsi_datumi = razbij_na_datume(let)
            let.pop('dnevi')
            let.pop('od')
            let.pop('do')
            if not isinstance(vsi_datumi, list):
                let['datum'] = f'{vsi_datumi[0]}/{vsi_datumi[1]}/{vsi_datumi[2]}'
                let['id'] = 'v' + f'{id_leta}'
                let['dan'] = f'{vsi_datumi[3]}'
                nov = podatki_o_letu_izboljsaj(let)
                leti.append(nov)
                id_leta +=1
            else:
                for datum in vsi_datumi:
                    let_tisti_dan = dict(let)
                    let_tisti_dan['datum'] = f'{datum[0]}/{datum[1]}/{datum[2]}'
                    let_tisti_dan['dan'] = f'{datum[3]}'
                    let_tisti_dan['id'] = 'v' + f'{id_leta}'
                    novi = podatki_o_letu_izboljsaj(let_tisti_dan)
                    leti.append(novi)    
                    id_leta +=1
       return (leti, id_leta)
    else:
        return None


def vsi_leti_venezia():
    leti = []  
    id_leta = 1 
    for i in range(1, ST_STRANI + 1):
        dat = f'venezia/{i}.html'
        vsebina = vsebina_datoteke(dat)
        letala = najdi_lete_venezia(vsebina, id_leta)
        leti.extend(letala[0])
        id_leta = letala[1]
    zapisi_json(leti, 'obdelani_podatki/venezia.json')
    return  leti

def izloci_druzbo(leti):
    id_druzba_let = []
    for let in leti:
        slovar = {'id': let[0]}
        if isinstance(let[1], list):
            for druzba, letalo in zip(let[1], let[2]):
                posz_slovar = slovar.copy()
                posz_slovar['druzba'] = druzba
                posz_slovar['letalo'] = letalo
                id_druzba_let.append(posz_slovar)
        else:
            slovar['druzba'] = let[1]
            slovar['letalo'] = let[2]
            id_druzba_let.append(slovar)
    zapisi_csv(id_druzba_let, ['id', 'druzba', 'letalo'], 'obdelani_podatki/letalska_druzba.csv')



def ustvari_slovar_datumov():
    meseci = [11, 12, 1, 2, 3]
    datumi=[]
    dnevi = ['TOR', 'SRE', 'CET', 'PET', 'SOB', 'NED', 'PON']
    k = 0
    for mesec in meseci:
        if mesec == 11 or mesec == 12:
            leto = 2022
            if mesec == 11:
                for dan in range(1, 31):
                    datumi.append((dan, mesec, leto, dnevi[k]))
                    if k != 6:
                        k+=1
                    else:
                        k = 0
            else:
                for dan in range(1,32):
                    datumi.append((dan, mesec, leto,  dnevi[k]))
                    if k != 6:
                        k+=1
                    else:
                        k = 0
        else:
            nleto = 2023
            if mesec == 2:
                for dan in range(1, 29):
                    datumi.append((dan, mesec, nleto,  dnevi[k]))
                    if k != 6:
                        k+=1
                    else:
                        k = 0
            else:
                for dan in range(1,32):
                    datumi.append((dan, mesec, nleto,  dnevi[k]))
                    if k != 6:
                        k+=1
                    else:
                        k = 0
    return datumi

def podatki_o_letu_izboljsaj(slovar_leta):
    t_odhod = datetime.strptime(slovar_leta['datum'] + ' '+ slovar_leta['odhod'], "%d/%m/%Y %H:%M")
    t_prihod = datetime.strptime(slovar_leta['datum'] +' '+ slovar_leta['prihod'], "%d/%m/%Y %H:%M")
    if t_prihod < t_odhod:
        t_prihod = t_prihod + timedelta(days=1)
    delta = t_prihod - t_odhod 
    cas = (int(delta.total_seconds()) // 3600 , int((delta.total_seconds() % 3600) // 60)) 
    slovar_leta['cas'] = f'{cas[0]}:{cas[1]}'
    vec_druzb = re.findall(r'(.*?)<br />', slovar_leta['druzba'] + '<br />')
    if len(vec_druzb) > 1:
        slovar_leta['druzba'] = vec_druzb
        izloci_prvega = re.search(r'<span.*?"bold">(.*?)</span>(.*?)$', slovar_leta['letalo'] + '<br />')
        brez_spana = izloci_prvega.group(1) + izloci_prvega.group(2) 
        slovar_leta['letalo'] = re.findall(r'(.*?)<br />', brez_spana)
    return slovar_leta

def razbij_na_datume(slovar):
    zacetek = slovar['od'].split('/')
    konec = slovar['do'].split('/')
    niz = slovar['dnevi']
    dnevi = []
    i = 0
    crtice = 0
    while i < len(niz):
        if niz[i] == '-':
            crtice += 1
        if niz[i].isalpha():
            if crtice == 0 and niz[i] == 'L':
                dnevi.append('PON')
            elif (crtice == 1 or len(dnevi) == 1) and niz[i] == 'M':
                dnevi.append('TOR')
            elif (crtice == 2 or len(dnevi) == 2 or (crtice == 1 and len(dnevi) == 1)) and niz[i]=='M':
                dnevi.append('SRE')
            elif niz[i] == 'G':
                dnevi.append('CET')
            elif niz[i] == 'V':
                dnevi.append('PET')
            elif niz[i] == 'S':
                dnevi.append('SOB')
            else:
                dnevi.append('NED')
        i+=1
    zacetni_dat = (int(zacetek[0]), int(zacetek[1]), int(zacetek[2]))
    koncni_dat = (int(konec[0]), int(konec[1]), int(konec[2]))
    koledar = ustvari_slovar_datumov()
    zacetni_indeks = 0
    koncni_indeks = 0
    for x in koledar:
        if x[0] == zacetni_dat[0] and x[1] == zacetni_dat[1]:
            zacetni_indeks = koledar.index(x)
        if x[0] == koncni_dat[0] and x[1] == koncni_dat[1]:
            koncni_indeks = koledar.index(x)
    if zacetni_indeks != koncni_indeks:
        datumi_letov = []
        for i in range(zacetni_indeks, koncni_indeks + 1):
            if koledar[i][3] in dnevi:
               datumi_letov.append(koledar[i])
        return datumi_letov
    else:
        return koledar[zacetni_indeks]


benetke = vsi_leti_venezia()
bergamo = shrani_destinacije_bergamo()
vsi_leti_za = []
benetke_zapisi = []
for let in benetke:
    vsi_leti_za.append((let['id'], let.pop('druzba'), let.pop('letalo')))
    let.pop('prihod')
    let.pop('odhod')
    benetke_zapisi.append(let)
zapisi_csv(benetke_zapisi, ['id', 'destinacija', 'datum','dan', 'cas'], 'obdelani_podatki/venezia.csv')

bergamo_zapisi = []
for blet in bergamo:
    vsi_leti_za.append((blet['id'], blet.pop('druzba'), blet.pop('letalo')))
    blet.pop('prihod')
    blet.pop('odhod')
    bergamo_zapisi.append(blet)
zapisi_csv(bergamo_zapisi, ['id','destinacija', 'datum','dan', 'cas'], 'obdelani_podatki/bergamo.csv' )
izloci_druzbo(vsi_leti_za)






