# -*- coding: utf-8 -*-
"""
verarbeitung_hypo.py   v0.3 (2023-09)
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
def HypoStruktur():

    import copy
    from .datenstruktur import Datenstruktur

    struktur = Datenstruktur({
        'Schuettkegel': Datenstruktur({
            'Korndichte [g/cm^3]': [],
            'Porenzahl-max [-]': [],
            'Porenzahl-min [-]': [],
            'Reibungswinkel-krit [Grad]': []
        }),
        'Oedo-locker': Datenstruktur({
            'Masse [g]': [],
            'Hoehe [mm]': [],
            'Durchmesser [mm]': [],
            'Setzung [mm]': [],
            'Spannung [kN/m^2]': []
        }),
        'Oedo-dicht': Datenstruktur({
            'Masse [g]': [],
            'Hoehe [mm]': [],
            'Durchmesser [mm]': [],
            'Setzung [mm]': [],
            'Spannung [kN/m^2]': []
        }),
        'Triax-D': Datenstruktur({
            'Porenzahl-Peak [-]': [],
            'Spannung-Peak-eff [kN/m^2]': [],
            'Dilatanzwinkel [Grad]': [],
            'Reibungswinkel-Peak-locker [Grad]': [],
            'Reibungswinkel-Peak-dicht [Grad]': []
        })
    })
    return copy.deepcopy(struktur)



# -------------------------------------------------------------------------------------------------
def _KennwerteHypo(daten):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage
    Auswertung-Hypoplastisch und speichere sie in der uebergebenen Struktur daten, sofern diese
    den Vorgaben entspricht.
    """
    from math import pi

    schuettkegel = daten['Schuettkegel']
    korndichte = schuettkegel['Korndichte [g/cm^3]']
    e_max = schuettkegel['Porenzahl-max [-]']
    e_min = schuettkegel['Porenzahl-min [-]']

    oedo_locker = daten['Oedo-locker']
    masse_oedo_l = oedo_locker['Masse [g]']
    hoehe_oedo_l = oedo_locker['Hoehe [mm]']
    durchmesser_oedo_l = oedo_locker['Durchmesser [mm]']
    setzung_oedo_l = oedo_locker['Setzung [mm]']

    oedo_dicht = daten['Oedo-dicht']
    masse_oedo_d = oedo_dicht['Masse [g]']
    hoehe_oedo_d = oedo_dicht['Hoehe [mm]']
    durchmesser_oedo_d = oedo_dicht['Durchmesser [mm]']
    setzung_oedo_d = oedo_dicht['Setzung [mm]']

    triax = daten['Triax-D']
    e_peak = triax['Porenzahl-Peak [-]']

    # Erforderliche Werte zur Bestimmung der hypoplastischen Parameter, die spaeter als Skalarwerte vorliegen muessen
    testwert = schuettkegel['Reibungswinkel-krit [Grad]']
    # testwert = oedo_locker['Spannung [kN/m^2]']
    # testwert = oedo_dicht['Spannung [kN/m^2]']
    testwert = triax['Reibungswinkel-Peak-locker [Grad]']
    testwert = triax['Reibungswinkel-Peak-dicht [Grad]']
    testwert = triax['Dilatanzwinkel [Grad]']
    testwert = triax['Spannung-Peak-eff [kN/m^2]']
    testwert = triax['Porenzahl-Peak [-]']

    tol = 1e-6
    # ---------------------- Oedo-locker ----------------------
    if (any([(abs(einzelvar - hoehe_oedo_l) < tol) for einzelvar in setzung_oedo_l])):
        print('# Warnung: Setzung des lockeren Oedometers annaehernd Probenhoehe')
        return False

    if (abs(masse_oedo_l) < tol):
        print('# Warnung: Masse des lockeren Oedometers annaehernd Null')
        return False

    if (abs(durchmesser_oedo_l) < tol):
        print('# Warnung: Durchmesser des lockeren Oedometers annaehernd Null')
        return False

    porenzahlen = [korndichte/(masse_oedo_l /((hoehe_oedo_l - aktuelle_setzung)/10.0 \
        *pi*(durchmesser_oedo_l/20.0)**2)) - 1.0 for aktuelle_setzung in setzung_oedo_l]
    oedo_locker.update([('Porenzahl [-]', porenzahlen)])

    # ---------------------- Oedo-dicht -----------------------
    if (any([(abs(einzelvar - hoehe_oedo_d) < tol) for einzelvar in setzung_oedo_d])):
        print('# Warnung: Setzung des dichten Oedometers annaehernd Probenhoehe')
        return False

    if (abs(masse_oedo_l) < tol):
        print('# Warnung: Masse des dichten Oedometers annaehernd Null')
        return False

    if (abs(durchmesser_oedo_d) < tol):
        print('# Warnung: Durchmesser des dichten Oedometers annaehernd Null')
        return False

    porenzahlen = [korndichte/(masse_oedo_d /((hoehe_oedo_d - aktuelle_setzung)/10.0 \
        *pi*(durchmesser_oedo_d/20.0)**2))-1.0 for aktuelle_setzung in setzung_oedo_d]
    oedo_dicht.update([('Porenzahl [-]', porenzahlen)])

    # ----------------------- Triax-D -------------------------
    if (abs(e_max - e_min) < tol):
        print('# Warnung: Differenz zwischen max. und min. Porenzahl annaehernd Null')
        return False

    bez_lagerungsdichte = (e_max - e_peak)/(e_max - e_min)
    triax.update([('Lagerungsdichte-bez [-]', bez_lagerungsdichte)])
    return True



# -------------------------------------------------------------------------------------------------
def KennwerteHypo(daten, refwerte=None):
    """Erwartet eine JSON-Struktur daten, in der die Daten zur Bestimmung der hypoplastischen
    Parameter gespeichert sind und aktualisiert/berechnet die entsprechenden Kennwerte.
    """
    from .konstanten import debugmodus
    from .datenstruktur import DatenstrukturExtrahieren
    from .verarbeitung_hilfen import ZusatzdatenKopieren

    erfolgreich = False

    if ('_Refwahl' not in daten):
        if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001')

        daten.update([('_Refwahl', '_Ref_001')])

    extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=HypoStruktur(), refwahl=daten['_Refwahl'])
    if (extrahierte_daten):
        daten.update(extrahierte_daten)
        ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten)
        erfolgreich = _KennwerteHypo(daten=daten)

    return erfolgreich



# -------------------------------------------------------------------------------------------------
def VorbereitungHypo(daten):
    """Erwarte eine eingelesene JSON-Struktur daten, in der die Daten zur Bestimmung der
    hypoplastischen Parameter gespeichert sind. Die uebergebene Struktur wird modifiziert,
    um eine einheitliche Struktur fuer eine spaetere Weiterverarbeitung zu haben.
    """
    import copy
    from .datenstruktur import Datenstruktur, DictStrukturPruefenUndAngleichen

    testdaten = copy.deepcopy(daten)
    if (DictStrukturPruefenUndAngleichen(ref_dict=HypoStruktur(), test_dict=testdaten, warnung=True)):
        # Referenz an daten zu den modifizierten Daten aendern
        daten.clear()
        daten.update(testdaten)
    else:
        print('# Warnung: Struktur der Auswertung-Hypoplastisch-Daten ist ungueltig')


