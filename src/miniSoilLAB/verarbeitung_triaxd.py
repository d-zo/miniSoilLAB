# -*- coding: utf-8 -*-
"""
verarbeitung_triaxd.py   v0.2 (2021-11)
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
def TriaxDStruktur():
   #
   import copy
   from .datenstruktur import Datenstruktur
   #
   struktur = Datenstruktur({
      '1-Probenherstellung': Datenstruktur({
         'Hoehe [mm]': [],
         'Durchmesser [mm]': [],
         'Trockenmasse [g]': []
      }),
      '2-Saettigung': Datenstruktur({
         'Zelldruck [kN/m^2]': [],
         'Saettigungsdruck [kN/m^2]': [],
         'Backvolume-Start [mm^3]': [],
         'Backvolume-Ende [mm^3]': []
      }),
      '3-Konsolidation': Datenstruktur({
         'Backvolume-Ende [mm^3]': []
      }),
      '5-Abscheren': Datenstruktur({
         'Backvolume-Ende [mm^3]': []
      }),
      'Versuch 1': Datenstruktur({
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Porenwasservolumen [mm^3]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': [],
         'Zeit [s]': []
      }),
      'Versuch 2': Datenstruktur({
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Porenwasservolumen [mm^3]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': [],
         'Zeit [s]': []
      }),
      'Versuch 3': Datenstruktur({
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Porenwasservolumen [mm^3]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': [],
         'Zeit [s]': []
      })
   });
   return copy.deepcopy(struktur);
#


# -------------------------------------------------------------------------------------------------
def LagerungsdichtenTriaxDBestimmen(daten, refwerte, grenzen_min=[-0.1, 0.6], grenzen_max=[0.6, 1.2]):
   """Anhand der uebergebenen Trockendichten in refwerte und der berechneten Trockendichte der
   Daten in "_Ref_*" wird bestimmt, welche Versuche als locker bzw. dicht eingestuft werden.
   Als Toleranz werden grenzen_min/grenzen_max verwendet, wobei sich die beiden Werte auf das
   Intervall [Trockendichte-min, Trockendichte-max] beziehen mit 0 = Trockendichte-min und
   1 = Trockendichte-max. Gibt zwei (ggfs. leere) Listen mit den Namen der "_Ref_*"-Strukturen
   zurueck, die als locker bzw. dicht eingestuft worden sind.
   """
   from math import pi
   from .konstanten import debugmodus
   #
   triax_locker = [];
   triax_dicht = [];
   #
   refdichten = [refwerte[x] for x in ['Trockendichte-min [g/cm^3]', 'Trockendichte-max [g/cm^3]']];
   dichte_bereich = refdichten[1]-refdichten[0];
   bereich_locker = [refdichten[0] + grenzen_min[0]*dichte_bereich, refdichten[0] + grenzen_min[1]*dichte_bereich];
   bereich_dicht = [refdichten[0] + grenzen_max[0]*dichte_bereich, refdichten[0] + grenzen_max[1]*dichte_bereich];
   if (debugmodus):
      print('# Debug: Bereiche zur Bestimmung der Lagerungsdichte');
      print('         Locker: ' + str(round(1000*bereich_locker[0])/1000) + ' bis ' + str(round(1000*bereich_locker[1])/1000) + ' g/cm^3');
      print('         Dicht:  ' + str(round(1000*bereich_dicht[0])/1000) + ' bis ' + str(round(1000*bereich_dicht[1])/1000) + ' g/cm^3');
   #
   schluesselliste = sorted(list(daten.keys()));
   for schluessel in schluesselliste:
      if (not schluessel.startswith('_Ref_')):
         continue;
      #
      try:
         herstellung = daten[schluessel]['1-Probenherstellung'];
         hoehe_e = herstellung['Hoehe [mm]'];
         durchmesser_e = herstellung['Durchmesser [mm]'];
         trockenmasse_e = herstellung['Trockenmasse [g]'];
         #
         anzahl_versuche = len(hoehe_e);
         volumen_e = [pi*(durchmesser_e[idx]/10.0/2.0)**2 * hoehe_e[idx]/10.0 for idx in range(anzahl_versuche)];
         trockendichte_e = [trockenmasse_e[idx]/volumen_e[idx] for idx in range(anzahl_versuche)];
      except:
         print('# Debug: Abbruch wegen fehlender Werte');
         continue;
      #
      if (all([(trockendichte_e[idx] > bereich_locker[0]) and \
         (trockendichte_e[idx] < bereich_locker[1]) for idx in range(anzahl_versuche)])):
         triax_locker += [schluessel];
      elif (all([(trockendichte_e[idx] > bereich_dicht[0]) and \
         (trockendichte_e[idx] < bereich_dicht[1]) for idx in range(anzahl_versuche)])):
         triax_dicht += [schluessel];
      elif (debugmodus):
         print('# Debug: Triaxialversuch ' + schluessel + ' nicht erfolgreich als locker/dicht eingestuft');
         print(', '.join([str((trockendichte_e[idx]-refdichten[0])/dichte_bereich) for idx in range(anzahl_versuche)]));
   #
   return [triax_locker, triax_dicht];
#


# -------------------------------------------------------------------------------------------------
def KennwerteTriaxD(daten, refwerte):
   """Erwartet eine JSON-Struktur daten, in der die Daten zu Triax-D-Versuchen gespeichert sind
   und aktualisiert/berechnet die entsprechenden Kennwerte.
   """
   from .konstanten import debugmodus
   from .datenstruktur import Datenstruktur, DatenstrukturExtrahieren
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe, ZusatzdatenKopieren
   from .verarbeitung_triax import _KennwerteTriaxDundCU
   #
   triax_locker, triax_dicht = LagerungsdichtenTriaxDBestimmen(daten=daten, refwerte=refwerte);
   for variante, kandidaten in [('locker', triax_locker), ('dicht', triax_dicht)]:
      erfolgreich = False;
      if (kandidaten == []):
         if (debugmodus):
            print('# Hinweis: Keine kandidaten fuer Triax-D-' + variante);
         #
         continue;
      #
      triax_variante = GespeicherterWertOderUebergabe(daten=daten,
         bezeichnung='Triax-D-' + variante, uebergabe=Datenstruktur());
      #
      auswahl = kandidaten[0];
      if ('_Refwahl' not in triax_variante):
         if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme ' + kandidaten[0]);
         #
      else:
         if (triax_variante['_Refwahl'] not in kandidaten):
            print('# Warnung: Angegebene Referenzdaten ' + auswahl + ' ungueltig, nehme ' + kandidaten[0]);
         else:
            auswahl = triax_variante['_Refwahl'];
      #
      triax_variante.update([('_Refwahl', auswahl)]);
      #
      extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=TriaxDStruktur(),
         refwahl=triax_variante['_Refwahl']);
      if (extrahierte_daten):
         triax_variante.update(extrahierte_daten);
         ZusatzdatenKopieren(quelle=daten[triax_variante['_Refwahl']], ziel=triax_variante);
         erfolgreich = _KennwerteTriaxDundCU(daten=triax_variante, refwerte=refwerte, typ='Triax-D');
      #
      if (not erfolgreich):
         return False;
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def VorbereitungTriaxD(daten):
   """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Triax-D-Versuchen
   gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
   eine spaetere Weiterverarbeitung zu haben.
   """
   import copy
   from math import pi
   from .datenstruktur import DictStrukturPruefenUndAngleichen, DictStrukturGleichOderTeilmenge
   from .datenstruktur import EintraegeAusUnterstrukturenInHauptstruktur, ZielgroesseFindenUndAktualisieren
   #
   testdaten = copy.deepcopy(daten);
   if (not DictStrukturPruefenUndAngleichen(ref_dict=TriaxDStruktur(), test_dict=testdaten, warnung=False)):
      # Zusammengesetzte Einzelversuche haben die Tabellendaten ggfs. an anderer Stelle. Extrahiere diese
      # Daten aus Substrukturen (falls sie nicht schon dort gespeichert sind)
      EintraegeAusUnterstrukturenInHauptstruktur(daten=testdaten,
         unterstrukturen=['Versuch 1', 'Versuch 2', 'Versuch 3'], eintraege=['1-Probenherstellung',
         '2-Saettigung', '3-Konsolidation', '4-Nach Konsolidation', '5-Abscheren']);
      #
      # Zielgroessen aus Alternativgroessen berechnen (falls erforderlich)
      try:
         # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
         ZielgroesseFindenUndAktualisieren(daten=testdaten['1-Probenherstellung'], bezeichnung='Trockenmasse mit Behaelter', einheit='g');
         ZielgroesseFindenUndAktualisieren(daten=testdaten['1-Probenherstellung'], bezeichnung='Behaeltermasse', einheit='g');
         #
         gesamttrockenmasse = testdaten['1-Probenherstellung']['Trockenmasse mit Behaelter [g]'];
         behaeltermasse = testdaten['1-Probenherstellung']['Behaeltermasse [g]'];
         testdaten['1-Probenherstellung'].update([('Trockenmasse [g]', gesamttrockenmasse - behaeltermasse)]);
      except:
         pass;
      #
      try:
         hoehe_e = testdaten['1-Probenherstellung']['Hoehe [mm]'];
         hoehe_n = testdaten['3-Konsolidation']['Hoehe [mm]'];
         testdaten['3-Konsolidation'].update([('Delta Hoehe [mm]', hoehe_e-hoehe_n)]);
      except:
         pass;
      #
      if ('Backvolume-Start [mm^3]' not in testdaten['2-Saettigung']):
         try:
            numdaten = len(testdaten['1-Probenherstellung']['Trockenmasse [g]']);
            testdaten['2-Saettigung'].update([('Backvolume-Start [mm^3]', [0 for x in range(numdaten)])]);
         except:
            pass;
   #
   if (DictStrukturGleichOderTeilmenge(ref_dict=TriaxDStruktur(), test_dict=testdaten, warnung=True)):
      # Referenz an daten zu den modifizierten Daten aendern
      daten.clear();
      daten.update(testdaten);
   else:
      print('# Warnung: Struktur der Triax-D-Daten ist ungueltig');
#
