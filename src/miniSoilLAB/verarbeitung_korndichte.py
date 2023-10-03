# -*- coding: utf-8 -*-
"""
verarbeitung_korndichte.py   v0.2 (2023-09)
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
def KorndichteStruktur():

    import copy
    from .datenstruktur import Datenstruktur

    struktur = Datenstruktur({
        'Trockenmasse mit Behaelter [g]': [],
        'Feuchtmasse mit Behaelter [g]': [],
        'Wassertemperatur [C]': [],
        'Pyknometer': Datenstruktur({
            'Feuchtmasse [g]': [],
            'Trockenmasse [g]': [],
            'Wassertemperatur [C]': []
        })
    })
    return copy.deepcopy(struktur)



# -------------------------------------------------------------------------------------------------
def _KennwerteKorndichte(daten):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage KKorndichte und
    speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
    """
    pyknometer = daten['Pyknometer']

    liste_massetrocken_gesamt = daten['Trockenmasse mit Behaelter [g]']
    liste_massefeucht_gesamt = daten['Feuchtmasse mit Behaelter [g]']
    liste_temp_probewasser = daten['Wassertemperatur [C]']
    liste_massetrocken_pyknometer = pyknometer['Trockenmasse [g]']
    liste_massefeucht_pyknometer = pyknometer['Feuchtmasse [g]']
    liste_temp_pyknowasser = pyknometer['Wassertemperatur [C]']

    # ------------------ Korndichte Berechnung -------------------
    num_versuche = len(liste_massetrocken_gesamt)
    liste_wassermasse_probe = [0 for x in range(num_versuche)]
    liste_wassermasse_pykno = [0 for x in range(num_versuche)]
    liste_wasserdichte_probe = [0 for x in range(num_versuche)]
    liste_wasserdichte_pykno = [0 for x in range(num_versuche)]
    liste_trockenmasse_probe = [0 for x in range(num_versuche)]
    liste_volumen_pykno = [0 for x in range(num_versuche)]
    liste_wasservolumen_probe = [0 for x in range(num_versuche)]
    liste_kornvolumen_probe = [0 for x in range(num_versuche)]
    liste_korndichte_probe = [0 for x in range(num_versuche)]

    for idx in range(num_versuche):
        massetrocken_gesamt = liste_massetrocken_gesamt[idx]
        massefeucht_gesamt = liste_massefeucht_gesamt[idx]
        temp_probewasser = liste_temp_probewasser[idx]
        massetrocken_pyknometer = liste_massetrocken_pyknometer[idx]
        massefeucht_pyknometer = liste_massefeucht_pyknometer[idx]
        temp_pyknowasser = liste_temp_pyknowasser[idx]

        # Abschaetzung der Wasserdichte anhand der Temperatur (fur Normaldruck) nach DIN EN ISO 17892-3
        liste_wasserdichte_probe[idx] = 1.0/(1.0 + ((2.31*temp_probewasser - 2.0)**2 - 182.0)*1e-6)
        liste_wasserdichte_pykno[idx] = 1.0/(1.0 + ((2.31*temp_pyknowasser - 2.0)**2 - 182.0)*1e-6)

        liste_wassermasse_probe[idx] = massefeucht_gesamt - massetrocken_gesamt
        liste_wassermasse_pykno[idx] = massefeucht_pyknometer - massetrocken_pyknometer
        liste_trockenmasse_probe[idx] = massetrocken_gesamt - massetrocken_pyknometer
        liste_wasservolumen_probe[idx] = (massefeucht_gesamt-massetrocken_gesamt)/liste_wasserdichte_probe[idx]
        liste_volumen_pykno[idx] = (massefeucht_pyknometer-massetrocken_pyknometer)/liste_wasserdichte_pykno[idx]

        liste_kornvolumen_probe[idx] = liste_volumen_pykno[idx]-liste_wasservolumen_probe[idx]
        liste_korndichte_probe[idx] = liste_trockenmasse_probe[idx]/liste_kornvolumen_probe[idx]

    pyknometer.update([('Wassermasse [g]', liste_wassermasse_pykno)])
    pyknometer.update([('Wasserdichte [g]', liste_wasserdichte_pykno)])
    pyknometer.update([('Volumen [cm^3]', liste_volumen_pykno)])

    daten.update([('Wassermasse [g]', liste_wassermasse_probe)])
    daten.update([('Wasserdichte [g]', liste_wasserdichte_probe)])
    daten.update([('Trockenmasse [g]', liste_trockenmasse_probe)])
    daten.update([('Wasservolumen [cm^3]', liste_wasservolumen_probe)])
    daten.update([('Kornvolumen [cm^3]', liste_kornvolumen_probe)])
    daten.update([('Korndichte [g/cm^3]', sum(liste_korndichte_probe)/len(liste_korndichte_probe))])



# -------------------------------------------------------------------------------------------------
def KennwerteKorndichte(daten, refwerte=None):
    """Erwartet eine JSON-Struktur daten, in der die Daten zur Bestimmung der Korndichte
    gespeichert sind und aktualisiert/berechnet die entsprechenden Kennwerte.
    """
    from .datenstruktur import DatenstrukturExtrahieren
    from .verarbeitung_hilfen import ZusatzdatenKopieren

    erfolgreich = False
    extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=KorndichteStruktur())
    if (extrahierte_daten):
        daten.update(extrahierte_daten)
        ZusatzdatenKopieren(quelle=daten['_Ref_001'], ziel=daten)
        _KennwerteKorndichte(daten=daten)
        erfolgreich = True

    return erfolgreich



# -------------------------------------------------------------------------------------------------
def VorbereitungKorndichte(daten):
    """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zur Bestimmung der
    Korndichte gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche
    Struktur fuer eine spaetere Weiterverarbeitung zu haben.
    """
    import copy
    from .datenstruktur import DictStrukturPruefenUndAngleichen
    from .verarbeitung_hilfen import ImportiertesDatumFormatieren

    testdaten = copy.deepcopy(daten)
    if (DictStrukturPruefenUndAngleichen(ref_dict=KorndichteStruktur(), test_dict=testdaten, warnung=True)):
        # FIXME: Erforderlich?
        if ('Datum' in testdaten):
            testdaten.update([('Datum', ImportiertesDatumFormatieren(datum=testdaten['Datum'],
                ausgabeformat='%B %Y'))])

        # Referenz an daten zu den modifizierten Daten aendern
        daten.clear()
        daten.update(testdaten)
    else:
        print('# Warnung: Struktur der Korndichte-Daten ist ungueltig')


