# -*- coding: utf-8 -*-
"""
verarbeitung_lodi.py   v0.2 (2021-11)
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
def LoDiStruktur():
   #
   import copy
   from .datenstruktur import Datenstruktur
   #
   struktur = Datenstruktur({
      'Lockerste-Lagerung': Datenstruktur({
         'Zylindervolumen [cm^3]': [],
         'Probenmasse [g]': []
      }),
      'Dichteste-Lagerung': Datenstruktur({
         'Zylindergrundflaeche [cm^2]': [],
         'Zylinderhoehe [cm]': [],
         'Plattenhoehe [cm]': [],
         'Probenmasse [g]': [],
         'Setzung [mm]': []
      })
   });
   return copy.deepcopy(struktur);
#


# -------------------------------------------------------------------------------------------------
def _KennwerteLoDi(daten, refwerte):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage LoDi und speichere
   sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   lo_lagerung = daten['Lockerste-Lagerung'];
   di_lagerung = daten['Dichteste-Lagerung'];
   #
   liste_masse_lo = lo_lagerung['Probenmasse [g]'];
   liste_vol_lo = lo_lagerung['Zylindervolumen [cm^3]'];
   #
   liste_setzung = di_lagerung['Setzung [mm]'];
   liste_masse_di = di_lagerung['Probenmasse [g]'];
   liste_zylinderflaeche_di = di_lagerung['Zylindergrundflaeche [cm^2]'];
   liste_zylinderhoehe_di = di_lagerung['Zylinderhoehe [cm]'];
   liste_plattenhoehe = di_lagerung['Plattenhoehe [cm]'];
   #
   # Extrahiere Uebergabewerte
   korndichte = refwerte['Korndichte [g/cm^3]'];
   #
   tol = 1e-6;
   #
   if (korndichte < tol):
      print('# Warnung: Korndichte kleiner als ' + str(tol));
      return False;
   #
   # -------------------- Lockerste Lagerung --------------------
   # Falls ein skalares Zylindervolumen existiert, verwende es fuer alle Massen
   if (not isinstance(liste_vol_lo, list)):
      liste_vol_lo = [liste_vol_lo for x in liste_masse_lo];
   #
   num_lo = len(liste_masse_lo);
   liste_trockendichte_min = [0 for x in range(num_lo)];
   liste_porenanteil_max = [0 for x in range(num_lo)];
   liste_porenzahl_max = [0 for x in range(num_lo)];
   #
   for idx in range(num_lo):
      masse_lo = liste_masse_lo[idx];
      if (masse_lo < tol):
         print('# Warnung: Masse (lo) kleiner als ' + str(tol));
         return False;
      #
      zylindervolumen_lo = liste_vol_lo[idx];
      if (zylindervolumen_lo < tol):
         print('# Warnung: Zylindervolumen kleiner als ' + str(tol));
         return False;
      #
      liste_trockendichte_min[idx] = masse_lo/zylindervolumen_lo;
      liste_porenanteil_max[idx] = 1.0 - liste_trockendichte_min[idx]/korndichte;
      liste_porenzahl_max[idx] = korndichte/liste_trockendichte_min[idx] - 1.0;
   #
   lo_lagerung.update([('Trockendichte-min [g/cm^3]', liste_trockendichte_min)]);
   lo_lagerung.update([('Porenanteil-max [-]', liste_porenanteil_max)]);
   lo_lagerung.update([('Porenzahl-max [-]', liste_porenzahl_max)]);
   #
   # -------------------- Dichteste Lagerung --------------------
   # Die Eintraege von Setzung und Probemasse muessen aufeinander abgestimmt sein (u.a. gleiche Laenge)
   num_di = len(liste_masse_di);
   liste_trockendichte_max = [0 for x in range(num_di)];
   liste_porenanteil_min = [0 for x in range(num_di)];
   liste_porenzahl_min = [0 for x in range(num_di)];
   #
   if (num_di != len(liste_setzung)):
      print('# Warnung: Eintraege fuer Setzung und Probemasse (dichte Lagerung) muessen zueinander passen (u.a. gleiche Laenge)');
      return False;
   # Skalare Groessen in Listen umwandeln
   if (not isinstance(liste_zylinderflaeche_di, list)):
      liste_zylinderflaeche_di = [liste_zylinderflaeche_di for x in num_di];
   #
   if (not isinstance(liste_zylinderhoehe_di, list)):
      liste_zylinderhoehe_di = [liste_zylinderhoehe_di for x in num_di];
   #
   if (not isinstance(liste_plattenhoehe, list)):
      liste_plattenhoehe = [liste_plattenhoehe for x in num_di];
   #
   for idx in range(num_di):
      masse_di = liste_masse_di[idx];
      if (masse_di < tol):
         print('# Warnung: Masse (di) kleiner als ' + str(tol));
         return False;
      #
      zylinderflaeche_di = liste_zylinderflaeche_di[idx];
      zylinderhoehe_di = liste_zylinderhoehe_di[idx];
      plattenhoehe = liste_plattenhoehe[idx];
      setzung = liste_setzung[idx];
      #
      min_vol = zylinderflaeche_di*(zylinderhoehe_di - plattenhoehe - setzung/10.0);
      if (min_vol < tol):
         print('# Warnung: Volumen (di) kleiner als ' + str(tol));
         return False;
      #
      liste_trockendichte_max[idx] = masse_di/min_vol;
      # FIXME: In Vorverarbeitung beheben:
      # In manchen Vorlagen werden die Setzungen nicht mit dem richtigen Vorzeichen angegeben,
      # so dass geprueft werden muss, ob die Werte in einem sinnvollen Bereich liegen
      if (liste_trockendichte_max[idx] > korndichte):
         print('# Hinweis: Vorzeichen fuer Setzung der dichten Lagerung werden invertiert');
         liste_setzung[idx] = -setzung;
         di_lagerung.update([('Setzung [mm]', liste_setzung)]);
         min_vol = zylinderflaeche_di*(zylinderhoehe_di - plattenhoehe + setzung/10.0);
         if (min_vol < tol):
            print('# Warnung: Volumen (di) kleiner als ' + str(tol));
            return False;
         #
         liste_trockendichte_max[idx] = masse_di/min_vol;
      #
      liste_porenanteil_min[idx] = 1.0 - liste_trockendichte_max[idx]/korndichte;
      liste_porenzahl_min[idx] = korndichte/liste_trockendichte_max[idx] - 1.0;
   #
   di_lagerung.update([('Trockendichte-max [g/cm^3]', liste_trockendichte_max)]);
   di_lagerung.update([('Porenanteil-min [-]', liste_porenanteil_min)]);
   di_lagerung.update([('Porenzahl-min [-]', liste_porenzahl_min)]);
   #
   trockendichte_min = sum(liste_trockendichte_min)/len(liste_trockendichte_min);
   trockendichte_max = sum(liste_trockendichte_max)/len(liste_trockendichte_max);
   daten.update([('Trockendichte-min [g/cm^3]', trockendichte_min)]);
   daten.update([('Trockendichte-max [g/cm^3]', trockendichte_max)]);
   daten.update([('Porenzahl-min [-]', korndichte/trockendichte_max - 1.0)]);
   daten.update([('Porenzahl-max [-]', korndichte/trockendichte_min - 1.0)]);
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def KennwerteLoDi(daten, refwerte):
   """Erwartet eine JSON-Struktur daten, in der die Daten zur Bestimmung der lockersten und
   dichtesten Lagerung gespeichert sind und aktualisiert/berechnet die entsprechenden Kennwerte.
   """
   from .datenstruktur import DatenstrukturExtrahieren
   from .verarbeitung_hilfen import ZusatzdatenKopieren
   #
   erfolgreich = False;
   extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=LoDiStruktur(),
      listenlaenge=['Probenmasse [g]', 'Setzung [mm]']);
   if (extrahierte_daten):
      daten.update(extrahierte_daten);
      ZusatzdatenKopieren(quelle=daten['_Ref_001'], ziel=daten);
      if (_KennwerteLoDi(daten=daten, refwerte=refwerte)):
         erfolgreich = True;
      else:
         print('# Warnung: Berechnete LoDi-Daten unvollstaendig');
   #
   return erfolgreich;
#


# -------------------------------------------------------------------------------------------------
def VorbereitungLoDi(daten):
   """Erwarte eine eingelesene JSON-Struktur daten, in der die Daten zur Bestimmung der
   lockersten und dichtesten Lagerung gespeichert sind. Die uebergebene Struktur wird modifiziert,
   um eine einheitliche Struktur fuer eine spaetere Weiterverarbeitung zu haben.
   """
   import copy
   from .datenstruktur import Datenstruktur, DictStrukturPruefenUndAngleichen
   from .datenstruktur import DictStrukturGleichOderTeilmenge, ZielgroesseFindenUndAktualisieren
   #
   testdaten = copy.deepcopy(daten);
   if (not DictStrukturPruefenUndAngleichen(ref_dict=LoDiStruktur(), test_dict=testdaten, warnung=False)):
      try:
         lo_lagerung = testdaten['Lockerste-Lagerung'];
         di_lagerung = testdaten['Dichteste-Lagerung'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens eine erforderliche Struktur in LoDi nicht vorhanden - ' + str(errormessage));
         return;
      #
      # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
      ZielgroesseFindenUndAktualisieren(daten=lo_lagerung, bezeichnung='Probenmasse-1', einheit='g');
      ZielgroesseFindenUndAktualisieren(daten=lo_lagerung, bezeichnung='Probenmasse-2', einheit='g');
      ZielgroesseFindenUndAktualisieren(daten=di_lagerung, bezeichnung='Probenmasse-1', einheit='g');
      ZielgroesseFindenUndAktualisieren(daten=di_lagerung, bezeichnung='Probenmasse-2', einheit='g');
      ZielgroesseFindenUndAktualisieren(daten=di_lagerung, bezeichnung='Setzung-1', einheit='mm');
      ZielgroesseFindenUndAktualisieren(daten=di_lagerung, bezeichnung='Setzung-2', einheit='mm');
      # Zielgroessen aus Alternativgroessen berechnen (falls erforderlich)
      hat_lo_masse = False;
      try:
         masse_lo = lo_lagerung['Probenmasse [g]'];
         hat_lo_masse = True;
      except:
         pass;
      #
      if (not hat_lo_masse):
         try:
            temp_masse1 = lo_lagerung['Probenmasse-1 [g]'];
            temp_masse2 = lo_lagerung['Probenmasse-2 [g]'];
            masse_lo = [temp_masse1, temp_masse2];
            lo_lagerung.update([('Probenmasse [g]', masse_lo)]);
            del lo_lagerung['Probenmasse-1 [g]'];
            del lo_lagerung['Probenmasse-2 [g]'];
         except:
            print('# Warnung: Mindestens eine erforderliche Struktur in LoDi nicht vorhanden ' \
               '- Probenmasse [g] bzw. Probenmasse-1 [g] und Probenmasse-2 [g]');
            return;
      #
      if ('Probenmasse [g]' in di_lagerung):
         masse_di = di_lagerung['Probenmasse [g]'];
      else:
         if (('Probenmasse-1 [g]' in di_lagerung) and ('Probenmasse-2 [g]' in di_lagerung)):
            masse_di = [di_lagerung['Probenmasse-1 [g]'], di_lagerung['Probenmasse-2 [g]']];
         else:
            masse_di = masse_lo;
      #
      if ('Setzung [mm]' in di_lagerung):
         di_setzung = di_lagerung['Setzung [mm]'];
         if (isinstance(masse_di, list)):
            print('# Warnung: Erwarte Skalarwert fuer dichte Probenmasse bei einer Setzungsliste in LoDi');
            return;
         #
         else:
            masse_di = [masse_di for x in di_setzung];
      #
      else:
         if (('Setzung-1 [mm]' in di_lagerung) and ('Setzung-2 [mm]' in di_lagerung)):
            temp_setzung1 = di_lagerung['Setzung-1 [mm]'];
            temp_setzung2 = di_lagerung['Setzung-2 [mm]'];
            #
            if (isinstance(masse_di, list)):
               if (len(masse_di) == 2):
                  masse_di = [masse_di[0] for x in temp_setzung1] + [masse_di[1] for x in temp_setzung2];
               elif (len(masse_di) == 1):
                  masse_di = [masse_di[0] for x in temp_setzung1+temp_setzung2];
               else:
                  print('# Warnung: Listen mit Laenge 1 oder 2 fuer dichte Probenmasse in LoDi erwartet');
                  return;
            else:
               masse_di = [masse_di for x in temp_setzung1+temp_setzung2];
            #
            di_lagerung.update([('Setzung [mm]', temp_setzung1+temp_setzung2)]);
            del di_lagerung['Setzung-1 [mm]'];
            del di_lagerung['Setzung-2 [mm]'];
      #
      di_lagerung.update([('Probenmasse [g]', masse_di)]);
   # Nach Ueberarbeitung erneut ueberpruefen
   if (DictStrukturGleichOderTeilmenge(ref_dict=LoDiStruktur(), test_dict=testdaten, warnung=True)):
      # Referenz an daten zu den modifizierten Daten aendern
      daten.clear();
      daten.update(testdaten);
   else:
      print('# Warnung: Struktur der LoDi-Daten ist ungueltig');
#
