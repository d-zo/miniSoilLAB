# -*- coding: utf-8 -*-
"""
verarbeitung_hilfen.py   v0.3 (2023-09)
"""

# Copyright 2020-2023 Dominik Zobel.
# All rights reserved.
#
# This file is part of the miniSoilLAB package.
# miniSoilLAB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# miniSoilLAB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with miniSoilLAB. If not, see <http://www.gnu.org/licenses/>.


# -------------------------------------------------------------------------------------------------
def ImportiertesDatumFormatieren(datum, ausgabeformat='%d.%m.%Y',
    formatliste=['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y%m%d']):
    """Erwartet einen String datum, der entweder eine Gleitkommazahl repraesentiert (Rohdatum aus
    Excel) oder bereits ein gueltiges Datum in einem Format aus formatliste erhaelt. Gibt das
    extrahierte Datum im ausgabeformat zurueck oder den uebergebenen String, falls es nicht
    erfolgreich extrahiert werden kann.
    """
    import datetime

    if (ausgabeformat not in formatliste):
        formatliste += [ausgabeformat]

    startdatum = datetime.datetime(year=1899, month=12, day=30)
    mod_datum = None
    for idx_zeit in range(1):
        try:
            tempzeit = startdatum + datetime.timedelta(days=float(datum))
            mod_datum = tempzeit.strftime(ausgabeformat)
            break
        except:
            pass

        for datumformat in formatliste:
            try:
                tempzeit = datetime.datetime.strptime(datum, datumformat)
                mod_datum = tempzeit.strftime(ausgabeformat)
                break
            except:
                pass

    if (mod_datum is None):
        print('# Warnung: Datum konnte nicht aus >' + datum + '< extrahiert werden')
        mod_datum = datum

    return mod_datum



# -------------------------------------------------------------------------------------------------
def SekundenAusDatumsangabenExtrahieren(daten, formatliste=[]):
    """Erwartet eine Liste an Datum-String daten, deren Eintraege entweder eine Gleitkommazahl
    repraesentieren (typischerweise Rohdatum aus Excel) oder bereits ein gueltiges Datum in
    einem der angegebenen datumformate erhaelt. Aus allen Eintraegen werden die vergangenen Sekunden
    relativ zum ersten Eintrag extrahiert. Gibt eine Liste der Differenzen in Sekunden bei
    erfolgreicher Verarbeitung zurueck, sonst None.
    """
    import datetime

    startdatum = datetime.datetime(year=1899, month=12, day=30)
    sekunden = [0.0 for x in daten]
    refzeit = None
    for idx_datum, datum in enumerate(daten):
        zeitpunkt = None
        for idx_none in range(1):
            try:
                zeitpunkt = startdatum + datetime.timedelta(days=float(datum))
                break
            except:
                pass

            for datumformat in formatliste:
                try:
                    zeitpunkt = datetime.datetime.strptime(datum.split('.')[0], datumformat)
                    break
                except:
                    pass

        if (zeitpunkt is None):
            print('# Warnung: Konnte nicht alle Zeitstempel konvertieren')
            return None

        if (refzeit is None):
            refzeit = zeitpunkt

        sekunden[idx_datum] = (zeitpunkt - refzeit).total_seconds()

    return sekunden



# -------------------------------------------------------------------------------------------------
def SekundenOhneOffsetBereitstellen(daten, formatliste=[]):
    """Falls ein "Zeit [s]"-Eintrag in daten existiert, wird das Offset von den Werten abgezogen.
    Andernfalls werden die Eintraege "Datum" und "Uhrzeit" erwartet.
    Aus diesen Eintraegen wird "Zeit [s]" beginnend von 0 berechnet und in daten gespeichert.
    Als Unterstuetzung kann das Format der aktuellen Daten in formatliste angegeben werden, damit
    die Eintraege korrekt interpretiert werden koennen. Gibt True zurueck, falls "Zeit [s]"
    erfolgreich angelegt/modifiziert werden konnte, sonst False.
    """
    if ('Zeit [s]' in daten):
        # Ziehe Offset ab und speichere die bereinigte Zeit wieder
        zeit = daten['Zeit [s]']
        zeit = [einzelzeit - zeit[0] for einzelzeit in zeit]
        daten.update([('Zeit [s]', zeit)])
        return True

    if (('Datum' in daten) and ('Uhrzeit' in daten)):
        datum = daten['Datum']
        uhrzeit = daten['Uhrzeit']
        zeit = None
        try:
            zeitwerte = [str(float(x)+float(y)) for x, y in zip(datum, uhrzeit)]
            zeit = SekundenAusDatumsangabenExtrahieren(daten=zeitwerte)
        except:
            pass

        if (zeit is not None):
            daten.update([('Zeit [s]', zeit)])
            return True

    return False



# -------------------------------------------------------------------------------------------------
def GespeicherterWertOderUebergabe(daten, bezeichnung, uebergabe):
    """Ueberpruefe, ob daten[bezeichnung] existiert, ansonsten erstelle es und speichere den Wert
    aus uebergabe dort (daten kann somit modifiziert werden). Gibt den (ggfs. erstellten) Wert
    von daten[bezeichnung] zurueck.
    """
    try:
        rueckgabe = daten[bezeichnung]
    except:
        rueckgabe = uebergabe
        daten.update([(bezeichnung, rueckgabe)])

    return rueckgabe



# -------------------------------------------------------------------------------------------------
def PraefixUmrechnungsfaktor(von, zu):
    """Extrahiert die Einheiten aus den beiden uebergebenen Strings von und zu. Es wird erwartet,
    dass beide Strings dem Muster "Bezeichnung [Einheit]" folgen, wobei Bezeichnung identisch ist.
    Bei vielen fuer geotechnische Laborversuche gebraeuchlichen Einheiten kann ein Umrechnungsfaktor
    zwischen den beiden Einheiten ermittelt werden. Falls ein Faktor ermittelt werden kann,
    wird dieser zurueckgegeben, sonst None.
    """
    from .konstanten import grad2rad

    if (von == zu):
        return 1.0

    startbloecke = von.split('[')
    zielbloecke = zu.split('[')
    if (startbloecke[0] != zielbloecke[0]):
        # Bezeichnung muss identisch sein
        return None

    einheit_start = startbloecke[1].split(']')[0]
    einheit_ziel = zielbloecke[1].split(']')[0]

    # (Zusammengesetzte) SI-Einheiten als Referenz mit 1.0 setzen
    referenz = {
        'Laenge': {'m': 1.0, 'cm': 100.0, 'mm': 1000.0},
        'Flaeche': {'m^2': 1.0, 'cm^2': 10000.0, 'mm^2': 1000000.0},
        'Volumen': {'m^3': 1.0, 'cm^3': 1000000.0, 'mm^3': 1000000000.0},
        'Drehung': {'Grad': 1.0, 'rad': 1.0/grad2rad},
        'Gewicht': {'kg': 1.0, 'g': 1000.0, 'mg': 1000000.0, 't': 0.001},
        'Zeit': {'s': 1.0, 'min': 1.0/60.0, 'h': 1.0/3600.0},
        'Kraft': {'N': 1.0, 'kN': 0.001, 'MN': 0.000001},
        'Spannung': {'N/m^2': 1.0, 'N/cm^2': 0.0001, 'N/mm^2': 0.000001, 'kN/m^2': 0.001, 'MN/m^2': 0.000001},
        'Dichte': {'kg/m^3': 1.0, 't/m^3': 0.001, 'kg/cm^3': 0.000001, 'g/cm^3': 0.001, 'Mg/m^3': 0.001},
        'Geschwindigkeit': {'m/s': 1.0, 'm/min': 60.0, 'm/h': 3600.0, 'km/h': 3.6, 'cm/s': 100.0, 'cm/min': 6000.0, 'cm/h': 360000.0, 'mm/s': 1000.0, 'mm/min': 60000.0, 'mm/h': 3600000.0},
        'Relativ': {'-': 1.0, '%': 100.0},
    }
    faktor_start = None
    faktor_ziel = None
    for gruppenschluessel in list(referenz.keys()):
        gruppe = referenz[gruppenschluessel]
        for schluessel in list(gruppe.keys()):
            if (schluessel == einheit_start):
                faktor_start = gruppe[schluessel]

            if (schluessel == einheit_ziel):
                faktor_ziel = gruppe[schluessel]

        if ((faktor_start is None) and (faktor_ziel is None)):
            continue
        elif ((faktor_start is None) or (faktor_ziel is None)):
            print('# Warnung: Beide Praefixeinheiten ' + einheit_start + ' und ' + einheit_ziel + ' muessen der gleichen (vorimplementierten) Gruppe angehoeren')
            return None
        else:
            break

    if ((faktor_start is None) or (faktor_ziel is None)):
        print('# Warnung: Einheiten nicht in den vorimplementierten Gruppen gefunden')
        return None
    else:
        return faktor_ziel/faktor_start



# -------------------------------------------------------------------------------------------------
def ZusatzdatenKopieren(quelle, ziel, zusatzdaten=['Datum', 'Dateiname', 'Bodenart', 'Bodenname',
    'Projektnummer', 'Projektname', 'Entnahmestelle', 'Entnahmetiefe', 'Tiefe']):
    """Jeder Eintrag aus zusatzdaten, der (nur) in der uebergebenen Struktur quelle enthalten ist,
    wird mit seinem Wert in die Struktur ziel kopiert (ziel wird modifiziert).
    """
    for eintrag in zusatzdaten:
        if ((eintrag in quelle) and (eintrag not in ziel)):
            ziel.update([(eintrag, quelle[eintrag])])


