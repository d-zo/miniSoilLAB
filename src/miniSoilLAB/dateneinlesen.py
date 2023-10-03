# -*- coding: utf-8 -*-
"""
dateneinlesen.py   v0.7 (2023-09)
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
def ExistiertDatei(dateiname):
    """Pruefe die Existenz einer Datei. Gibt True zurueck, falls die Datei vorhanden ist.
    """
    from pathlib import Path

    testdatei = Path(dateiname)
    if (testdatei.is_file()):
        return True
    else:
        return False



# -------------------------------------------------------------------------------------------------
def BodenmusterdateiEinlesen(dateiname):
    """Liest den Inhalt einer Bodenmuster-Datei (dateiname) ein, die in jeder Zeile durch Semikolons
    getrennt die drei Eintraege Bodenname, Dateimuster und Zielordner enthaelt.
    Gibt ein dict mit den Bodennamen als Schluessel zurueck, das fuer jeden Bodennamen die
    Eintraege Dateimuster und Zielordner enthaelt.
    """
    eintraege = dict()
    idx_leseversuch = 0
    max_leseversuche = 5
    try:
        with open(dateiname, 'r', encoding='utf-8') as eingabe:
            for idx_zeile, zeile in enumerate(eingabe):
                if (len(zeile) == 0):
                    continue

                if ((zeile == '\n') or (zeile == '\r\n')):
                    continue

                if (zeile[0] == '#'):
                    continue

                einzelteile = zeile.split(';')
                if (len(einzelteile) != 3):
                    idx_leseversuch += 1
                    print('# Warnung: Die folgende Zeile hat nicht genau 2 Semikolons und wird ignoriert:')
                    print(zeile)

                    if (idx_leseversuch == max_leseversuche):
                        print('# Fehler: Zuviele ungueltige Zeilen - Breche Lesevorgang ab')
                        break

                    continue

                schluessel = einzelteile[0].strip()
                if (schluessel in eintraege.keys()):
                    print('# Warnung: Eintrag in Zeile ' + str(idx_zeile) \
                        + ' wird ignoriert (Bodenname ' + schluessel + ' bereits eingelesen)')
                    continue

                eintraege.update([(schluessel, [einzelteile[1].strip(), einzelteile[2].strip()])])
    except FileNotFoundError:
        print('# Fehler: Bodenmuster-Datei konnte nicht gefunden/geoeffnet werden')
    except:
        print('# Fehler: Bodenmuster-Datei konnte nicht eingelesen werden')

    return eintraege



# -------------------------------------------------------------------------------------------------
def BodendatenMitSchluesselAusMusterEinlesen(muster, schluessel=None, ignoriere=['rohdaten', '.dta',
    '.eax', '.gds', '.tvc'], verarbeitet=True):
    """Lese alle Dateien der Boeden ein, die in muster hinterlegt sind (falls schluessel=None),
    oder nur diejenigen, die als Liste an schluessel uebergeben worden sind. Die Werte der Schluessel
    in muster entsprechen dem dateimuster und dem zielordner fuer den jeweiligen Bodennamen. Es
    werden alle Dateien ignoriert, in deren Namen sich ein in ignoriere definierter Begriff befindet.
    """
    from .datenstruktur import Datenstruktur

    if (schluessel is None):
        schluessel = muster.keys()

    bodendaten = Datenstruktur()
    for bodenname in schluessel:
        try:
            dateimuster, zielordner = muster[bodenname]
        except:
            print('# Warnung: ' + bodenname + ' ist kein gueltiger Schluessel fuer die uebergebenen Muster')
            continue

        tempboden = BodendatenEinlesen(bodenname=bodenname, dateimuster=dateimuster,
            zielordner=zielordner, ignoriere=ignoriere, verarbeitet=verarbeitet)
        if (tempboden is None):
            print('# Warnung: Boden ' + bodenname + ' ungueltig (Pfad/Muster korrekt?)')
            continue

        bodendaten.update(tempboden)

    return bodendaten



# -------------------------------------------------------------------------------------------------
def BodendatenEinlesen(bodenname, dateimuster, zielordner, ignoriere=['rohdaten', '.dta', '.eax',
    '.gds', '.tvc'], verarbeitet=True):
    """Lese alle Dateien aus dem zielordner ein, die dateimuster enthalten. Speichere die
    eingelesenen Dateien in einer Struktur mit dem Schluessel bodenname und gib diese zurueck.
    Es werden alle Dateien ignoriert, in deren Namen sich ein in ignoriere definierter Begriff
    befindet. Gibt None zurueck, falls keine Daten eingelesen werden koennen.
    """
    import os

    if (zielordner[-1] == os.sep):
        zielordner = zielordner[:-1]

    temp_dateiliste = ZieldateienFinden(zielordner=zielordner, dateimuster=dateimuster)
    dateiliste = []
    for dateiname in temp_dateiliste:
        ueberspringen = False
        for bezeichnung in ignoriere:
            if (bezeichnung in dateiname.lower()):
                ueberspringen = True
                break

        if (not ueberspringen):
            dateiliste += [dateiname]

    if (dateiliste == []):
        return None
    else:
        return BodendatenDateilisteEinlesen(bodenname=bodenname, dateiliste=dateiliste, verarbeitet=verarbeitet)



# -------------------------------------------------------------------------------------------------
def ListendateiEinlesen(dateiname):
    """Liest den Inhalt einer Listendatei (dateiname) ein, die eine Dateiliste fuer einen oder
    mehrere Boeden enthaelt. Die erste Zeile einer Liste enthaelt den Namen des Bodens mit einem
    abschliessenden Doppelpunkt und danach folgt eine Liste an Dateinamen (die nicht auf einem
    Doppelpunkt enden duerfen). Jede Zeile muss genau einem Dateinamen entsprechen, leer sein oder
    eine Kommentarzeile sein (Raute # als erstes Zeichen).
    Gibt ein dict mit den Bodennamen als Schluessel zurueck, das fuer jeden Bodennamen die
    Liste der dazugehoerigen Dateinamen enthaelt.
    """
    eintraege = dict()
    temp_bezeichnung = None
    temp_liste = []
    idx_leseversuch = 0
    max_leseversuche = 5
    try:
        with open(dateiname, 'r', encoding='utf-8') as eingabe:
            for idx_zeile, zeile in enumerate(eingabe):
                zeile = zeile.strip()

                if (len(zeile) == 0):
                    continue

                if (zeile.lstrip()[0] == '#'):
                    continue

                if ('#' in zeile):
                    zeile = zeile[:zeile.index('#')].rstrip()

                if (zeile.endswith(':')):
                    if (temp_bezeichnung is not None):
                        eintraege.update([(temp_bezeichnung, temp_liste)])

                    temp_bezeichnung = zeile[:-1]
                    temp_liste = []
                else:
                    if (temp_bezeichnung is None):
                        idx_leseversuch += 1
                        print('# Warnung: Bodenname vor der folgenden Datenzeile erwartet')
                        print(zeile)

                        if (idx_leseversuch == max_leseversuche):
                            print('# Fehler: Zuviele ungueltige Zeilen - Breche Lesevorgang ab')
                            break

                        continue

                    temp_liste += [zeile]

            if (temp_bezeichnung is not None):
                eintraege.update([(temp_bezeichnung, temp_liste)])
    except FileNotFoundError:
        print('# Fehler: Listendatei konnte nicht gefunden/geoeffnet werden')
    except:
        print('# Fehler: Listendatei konnte nicht eingelesen werden')

    return eintraege



# -------------------------------------------------------------------------------------------------
def BodendatenListeEinlesen(dateiname, verarbeitet=True):
    """Liest den Inhalt einer Listendatei (dateiname) ein, die eine Dateiliste fuer einen oder
    mehrere Boeden enthaelt. Die erste Zeile einer Liste enthaelt den Namen des Bodens mit einem
    abschliessenden Doppelpunkt und danach folgt eine Liste an Dateinamen (die nicht auf einem
    Doppelpunkt enden duerfen). Jede Zeile muss genau einem Dateinamen entsprechen, leer sein oder
    eine Kommentarzeile sein (Raute # als erstes Zeichen).
    Fuer alle Boeden werden alle Dateien eingelesen und in einer Struktur mit dem jeweiligen
    Bodennamen als Schluessel gespeichert. Diese Struktur wird zurueckgegeben.
    """
    from .datenstruktur import Datenstruktur

    bodendaten = Datenstruktur()
    bodenliste = ListendateiEinlesen(dateiname=dateiname)
    if (len(bodenliste) == {}):
        print('# Warnung: Keine Daten aus Listendatei ' + dateiname + ' eingelesen')
    else:
        for bodenname, dateiliste in bodenliste.items():
            tempboden = BodendatenDateilisteEinlesen(bodenname=bodenname, dateiliste=dateiliste,
                verarbeitet=verarbeitet)
            if (tempboden is None):
                print('# Warnung: Boden ' + bodenname + ' ungueltig (Dateinamen in Liste korrekt?)')
                continue

            bodendaten.update(tempboden)

    return bodendaten



# -------------------------------------------------------------------------------------------------
def BasispfadErmitteln(dateiliste):
    """Finde den laengsten gemeinsamen Pfad aller Dateien in dateiliste und
    gebe ihn zurueck.
    """
    basispfad = ''
    # Alle gemeinsamen Zeichen finden
    num_pruefstellen = min(len(pfad) for pfad in dateiliste)
    for idx_pos in range(num_pruefstellen):
        if (all([(pfad[idx_pos] == dateiliste[0][idx_pos]) for pfad in dateiliste])):
            basispfad += dateiliste[0][idx_pos]
        else:
            break

    # Aus den gemeinsamen Zeichen den letzten Pfad extrahieren
    # (d.h. alle Zeichen am Ende entfernen, die keinen Unterordner andeuten)
    while (basispfad != ''):
        if (basispfad.endswith('/') or basispfad.endswith('\\')):
            break

        basispfad = basispfad[:-1]

    return basispfad



# FIXME: Andere Position/Datei
# -------------------------------------------------------------------------------------------------
def StrukturZuSchluesselInBasisstrukturHinzufuegen(basisstruktur, schluessel, struktur):
    """Erwartet eine basisstruktur und eine weitere struktur. Pruefe, ob schluessel in basisstruktur
    existiert (ggfs. erzeugen) und fuege die struktur dort mit der Bezeichnung "_Ref_" und der
    kleinsten, nicht vergebenen dreistelligen Nummer ab 001 hinzu. Aendert basisstruktur und
    gibt die tatsaechlich gewaehlte Bezeichnung zurueck.
    """
    from .datenstruktur import Datenstruktur

    if (schluessel not in basisstruktur):
        refid = '_Ref_' + str(1).zfill(3)
        basisstruktur.update([(schluessel, Datenstruktur({refid: struktur}))])
    else:
        refid = '_Ref_' + str(len(list(basisstruktur[schluessel].keys()))+1).zfill(3)
        basisstruktur[schluessel].update({refid: struktur})

    return refid



# -------------------------------------------------------------------------------------------------
def BodendatenDateilisteEinlesen(bodenname, dateiliste, verarbeitet=True):
    """Lese alle Dateien aus dateiliste ein, speichere die eingelesenen Daten in einer Struktur mit
    dem Schluessel bodenname und gib diese zurueck.
    """
    from .konstanten import debugmodus
    from .datenstruktur import Datenstruktur
    from .kennwerte import Kennwertberechnungen

    if (debugmodus):
        print('# --- Einzulesende Dateien: ' + bodenname)
        for idx_datei, datei in enumerate(dateiliste):
            print(str(idx_datei+1).zfill(2) + ') ' + datei)

        print('# ---')

    bodendaten = Datenstruktur()
    for dateiname in dateiliste:
        eingelesen = DateiEinlesen(dateiname=dateiname, verarbeitet=False)
        if (eingelesen is not None):
            if (len(eingelesen.keys()) == 0):
                print('# Warnung: Keine Daten aus aktueller Datei eingelesen')
                continue

            schluesselliste = list(eingelesen.keys())
            if (len(schluesselliste) > 1):
                print('# Warnung: Mehrere Schluessel in einer Datei nicht unterstuetzt - ignoriere Eintraege')
                continue

            # Es existiert genau ein Schluessel
            schluessel = schluesselliste[0]
            StrukturZuSchluesselInBasisstrukturHinzufuegen(basisstruktur=bodendaten,
                schluessel=schluessel, struktur=eingelesen[schluessel])

    if (len(bodendaten.keys()) == 0):
        return None

    bodendaten.update([('Basisordner', BasispfadErmitteln(dateiliste))])

    if (debugmodus):
        print('# Hinweis: Alle Dateien zu ' + bodenname + ' eingelesen')

    if (verarbeitet):
        if (debugmodus):
            print('# --- Berechne Kennwerte zu ' + bodenname)

        if (not Kennwertberechnungen(daten=bodendaten)):
            print('# Warnung: Es konnten nicht alle Kennwerte fuer Boden ' + bodenname + ' berechnet werden')

    boden = Datenstruktur()
    boden.update([(bodenname, bodendaten)])

    if (debugmodus):
        print('# ---')

    return boden



# -------------------------------------------------------------------------------------------------
def DateiEinlesen(dateiname, verarbeitet=True):
    """Lese die Datei namens dateiname ein, sofern es sich um einen unterstuetzten Dateityp/-namen
    handelt.
    """
    from .konstanten import debugmodus
    from .xlshilfen import LeseXLSDaten
    from .rohdaten import LeseDTADaten, LeseEAXDaten, LeseGDSDaten, LeseTVCDaten, LeseKVSDaten

    if ((dateiname[-3:].lower() == 'xls') or (dateiname[-4:].lower() == 'xlsx')):
        ignoriere = ['rohdaten']
        if (not verarbeitet):
            ignoriere = []

        return LeseXLSDaten(dateiname=dateiname, verarbeitet=verarbeitet, ignoriere=ignoriere)
    elif (dateiname[-3:].lower() == 'dta'):
        if (debugmodus):
            print('# - LeseDTA: ' + dateiname)

        return LeseDTADaten(dateiname=dateiname)
    elif (dateiname[-3:].lower() == 'eax'):
        if (debugmodus):
            print('# - LeseEAX: ' + dateiname)

        return LeseEAXDaten(dateiname=dateiname)
    elif (dateiname[-3:].lower() == 'gds'):
        if (debugmodus):
            print('# - LeseGDS: ' + dateiname)

        return LeseGDSDaten(dateiname=dateiname)
    elif (dateiname[-3:].lower() == 'tvc'):
        if (debugmodus):
            print('# - LeseTVC: ' + dateiname)

        return LeseTVCDaten(dateiname=dateiname)
    elif (dateiname[-3:].lower() == 'kvs'):
        if (debugmodus):
            print('# - LeseKVS: ' + dateiname)

        return LeseKVSDaten(dateiname=dateiname)
    else:
        #print('# Hinweis: Ignoriere ' + dateiname)
        return None



# -------------------------------------------------------------------------------------------------
def ZieldateienFinden(zielordner, dateimuster, ignoriereOrdnernamen=['alt']):
    """Ermittle im zielordner und allen Unterordnern alle Dateien, deren Namen dateimuster enthaelt.
    Falls ignoriereOrdnernamen keine leere Liste ist, werden alle Unterordner in der Liste ignoriert
    (deren Name einem der Eintraege entspricht).
    Gibt eine Liste aller Dateinamen der so ausgewaehlten Dateien zurueck.

    Kann auch zum Testen von Bodenmusterdatei-Eintraegen verwendet werden. Wenn Pfad und regulaerer
    Ausdruck richtig gewaehlt sind, sollten exakt die gewuenschten Dateien aufgelistet/eingelesen
    werden. Fuer die Wahl von sinnvollen regulaeren Ausdrucken sei auf das Python-Modul re und
    die offizielle Dokumentation verwiesen (Standard Library Reference unter https://docs.python.org)
    """
    from os import walk as os_walk
    from os import sep as os_sep
    from os.path import join as os_join
    from re import compile as re_compile
    from re import search as re_search

    if ((dateimuster == '*') or (dateimuster == '*.*')):
        dateimuster = ''

    if (zielordner == ''):
        zielordner = '.'

    if (zielordner[-1] != os_sep):
        zielordner += os_sep

    try:
        remuster = re_compile(dateimuster)
    except:
        print('# Warnung: Fehler im regulaeren Ausdruck \"' + dateimuster + '\"')
        return []

    zieldateiliste = []
    for (pfad, _, dateiliste) in os_walk(zielordner):
        # Ignoriere alle Dateien aus (Unter-)ordner eines Eintrags aus ignoriereOrdnernamen
        unterpfad = pfad[len(zielordner):].split(os_sep)
        if (any([pfadteil in ignoriereOrdnernamen for pfadteil in unterpfad])):
            continue

        for datei in dateiliste:
            if (re_search(remuster, datei)):
                zieldateiliste += [os_join(pfad, datei)]

    if (len(zieldateiliste) > 0):
        zieldateiliste.sort()

    return zieldateiliste



# -------------------------------------------------------------------------------------------------
def DatensatzEinlesen(dateiname):
    """Lade eine JSON-formatierte Datei, die mit Datensatz_Speichern erstellt worden ist. Gib die
    eingelesene Struktur zurueck.
    """
    return _JSONDateiEinlesen(dateiname, bezeichnung='Datensatz')



# -------------------------------------------------------------------------------------------------
def _JSONDateiEinlesen(dateiname, bezeichnung='Datei'):
    """Lade eine JSON-formatierte Datei und gib die eingelesene Struktur zurueck.
    """
    import json

    def Eingabedaten_json(json_objekt):
        """Hilfsfunktion zur Umwandlung von unterstuetzten Strukturen beim Einlesen von
        JSON-formatierten Dateien.
        """
        from .datenstruktur import Datenstruktur

        if (isinstance(json_objekt, dict)):
            return Datenstruktur(json_objekt)
        else:
            return json_objekt

    eingelesen = None
    try:
        with open(dateiname, 'r', encoding='utf-8') as eingabe:
            eingelesen = json.load(eingabe, object_hook=Eingabedaten_json)
    except FileNotFoundError:
        print('# Fehler: Datei konnte nicht gefunden/geoeffnet werden')
    except Exception as e:
        print('# Fehler: Datei ' + dateiname + ' konnte nicht eingelesen werden')
        print(e)

    return eingelesen



# -------------------------------------------------------------------------------------------------
def _DatensatzSpeichern(datensatz, dateiname):
    """Speichere die Stuktur datensatz als JSON-formatierte Datei namens dateiname.
    """
    import json

    class DatenstrukturEncoder(json.JSONEncoder):
        """Einfacher Encoder fuer Objekte der Datenstruktur-Klasse. Kovertiert Datenstruktur-Elemente
        in dicts und schreibt alle Listeneintraege in eine Zeile.
        """
        def default(self, o):
            return o.__dict__

        def iterencode(self, eintrag, _one_shot=False):
            listenstufe = 0
            for dumpstring in super().iterencode(eintrag, _one_shot=_one_shot):
                if (dumpstring[0] =='['):
                    listenstufe += 1
                    dumpstring = ''.join([teil.strip() for teil in dumpstring.split('\n')])

                elif (listenstufe > 0):
                    dumpstring = ' '.join([teil.strip() for teil in dumpstring.split('\n')])
                    if (dumpstring == ' '):
                        continue

                    if (dumpstring[-1] == ','):
                        dumpstring = dumpstring[:-1] + self.item_separator
                    elif (dumpstring[-1] == ':'):
                        dumpstring = dumpstring[:-1] + self.key_separator

                if (dumpstring[-1] == ']'):
                    listenstufe -= 1

                yield dumpstring

    with open(dateiname, 'w') as ausgabe:
        json.dump(datensatz, ausgabe, cls=DatenstrukturEncoder, indent=1)



# -------------------------------------------------------------------------------------------------
def DatensatzSpeichern(datensatz, dateiname, refspeichern=True):
    """Speichere die Stuktur datensatz als JSON-formatierte Datei namens dateiname. Mit
    respeichern=False werden die Rohdaten und Verweise darauf nicht der Datei gespeichert.
    """
    import copy
    from .datenstruktur import EintraegeEntfernen

    ausgabedaten = datensatz
    if (not refspeichern):
        ausgabedaten = copy.deepcopy(datensatz)
        EintraegeEntfernen(mod_struktur=ausgabedaten, entfernen_start=['_Ref_', '_Refwahl'])

    _DatensatzSpeichern(datensatz=ausgabedaten, dateiname=dateiname)


