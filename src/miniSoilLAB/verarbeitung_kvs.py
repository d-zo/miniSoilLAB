# -*- coding: utf-8 -*-
"""
verarbeitung_kvs.py   v0.3 (2023-09)
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
def KVSStruktur():

    import copy
    from .datenstruktur import Datenstruktur

    struktur = Datenstruktur({
        'Sieblinie 1': Datenstruktur({
            'Entnahmestelle': [],
            'Korndurchmesser [mm]': [],
            'Summierte Masseanteile Gesamtmenge [%]': []
        })
    })
    return copy.deepcopy(struktur)



# -------------------------------------------------------------------------------------------------
def _KennwerteKVS(daten):
    from .rohdaten import Interpolationsblock_Aus_KVSdaten
    from .verarbeitung_hilfen import GespeicherterWertOderUebergabe

    param_interpolationspunkte = 24

    rueckgabe = False
    for sieblinie in daten:
        if (not sieblinie.startswith('Sieblinie')):
            continue

        korndurchmesser = daten[sieblinie]['Korndurchmesser [mm]']
        sum_masseprozent = daten[sieblinie]['Summierte Masseanteile Gesamtmenge [%]']

        interpolationspunkte = GespeicherterWertOderUebergabe(daten=daten[sieblinie],
            bezeichnung='Interpolationspunkte [-]', uebergabe=param_interpolationspunkte)

        nursiebung = False
        if (min(korndurchmesser) >= 0.06):
            nursiebung = True

        interpolation = Interpolationsblock_Aus_KVSdaten(korndurchmesser=korndurchmesser,
            sum_masseprozent=sum_masseprozent, interpolationspunkte=interpolationspunkte,
            nursiebung=nursiebung)
        daten[sieblinie].update([('Interpolation', interpolation)])
        rueckgabe = True

    return rueckgabe



# -------------------------------------------------------------------------------------------------
def AlleKVSKurven(daten):
    """Fuege alle vorhandenen Sieblinien der ausgewaehlten Referenzdaten zum tatsaechlichen
    Datensatz hinzu.
    """
    from .datenstruktur import Datenstruktur, DatenstrukturExtrahieren

    for sieblinie in daten[daten['_Refwahl']]:
        if ((sieblinie.startswith('Sieblinie')) and (sieblinie != 'Sieblinie 1')):
            KVSStruktur_mod = Datenstruktur({sieblinie: KVSStruktur()['Sieblinie 1']})
            extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=KVSStruktur_mod, refwahl=daten['_Refwahl'])
            if (extrahierte_daten):
                daten.update(extrahierte_daten)
        else:
            continue



# -------------------------------------------------------------------------------------------------
def KennwerteKVS(daten, refwerte=None):
    """Erwartet eine JSON-Struktur daten, in der die Kornverteilungsdaten gespeichert sind und
    aktualisiert/berechnet die entsprechenden Kennwerte.
    """
    from .konstanten import debugmodus
    from .datenstruktur import DatenstrukturExtrahieren
    from .verarbeitung_hilfen import ZusatzdatenKopieren

    erfolgreich = False

    if ('_Refwahl' not in daten):
        if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001')

        daten.update([('_Refwahl', '_Ref_001')])

    extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=KVSStruktur(), refwahl=daten['_Refwahl'])
    if (extrahierte_daten):
        daten.update(extrahierte_daten)
        ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten)
        AlleKVSKurven(daten=daten)
        erfolgreich = _KennwerteKVS(daten=daten)

    return erfolgreich


