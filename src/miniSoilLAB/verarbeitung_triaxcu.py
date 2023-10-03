# -*- coding: utf-8 -*-
"""
verarbeitung_triaxcu.py   v0.2 (2021-11)
"""

# Copyright 2020-2021 Dominik Zobel.
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
def TriaxCUStruktur():
   #
   import copy
   from .datenstruktur import Datenstruktur
   #
   struktur = Datenstruktur({
      '1-Probenherstellung': Datenstruktur({
         'Hoehe [mm]': [],
         'Durchmesser [mm]': [],
         'Feuchtmasse [g]': []
      }),
      '2-Saettigung': Datenstruktur({
         'Zelldruck [kN/m^2]': [],
         'Saettigungsdruck [kN/m^2]': []
      }),
      '3-Konsolidation': Datenstruktur({
         'Delta Hoehe [mm]': []
      }),
      '5-Abscheren': Datenstruktur({
         'Trockenmasse [g]': []
      }),
      'Versuch 1': Datenstruktur({
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': [],
         'Zeit [s]': []
      }),
      'Versuch 2': Datenstruktur({
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': [],
         'Zeit [s]': []
      }),
      'Versuch 3': Datenstruktur({
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': [],
         'Zeit [s]': []
      })
   });
   return copy.deepcopy(struktur);
#


# -------------------------------------------------------------------------------------------------
def KennwerteTriaxCU(daten, refwerte):
   """Erwartet eine JSON-Struktur daten, in der die Daten zu Triax-CU-Versuchen gespeichert sind
   und aktualisiert/berechnet die entsprechenden Kennwerte.
   """
   from .konstanten import debugmodus
   from .datenstruktur import DatenstrukturExtrahieren
   from .verarbeitung_hilfen import ZusatzdatenKopieren
   from .verarbeitung_triax import _KennwerteTriaxDundCU
   #
   erfolgreich = False;
   #
   if ('_Refwahl' not in daten):
      if (debugmodus):
         print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001');
      #
      daten.update([('_Refwahl', '_Ref_001')]);
   #
   extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=TriaxCUStruktur(), refwahl=daten['_Refwahl']);
   if (extrahierte_daten):
      daten.update(extrahierte_daten);
      ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten);
      erfolgreich = _KennwerteTriaxDundCU(daten=daten, refwerte=refwerte, typ='Triax-CU');
   #
   return erfolgreich;
#


# -------------------------------------------------------------------------------------------------
def VorbereitungTriaxCU(daten):
   """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Triax-CU-Versuchen
   gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
   eine spaetere Weiterverarbeitung zu haben.
   """
   import copy
   from math import pi
   from .datenstruktur import DictStrukturPruefenUndAngleichen, DictStrukturGleichOderTeilmenge
   from .datenstruktur import EintraegeAusUnterstrukturenInHauptstruktur, ZielgroesseFindenUndAktualisieren
   from .verarbeitung_hilfen import SekundenOhneOffsetBereitstellen
   #
   testdaten = copy.deepcopy(daten);
   if (not DictStrukturPruefenUndAngleichen(ref_dict=TriaxCUStruktur(), test_dict=testdaten, warnung=False)):
      # Zusammengesetzte Einzelversuche haben die Tabellendaten ggfs. an anderer Stelle. Extrahiere diese
      # Daten aus Substrukturen (falls sie nicht schon dort gespeichert sind)
      EintraegeAusUnterstrukturenInHauptstruktur(daten=testdaten,
         unterstrukturen=['Versuch 1', 'Versuch 2', 'Versuch 3'], eintraege=['1-Probenherstellung',
         '2-Saettigung', '3-Konsolidation', '4-Nach Konsolidation', '5-Abscheren']);
      # Zielgroessen aus Alternativgroessen berechnen (falls erforderlich)
      try:
         # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
         ZielgroesseFindenUndAktualisieren(daten=testdaten['5-Abscheren'], bezeichnung='Trockenmasse mit Behaelter', einheit='g');
         ZielgroesseFindenUndAktualisieren(daten=testdaten['5-Abscheren'], bezeichnung='Behaeltermasse', einheit='g');
         #
         gesamttrockenmasse = testdaten['5-Abscheren']['Trockenmasse mit Behaelter [g]'];
         behaeltermasse = testdaten['5-Abscheren']['Behaeltermasse [g]'];
         testdaten['5-Abscheren'].update([('Trockenmasse [g]', [gesamttrockenmasse[idx]-behaeltermasse[idx] for idx in range(len(gesamttrockenmasse))])]);
      except:
         pass;
      #
      try:
         hoehe_e = testdaten['1-Probenherstellung']['Hoehe [mm]'];
         hoehe_n = testdaten['3-Konsolidation']['Hoehe [mm]'];
         testdaten['3-Konsolidation'].update([('Delta Hoehe [mm]', [hoehe_e[idx]-hoehe_n[idx] for idx in range(len(hoehe_e))])]);
      except:
         pass;
      #
      for versuch in ['Versuch 1', 'Versuch 2', 'Versuch 3']:
         SekundenOhneOffsetBereitstellen(daten=testdaten[versuch]);
   #
   if (DictStrukturGleichOderTeilmenge(ref_dict=TriaxCUStruktur(), test_dict=testdaten, warnung=True)):
      # Referenz an daten zu den modifizierten Daten aendern
      daten.clear();
      daten.update(testdaten);
   else:
      print('# Warnung: Struktur der Triax-CU-Daten ist ungueltig');
#
