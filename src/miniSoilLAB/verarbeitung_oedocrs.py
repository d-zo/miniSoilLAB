# -*- coding: utf-8 -*-
"""
verarbeitung_oedocrs.py   v0.4 (2023-09)
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
def OedoCRSStruktur():

    import copy
    from .datenstruktur import Datenstruktur

    struktur = Datenstruktur({
        'Oedo-dicht': Datenstruktur({
            'Hoehe [mm]': [],
            'Durchmesser [mm]': [],
            'Masse [g]': [],
            'Schergeschwindigkeit [mm/min]': [],
            'Setzung [mm]': [],
            'Spannung [kN/m^2]': []
        }),
        'Oedo-locker': Datenstruktur({
            'Hoehe [mm]': [],
            'Durchmesser [mm]': [],
            'Masse [g]': [],
            'Schergeschwindigkeit [mm/min]': [],
            'Setzung [mm]': [],
            'Spannung [kN/m^2]': []
        })
    })
    return copy.deepcopy(struktur)



# -------------------------------------------------------------------------------------------------
def _KennwerteOedoCRS(daten, refwerte):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo-CRS und
    speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
    """
    from math import pi
    from .konstanten import g

    # Extrahiere Uebergabewerte
    korndichte = refwerte['Korndichte [g/cm^3]']

    tol = 1e-6

    for oedo_variante in ['Oedo-locker', 'Oedo-dicht']:
        oedo = daten[oedo_variante]
        anfangshoehe = oedo['Hoehe [mm]']
        durchmesser = oedo['Durchmesser [mm]']
        masse = oedo['Masse [g]']
        vscher = oedo['Schergeschwindigkeit [mm/min]']
        setzung = oedo['Setzung [mm]']

        #spannung = oedo['Spannung [kN/m^2]']
        spannungsoffset = 0.0 # kN/m^2
        druckflaeche = pi*(durchmesser/2000.0)**2 # [m^2]

        ref_oedo = daten[daten['_Refwahl']][oedo_variante]
        if ('Gewicht Kopfplatte [g]' in ref_oedo):
            spannungsoffset += ref_oedo['Gewicht Kopfplatte [g]']*g/1e6/druckflaeche

        if ('Kraft Startwert [kN]' in ref_oedo):
            spannungsoffset += ref_oedo['Kraft Startwert [kN]']/druckflaeche

        oedo.update([('Spannung [kN/m^2]', [spannungsoffset+tmp_spannung for tmp_spannung in oedo['Spannung [kN/m^2]']])])

        volumen = anfangshoehe * pi*(durchmesser/2.0)**2 / 1000.0 # [cm^3]
        if (abs(masse) < tol):
            print('# Warnung: Masse in ' + oedo_variante + ' annaehernd Null')
            return False

        if (abs(volumen) < tol):
            print('# Warnung: Volumen in ' + oedo_variante + ' annaehernd Null')
            return False

        trockendichte = masse/volumen
        porenzahl_anfang = korndichte/trockendichte - 1.0
        stauchung = [100.0*(temp_setzung - setzung[0])/anfangshoehe for temp_setzung in setzung]
        oedo.update([('Stauchung [%]', stauchung)])
        # FIXME: Richtig? (siehe auch oedo)
        #porenzahlen = [porenzahl_anfang - (temp_setzung - setzung[0])/anfangshoehe * (1.0 + porenzahl_anfang) for temp_setzung in setzung]
        porenzahlen = [(anfangshoehe - (tempsetzung-setzung[0]))/anfangshoehe * (porenzahl_anfang + 1.0) - 1.0 for tempsetzung in setzung]
        oedo.update([('Porenzahl [-]', porenzahlen)])

    return True



# -------------------------------------------------------------------------------------------------
def KennwerteOedoCRS(daten, refwerte):
    """Erwartet eine JSON-Struktur daten, in der die Daten zu Oedo-CRS-Versuchen gespeichert sind
    und aktualisiert/berechnet die entsprechenden Kennwerte.
    """
    from .konstanten import debugmodus
    from .datenstruktur import DatenstrukturExtrahieren
    from .verarbeitung_hilfen import ZusatzdatenKopieren

    erfolgreich = False

    if ('_Refwahl' not in daten):
        if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001')

        daten.update([('_Refwahl', '_Ref_001')])

    extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=OedoCRSStruktur(), refwahl=daten['_Refwahl'])
    if (extrahierte_daten):
        daten.update(extrahierte_daten)
        ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten)
        _KennwerteOedoCRS(daten=daten, refwerte=refwerte)
        erfolgreich = True

    return erfolgreich



# -------------------------------------------------------------------------------------------------
def VorbereitungOedoCRS(daten):
    """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Oedo-CRS-Versuchen
    gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
    eine spaetere Weiterverarbeitung zu haben.
    """
    import copy
    from math import pi
    from .datenstruktur import DictStrukturPruefenUndAngleichen, DictStrukturGleichOderTeilmenge
    from .datenstruktur import ZielgroesseFindenUndAktualisieren
    from .verarbeitung_hilfen import ImportiertesDatumFormatieren

    testdaten = copy.deepcopy(daten)
    if (not DictStrukturPruefenUndAngleichen(ref_dict=OedoCRSStruktur(), test_dict=testdaten, warnung=False)):
        for oedo_variante in ['Oedo-locker', 'Oedo-dicht']:
            try:
                belastung = testdaten[oedo_variante]
                durchmesser = belastung['Durchmesser [mm]']
            except KeyError as errormessage:
                print('# Warnung: Mindestens ein erforderlicher Wert in Oedo-CRS nicht vorhanden - ' + str(errormessage))
                return

            # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
            ZielgroesseFindenUndAktualisieren(daten=belastung, bezeichnung='Kraft', einheit='kN')
            ZielgroesseFindenUndAktualisieren(daten=belastung, bezeichnung='Weg', einheit='mm')
            try:
                setzung = belastung['Weg [mm]']
                kraft = belastung['Kraft [kN]']
                druckflaeche = pi*(durchmesser/2000.0)**2 # [m^2]
                belastung.update([('Setzung [mm]', setzung)])
                belastung.update([('Spannung [kN/m^2]', [einzelkraft/druckflaeche for einzelkraft in kraft])])
                del belastung['Weg [mm]']
                del belastung['Kraft [kN]']
            except:
                pass

    if ('Zeitwert' in testdaten):
        testdaten.update([('Datum', ImportiertesDatumFormatieren(datum=testdaten['Zeitwert'],
            ausgabeformat='%B %Y'))])
        del testdaten['Zeitwert']

    if (DictStrukturGleichOderTeilmenge(ref_dict=OedoCRSStruktur(), test_dict=testdaten, warnung=True)):
        # Referenz an daten zu den modifizierten Daten aendern
        daten.clear()
        daten.update(testdaten)
    else:
        print('# Warnung: Struktur der Oedo-CRS-Daten ist ungueltig')


