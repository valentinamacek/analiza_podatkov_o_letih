from xml.sax.handler import feature_external_ges
import requests
import os
import sys
import re
from datetime import datetime

ST_STRANI = 109
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

def shrani_venezia():
    stran = 1
    while True:
        url = f'https://www.veneziaairport.it/en/flights/seasonal-schedule/fdatefrom-30-10-2022/fdateto-25-03-2023/ftype-D/ftframe-alldaylong/page-{stran}.html'
        besedilo = download_url_to_string(url)
        if najdi_lete(besedilo) == None:
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
    for dest_id in destinacije:
        for par in PARI: 
            url = f'https://www.milanbergamoairport.it/en/seasonal-flights-timetable/calendar/linea/dep/{dest_id}/?m={par[0]}&y={par[1]}'
            dat = f'bergamo/{dest_id}/{par[0]}.html'
            shrani_spletno_stran(url, dat)
            vsebina = vsebina_datoteke(dat)
            for let_najdba in bvzorec_leta.finditer(vsebina):
                let = podatki_o_letu_izboljsaj(let_najdba.groupdict())
                leti.append(let)
    return leti



def najdi_lete(vsebina_strani):
    seznam_letov = vzorec_bloka.findall(vsebina_strani)
    if len(seznam_letov)==1:
       leti = []
       for let_podatki in vzorec_leta.finditer(seznam_letov[0]):
            let = let_podatki.groupdict()
            leti.append(let)
       return leti
    else:
        return None

def vsi_leti_venezia():
    leti = []   
    for i in range(1, ST_STRANI + 1):
        dat = f'venezia/{i}.html'
        vsebina = vsebina_datoteke(dat)
        letala = najdi_lete(vsebina)
        leti.extend(letala)
    print(leti)

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
    t_odhod = datetime.strptime(slovar_leta['odhod'], "%H:%M")
    t_prihod = datetime.strptime(slovar_leta['prihod'], "%H:%M")
    delta = t_prihod - t_odhod
    cas = (int(delta.total_seconds()) // 3600 , int((delta.total_seconds() % 3600) // 60)) 
    slovar_leta['cas'] = f'{cas[0]}:{cas[1]}'

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
    for x in koledar :
        if x[0] == zacetni_dat[0] and x[1] == zacetni_dat[1]:
            zacetni_indeks = koledar.index(x)
            print(zacetni_indeks)
        if x[0] == koncni_dat[0] and x[1] == koncni_dat[1]:
            koncni_indeks = koledar.index(x)
            print(koncni_indeks)
    if zacetni_indeks != koncni_indeks:
        datumi_letov = []
        for i in range(zacetni_indeks, koncni_indeks + 1):
            if koledar[i][3] in dnevi:
               datumi_letov.append(koledar[i])
        return datumi_letov
    else:
        return koledar[zacetni_indeks]






# def main(redownload=True, reparse=True):
#     shrani_venezia()

# def vsi_leti_bergamo():
#     leti= []

dat = f'bergamo/RHO/03.html'
vsebina = vsebina_datoteke(dat)
slovar = bvzorec_leta.search(vsebina).groupdict()
print(slovar)
ku = {'destinacija': 'Rhodes', 'datum': '26/03/2023', 'druzba': 'Ryanair', 'letalo': 'FR 4201', 'odhod': '05:45', 'prihod': '09:35'}

vedat = f'venezia/100.html'
vsebin = vsebina_datoteke(vedat)
leti = najdi_lete(vsebin)
print(leti)