# -*- coding: utf-8 -*-
"""
verarbeitung_atterberg.py   v0.3 (2023-09)
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
def AtterbergStruktur():

    import copy
    from .datenstruktur import Datenstruktur

    struktur = Datenstruktur({
        'Wassergehalt [%]': [],
        'Ueberkornanteil > 0,4mm [%]': [],
        'Daten-Fliessgrenze': Datenstruktur({
            'Schlaege-Anzahl [-]': [],
            'Feuchtmasse mit Behaelter [g]': [],
            'Trockenmasse mit Behaelter [g]': [],
            'Behaeltermasse [g]': []
        }),
        'Daten-Ausrollgrenze': Datenstruktur({
            'Feuchtmasse mit Behaelter [g]': [],
            'Trockenmasse mit Behaelter [g]': [],
            'Behaeltermasse [g]': []
        })
    })
    return copy.deepcopy(struktur)



# -------------------------------------------------------------------------------------------------
def _KennwerteAtterberg(daten):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Atterberg und
    speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
    """
    from math import log10

    wassergehalt_probe = daten['Wassergehalt [%]']
    ueberkornanteil_probe = daten['Ueberkornanteil > 0,4mm [%]']

    fliess = daten['Daten-Fliessgrenze']
    ausroll = daten['Daten-Ausrollgrenze']

    schlaege = fliess['Schlaege-Anzahl [-]']
    massefeucht_f = fliess['Feuchtmasse mit Behaelter [g]']
    massetrocken_f = fliess['Trockenmasse mit Behaelter [g]']
    massebehaelter_f = fliess['Behaeltermasse [g]']
    massefeucht_a = ausroll['Feuchtmasse mit Behaelter [g]']
    massetrocken_a = ausroll['Trockenmasse mit Behaelter [g]']
    massebehaelter_a = ausroll['Behaeltermasse [g]']

    tol = 1e-6
    # ----------------------- Fliessgrenze -----------------------
    if (any([(abs(massetrocken_f[idx]-massebehaelter_f[idx]) < tol) for idx in range(len(massefeucht_f))])):
        print('# Warnung: Behaeltermasse und Trockenmasse fuer Fliessgrenze fast identisch')
        return False

    wassergehalt_f = [100.0*(massefeucht_f[idx]-massetrocken_f[idx])/(massetrocken_f[idx]-massebehaelter_f[idx]) for idx in range(len(massefeucht_f))]
    fliess.update([('Wassergehalt [%]', wassergehalt_f)])

    if (any([(schlag < tol) for schlag in schlaege])):
        print('# Warnung: Schlaganzahl muss eine ganze Zahl groesser als Null sein')
        return False

    logschlaege = [log10(schlag) for schlag in schlaege]
    sumlog2schlaege = sum([schlag**2 for schlag in logschlaege])
    sumlogschlaegewasser = sum([logschlaege[idx]*wassergehalt_f[idx] for idx in range(len(logschlaege))])
    A_wert = ((len(schlaege)*sumlogschlaegewasser)-(sum(logschlaege)*sum(wassergehalt_f))) / ((len(schlaege)*sumlog2schlaege)-(sum(logschlaege)**2))
    B_wert = (sum(wassergehalt_f)-(A_wert*sum(logschlaege)))/len(logschlaege)

    fliess.update([('A-Wert [-]', A_wert)])
    fliess.update([('B-Wert [-]', B_wert)])

    if ((schlaege[0] == schlaege[1]) and (schlaege[1] == schlaege[2])):
        # Einpunktmethode nach DIN 18122-1 Gleichung 5 und Anmerkungen
        wassergehalt_mittel = sum(wassergehalt_f)/len(wassergehalt_f)
        einpunktexp = 0.112
        if (wassergehalt_mittel < 40.0):
            einpunktexp = 0.14

        if (wassergehalt_mittel > 60.0):
            einpunktexp = 0.1

        fliess.update([('Exponent-Einpunktmethode [-]', einpunktexp)])
        # Nur die ersten drei Werte beruecksichtigen
        fliessgrenze = sum(wassergehalt_f[:3])/3.0 * (schlaege[0]/25.0)**einpunktexp
    else:
        fliessgrenze = B_wert + log10(25)*A_wert

    daten.update([('Fliessgrenze [%]', fliessgrenze)])

    # ---------------------- Ausrollgrenze -----------------------
    if (any([(abs(massetrocken_a[idx]-massebehaelter_a[idx]) < tol) for idx in range(len(massefeucht_a))])):
        print('# Warnung: Behaeltermasse und Trockenmasse fuer Ausrollgrenze fast identisch')
        return False

    wassergehalt_a = [100.0*(massefeucht_a[idx]-massetrocken_a[idx])/(massetrocken_a[idx]-massebehaelter_a[idx]) for idx in range(len(massefeucht_a))]
    ausroll.update([('Wassergehalt [%]', wassergehalt_a)])
    ausrollgrenze = sum(wassergehalt_a)/len(wassergehalt_a)
    daten.update([('Ausrollgrenze [%]', ausrollgrenze)])

    if (abs(100.0 - ueberkornanteil_probe) < tol):
        print('# Warnung: Ueberkornanteil > 0,4mm annaehernd 100%')
        return False

    plastizitaetszahl = fliessgrenze - ausrollgrenze
    if (abs(plastizitaetszahl) < tol):
        print('# Warnung: Plastizitaetszahl annaehernd Null')
        return False

    wassergehalt_korr = 100.0*wassergehalt_probe/(100.0 - ueberkornanteil_probe)
    konsistenzzahl = (fliessgrenze - wassergehalt_korr)/plastizitaetszahl
    daten.update([('Plastizitaetszahl [%]', plastizitaetszahl)])
    daten.update([('Konsistenzzahl [-]', konsistenzzahl)])
    return True



# -------------------------------------------------------------------------------------------------
def KennwerteAtterberg(daten, refwerte=None):
    """Erwartet eine JSON-Struktur daten, in der die Daten zur Bestimmung der Fliessgrenzen
    nach Atterberg gespeichert sind und aktualisiert/berechnet die entsprechenden Kennwerte.
    """
    from .konstanten import debugmodus
    from .datenstruktur import DatenstrukturExtrahieren
    from .verarbeitung_hilfen import ZusatzdatenKopieren

    erfolgreich = False

    if ('_Refwahl' not in daten):
        if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001')

        daten.update([('_Refwahl', '_Ref_001')])

    extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=AtterbergStruktur(), refwahl=daten['_Refwahl'])
    if (extrahierte_daten):
        daten.update(extrahierte_daten)
        ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten)
        _KennwerteAtterberg(daten=daten)
        erfolgreich = True

    return erfolgreich



# -------------------------------------------------------------------------------------------------
def VorbereitungAtterberg(daten):
    """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zur Bestimmung der
    Fliessgrenzen nach Atterberg gespeichert sind. Die uebergebene Struktur wird modifiziert, um
    eine einheitliche Struktur fuer eine spaetere Weiterverarbeitung zu haben.
    """
    import copy
    from .datenstruktur import DictStrukturPruefenUndAngleichen

    testdaten = copy.deepcopy(daten)
    if (DictStrukturPruefenUndAngleichen(ref_dict=AtterbergStruktur(), test_dict=testdaten, warnung=True)):
        # Referenz an daten zu den modifizierten Daten aendern
        daten.clear()
        daten.update(testdaten)
    else:
        print('# Warnung: Struktur der Atterberg-Daten ist ungueltig')


