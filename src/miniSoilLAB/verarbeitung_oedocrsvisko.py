# -*- coding: utf-8 -*-
"""
verarbeitung_oedocrsvisko.py   v0.3 (2023-09)
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
def OedoCRSViskoStruktur():

    import copy
    from .datenstruktur import Datenstruktur

    struktur = Datenstruktur({
        'Hoehe [mm]': [],
        'Durchmesser [mm]': [],
        'Trockenmasse [g]': [],
        'Zeit [s]': [],
        'Spannung [kN/m^2]': [],
        'Setzung [mm]': []
    })
    return copy.deepcopy(struktur)



# -------------------------------------------------------------------------------------------------
def _KennwerteOedoCRSVisko(daten, refwerte):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo-CRS-Visko
    und speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
    """
    from math import pi
    from .datenstruktur import Datenstruktur
    from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
    from .parameterbestimmung import _ViskohypoplastischCRSPunkte

    # FIXME: Einstellbare Parameter
    param_refidx = 9
    param_intervallgroesse = 25
    param_p1logverhaeltnis = 0.5
    param_p5logverhaeltnis = 0.5

    anfangshoehe = daten['Hoehe [mm]']
    durchmesser = daten['Durchmesser [mm]']
    trockenmasse = daten['Trockenmasse [g]']
    zeit = daten['Zeit [s]']
    setzung = daten['Setzung [mm]']
    spannung = daten['Spannung [kN/m^2]']

    # Extrahiere Uebergabewerte
    korndichte = refwerte['Korndichte [g/cm^3]']

    tol = 1e-6

    volumen_e = anfangshoehe * pi*(durchmesser/2.0)**2 / 1000.0 # [cm^3]
    daten.update([('Volumen [cm^3]', volumen_e)])

    if (abs(volumen_e) < tol):
        print('# Warnung: Volumen annaehernd Null')
        return False
    # Zeit ueberpruefen sollte reichen, da Zeit-Kraft-Setzung als Gruppe eingelesen wird
    if (len(zeit) < param_refidx+1):
        print('# Warnung: Zu wenig Werte')
        return False

    if (abs(zeit[param_refidx]) < tol):
        print('# Warnung: Zeit annaehernd Null')
        return False

    pos_maxwert = spannung.index(max(spannung))
    if (pos_maxwert != len(spannung)-1):
        print('# Hinweis: Verwerfe Werte nach Maximalkraft (ab Index ' + str(pos_maxwert) +')')
        zeit = zeit[:pos_maxwert+1]
        daten.update([('Zeit [s]', zeit)])
        spannung = spannung[:pos_maxwert+1]
        daten.update([('Spannung [kN/m^2]', spannung)])
        setzung = setzung[:pos_maxwert+1]
        daten.update([('Setzung [mm]', setzung)])

    if (pos_maxwert < param_refidx):
        print('# Warnung: Zu wenig gueltige Werte')
        return False

    setzungsrate = setzung[9]*60.0/zeit[9] # [mm/min]
    daten.update([('Stauchungsrate [mm/min]', setzungsrate)])

    trockendichte = trockenmasse/volumen_e
    if (abs(trockendichte) < tol):
        print('# Warnung: Trockendichte annaehernd Null')
        return False

    porenzahl_e = korndichte/trockendichte - 1.0
    porenzahl = [porenzahl_e - (1.0 + porenzahl_e)*einzelsetzung/anfangshoehe for einzelsetzung in setzung]
    daten.update([('Porenzahl [-]', porenzahl)])

    einstellungen = GespeicherterWertOderUebergabe(daten=daten,
        bezeichnung='Einstellungen', uebergabe=Datenstruktur())

    intervallgroesse = GespeicherterWertOderUebergabe(daten=einstellungen,
        bezeichnung='Intervallgroesse', uebergabe=param_intervallgroesse)
    p1logverhaeltnis = GespeicherterWertOderUebergabe(daten=einstellungen,
        bezeichnung='P1 Logverhaeltnis', uebergabe=param_p1logverhaeltnis)
    p5logverhaeltnis = GespeicherterWertOderUebergabe(daten=einstellungen,
        bezeichnung='P5 Logverhaeltnis', uebergabe=param_p5logverhaeltnis)

    idxliste = _ViskohypoplastischCRSPunkte(spannungen=spannung, intervallgroesse=intervallgroesse,
        p1logverhaeltnis=p1logverhaeltnis, p5logverhaeltnis=p5logverhaeltnis)
    if (idxliste != []):
        punkte = Datenstruktur()
        punktspannung = [spannung[idx] for idx in idxliste]
        punktporenzahl = [porenzahl[idx] for idx in idxliste]
        punkte.update([('Indizes', idxliste)])
        punkte.update([('Spannung [kN/m^2]', punktspannung)])
        punkte.update([('Porenzahl [-]', punktporenzahl)])
        daten.update([('Punkte', punkte)])

    return True



# -------------------------------------------------------------------------------------------------
def KennwerteOedoCRSVisko(daten, refwerte):
    """Erwartet eine JSON-Struktur daten, in der die Daten zu Oedo-CRS-Visko-Versuchen gespeichert
    sind und aktualisiert/berechnet die entsprechenden Kennwerte.
    """
    from .konstanten import debugmodus
    from .datenstruktur import DatenstrukturExtrahieren
    from .verarbeitung_hilfen import ZusatzdatenKopieren

    erfolgreich = False

    if ('_Refwahl' not in daten):
        if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001')

        daten.update([('_Refwahl', '_Ref_001')])

    extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=OedoCRSViskoStruktur(), refwahl=daten['_Refwahl'])
    if (extrahierte_daten):
        daten.update(extrahierte_daten)
        ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten)
        _KennwerteOedoCRSVisko(daten=daten, refwerte=refwerte)
        erfolgreich = True

    return erfolgreich



# -------------------------------------------------------------------------------------------------
def VorbereitungOedoCRSVisko(daten):
    """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Oedo-CRS-Visko-Versuchen
    gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
    eine spaetere Weiterverarbeitung zu haben.
    """
    import copy
    from math import pi
    from .datenstruktur import DictStrukturPruefenUndAngleichen, DictStrukturGleichOderTeilmenge
    from .datenstruktur import ZielgroesseFindenUndAktualisieren
    from .verarbeitung_hilfen import SekundenOhneOffsetBereitstellen

    testdaten = copy.deepcopy(daten)
    if (not DictStrukturPruefenUndAngleichen(ref_dict=OedoCRSViskoStruktur(), test_dict=testdaten, warnung=False)):
        # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
        ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Trockenmasse mit Behaelter', einheit='g')
        ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Behaeltermasse', einheit='g')
        ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Kraft', einheit='kN')
        # Zielgroessen aus Alternativgroessen berechnen (falls erforderlich)
        try:
            durchmesser = testdaten['Durchmesser [mm]']
        except KeyError as errormessage:
            print('# Warnung: Mindestens ein erforderlicher Wert in Oedo-CRS-Visko nicht vorhanden - ' + str(errormessage))
            return

        try:
            gesamttrockenmasse = testdaten['Trockenmasse mit Behaelter [g]']
            behaeltermasse = testdaten['Behaeltermasse [g]']
            testdaten.update([('Trockenmasse [g]', gesamttrockenmasse - behaeltermasse)])
        except:
            pass

        try:
            kraft = testdaten['Kraft [kN]']
            druckflaeche = pi*(durchmesser/2000.0)**2 # [m^2]
            testdaten.update([('Spannung [kN/m^2]', [einzelkraft/druckflaeche for einzelkraft in kraft])])
            del testdaten['Kraft [kN]']
        except:
            pass

        SekundenOhneOffsetBereitstellen(daten=testdaten)

    if (DictStrukturGleichOderTeilmenge(ref_dict=OedoCRSViskoStruktur(), test_dict=testdaten, warnung=True)):
        # Referenz an daten zu den modifizierten Daten aendern
        daten.clear()
        daten.update(testdaten)
    else:
        print('# Warnung: Struktur der Oedo-CRS-Visko-Daten ist ungueltig')


