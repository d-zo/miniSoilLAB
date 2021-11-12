# -*- coding: utf-8 -*-
"""
rohdatenverarbeitung.py   v0.2 (2020-12)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with miniSoilLAB. If not, see <http://www.gnu.org/licenses/>.


# -------------------------------------------------------------------------------------------------
def _RohdatensatzGruppePruefen(daten, vorlage, position):
   """Die in position definierte Struktur in daten entspricht einer Gruppe, die gemeinsam bearbeitet
   werden soll. Pruefe fuer alle Eintraege in der Gruppe, ob sie innerhalb der Grenzen der
   dazugehoerigen vorlage sind (und schneide sie ggfs. einheitlich ab).
   """
   from .gleichungsloeser import WertInZulaessigemBereich, LetzterIndexMitWertKleinerAls
   #
   # Erwarte keine Unterstruktur, sondern nur normale Eintraege in der Gruppe
   cur_vorlage = vorlage;
   cur_daten = daten;
   if (position != []):
      for idx_schluessel, schluessel in enumerate(position):
         cur_vorlage = cur_vorlage[schluessel];
         # Erster Schluessel ist die Tabellenseite der Vorlage -> Fuer Daten ignorieren
         if (idx_schluessel == 0):
            continue;
         #
         if (not schluessel.startswith('[')):
            cur_daten = cur_daten[schluessel];
   #
   idx_start_gruppe = 0;
   for bezeichnung in cur_vorlage.keys():
      if (len(cur_vorlage[bezeichnung]) > 2):
         grenzen = cur_vorlage[bezeichnung][1];
         temp_daten = cur_daten[bezeichnung];
         #
         idx_start = 0;
         temp_idx = LetzterIndexMitWertKleinerAls(liste=temp_daten, grenzwert=grenzen[0]);
         if (temp_idx is not None):
            idx_start = temp_idx + 1;
            if (idx_start > idx_start_gruppe):
               idx_start_gruppe = idx_start;
   #
   for bezeichnung in cur_vorlage.keys():
      grenzen = cur_vorlage[bezeichnung][1];
      temp_daten = cur_daten[bezeichnung];
      #
      if (not WertInZulaessigemBereich(name=bezeichnung, liste=temp_daten[idx_start_gruppe:],
         minmax=grenzen)):
         print('# Fehler: Wert ' + bezeichnung+ ' aus Gruppe ' + position[-1] + ' nicht in gueltigen Grenzen');
         return False;
      #
      if (idx_start_gruppe > 0):
         cur_daten[bezeichnung] = cur_daten[bezeichnung][idx_start_gruppe:];
   #
   if (idx_start_gruppe > 0):  
      print('# Hinweis: Begrenze Werte in ' + position[-1] + ' auf das Intervall [' \
         + str(idx_start_gruppe) + ', :]');
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def _RohdatensatzPruefen(daten, vorlage, position):
   """Pruefe alle Eintraege in der Struktur daten, ob sie innerhalb der Grenzen der dazugehoerigen
   vorlage sind (und schneide sie ggfs. ab). Mithilfe von position wird das aktuelle Element der
   Struktur uebergeben, um nacheinander alle Eintraege abzuarbeiten.
   """
   from .datenstruktur import Datenstruktur
   from .gleichungsloeser import WertInZulaessigemBereich, LetzterIndexMitWertKleinerAls
   #
   status = True;
   cur_vorlage = vorlage;
   cur_daten = daten;
   if (position != []):
      for idx_schluessel, schluessel in enumerate(position):
         cur_vorlage = cur_vorlage[schluessel];
         # Erster Schluessel ist die Tabellenseite der Vorlage -> Fuer Daten ignorieren
         if (idx_schluessel == 0):
            continue;
         #
         # Nur die Schluessel beruecksichtigen, die in Vorlage und Daten vorhanden sind
         try:
            cur_daten = cur_daten[schluessel];
         except:
            return True;
   #
   if ((isinstance(cur_vorlage, Datenstruktur)) or (isinstance(cur_vorlage, dict))):
      for bezeichnung in cur_vorlage.keys():
         if (bezeichnung.startswith('[')):
            if (not _RohdatensatzGruppePruefen(daten=daten, vorlage=vorlage, position=position + [bezeichnung])):
               return False;
         else:
            if (not _RohdatensatzPruefen(daten=daten, vorlage=vorlage, position=position + [bezeichnung])):
               return False;
      #
      return True;
   #
   elif (isinstance(cur_vorlage, str)):
      return True;
   elif (isinstance(cur_vorlage, list)):
      if (len(cur_vorlage) < 2):
         return True;
      #
      if (isinstance(cur_daten, list)):
         cur_list = cur_daten;
      else:
         cur_list = [cur_daten];
      #
      if (len(cur_vorlage) == 2):
         return WertInZulaessigemBereich(name=position[-1], liste=cur_list, minmax=cur_vorlage[1]);
      else:
         idx_start = 0;
         temp_idx = LetzterIndexMitWertKleinerAls(liste=cur_list, grenzwert=cur_vorlage[1][0]);
         if (temp_idx is not None):
            idx_start = temp_idx + 1;
         #
         zulaessig = WertInZulaessigemBereich(name=position[-1], liste=cur_list[idx_start:],
            minmax=cur_vorlage[1]);
         if (not zulaessig):
            print('# Fehler: Wert ' + position[-1] + ' nicht in gueltigen Grenzen');
            return False;
         #
         if (idx_start > 0):  
            print('# Hinweis: Schneide ungueltige Werte fuer ' + position[-1] + ' bis nach Index ' \
               + str(idx_start) + ' ab');
            cur_daten = cur_list[idx_start:];
         #
         return True;
   else:
      print('Fehler: Unbekannter Typ in Dict');
      return False;
#


# -------------------------------------------------------------------------------------------------
def _DatenErgaenzen(daten, schluessel, zusatzwerte):
   """Fügt die uebergebenen zusatzwerte ans Ende der Liste in der Struktur daten unter dem
   angegebenen schluessel. Effektiv wird somit die Liste unter daten[schluessel] um [zusatzwerte]
   erweitert.
   """
   daten.update([(schluessel, daten[schluessel] + [zusatzwerte])]);
#


# -------------------------------------------------------------------------------------------------
def VerarbeitungRohdatenGDSTriax(dateiname, lagerungsdichte, korndichte):
   """Liest eine gds-Datei fuer einen drainierten Triaxialversuch (Triax-D) ein und erzeugt eine
   interne Struktur der Daten. Dazu wird der dateiname der Rohdaten sowie eine Bezeichnung der
   lagerungsdichte ("locker" oder "dicht") sowie die korndichte in [g/cm^3] erwartet.
   Es kann entweder ein dateiname oder eine Liste mit drei dateinamen uebergeben werden.
   Gibt eine Datenstruktur mit den Versuchsdaten zurueck.
   """
   from .datenstruktur import Datenstruktur
   from .rohdaten import LeseGDSDaten
   from .kennwerte import _KennwerteTriax
   from .vorlagen import VorlagenstrukturZuDatenstruktur
   #
   if (not isinstance(dateiname, list)):
      dateiname = [dateiname];
   #
   if (len(dateiname) > 3):
      print('# Warnung: Nur drei Dateien beim Einlesen der Rohdaten (Triax) erlaubt - ignoriere Rest');
      dateiname = dateiname[:3];
   #
   if ((lagerungsdichte != 'locker') and (lagerungsdichte != 'dicht')):
      print('# Fehler: Lagerungsdichte muss locker oder dicht sein.');
      return None;
   #
   triaxvorlage = {
      'Tabelle': {
         'Projektname': ['B4'],
         'Datum': ['B3'],
         'Bodenname': ['B6'],
         'Korndichte [g/cm^3]': ['B8', [0.2, 10.0]],
         '1-Probenherstellung': {
            'Hoehe [mm]': ['B16:D16', [5.0, 500.0]],
            'Durchmesser [mm]': ['B17:D17', [5.0, 500.0]],
            'Trockenmasse [g]': ['B18:D18', [10.0, 1000.0]]
         },
         '2-Saettigung': {
            'Zelldruck [kN/m^2]': ['B23:D23', [5.0, 5000.0]],
            'Saettigungsdruck [kN/m^2]': ['B24:D24', [5.0, 5000.0]],
            'Dauer [h]': ['B26:D26', [0.0, 340.0]],
            'Backvolume-Start [mm^3]': ['B27:D27', [-200000.0, 200000.0]],
            'Backvolume-Ende [mm^3]': ['B28:D28', [-200000.0, 200000.0]]
         },
         '3-Konsolidation': {
            'Backvolume-Ende [mm^3]': ['B33:D33', [-200000.0, 200000.0]]
         },
         '5-Abscheren': {
            'Backvolume-Ende [mm^3]': ['B38:D38', [-200000.0, 200000.0]]
         }
      },
      'Versuch01': {
         'Versuch 1': {
            '[Einzelversuch1]': {
               'Zeit [s]': ['A5:A-1', [0.0, 1.21e6]],
               'Radialdruck [kN/m^2]': ['B5:B-1', [5.0, 5000.0]],
               'Radialvolumen [mm^3]': ['C5:C-1', [-200000.0, 200000.0]],
               'Porenwasserdruck [kN/m^2]': ['D5:D-1', [5.0, 5000.0]],
               'Porenwasservolumen [mm^3]': ['E5:E-1', [-200000.0, 200000.0]],
               'Axialkraft [kN]': ['F5:F-1', [0.0, 100.0], 'min_schnitt'],
               'Porendruck [kN/m^2]': ['G5:G-1', [5.0, 5000.0]],
               'Stauchung [mm]': ['H5:H-1', [0.0, 500.0], 'min_schnitt']
            }
         }
      },
      'Versuch02': {
         'Versuch 2': {
            '[Einzelversuch2]': {
               'Zeit [s]': ['A5:A-1', [0.0, 1.21e6]],
               'Radialdruck [kN/m^2]': ['B5:B-1', [5.0, 5000.0]],
               'Radialvolumen [mm^3]': ['C5:C-1', [-200000.0, 200000.0]],
               'Porenwasserdruck [kN/m^2]': ['D5:D-1', [5.0, 5000.0]],
               'Porenwasservolumen [mm^3]': ['E5:E-1', [-200000.0, 200000.0]],
               'Axialkraft [kN]': ['F5:F-1', [0.0, 100.0], 'min_schnitt'],
               'Porendruck [kN/m^2]': ['G5:G-1', [5.0, 5000.0]],
               'Stauchung [mm]': ['H5:H-1', [0.0, 500.0], 'min_schnitt']
            }
         }
      },
      'Versuch03': {
         'Versuch 3': {
            '[Einzelversuch3]': {
               'Zeit [s]': ['A5:A-1', [0.0, 1.21e6]],
               'Radialdruck [kN/m^2]': ['B5:B-1', [5.0, 5000.0]],
               'Radialvolumen [mm^3]': ['C5:C-1', [-200000.0, 200000.0]],
               'Porenwasserdruck [kN/m^2]': ['D5:D-1', [5.0, 5000.0]],
               'Porenwasservolumen [mm^3]': ['E5:E-1', [-200000.0, 200000.0]],
               'Axialkraft [kN]': ['F5:F-1', [0.0, 100.0], 'min_schnitt'],
               'Porendruck [kN/m^2]': ['G5:G-1', [5.0, 5000.0]],
               'Stauchung [mm]': ['H5:H-1', [0.0, 500.0], 'min_schnitt']
            }
         }
      }
   };
   triax = VorlagenstrukturZuDatenstruktur(vorlage=triaxvorlage);
   #
   for idx_datei, einzeldateiname in enumerate(dateiname):
      tempgds = LeseGDSDaten(dateiname=einzeldateiname);
      gds = tempgds['Triax'];
      #
      if (idx_datei == 0):
         triax.update([('Projektname', 'GDS-Rohdaten')]);
         triax.update([('Bodenname', gds['Description of Sample:'])]);
         triax.update([('Datum', gds['Date of Test'])]);
         zusatz = '';
         if (len(dateiname) > 1):
            zusatz = ' (+' + str(len(dateiname)-1) + ')';
         triax.update([('Dateiname', einzeldateiname + zusatz)]);
         triax.update([('Korndichte [g/cm^3]', korndichte)]);
      #
      _DatenErgaenzen(daten=triax['1-Probenherstellung'], schluessel='Hoehe [mm]', zusatzwerte=gds['Initial Height (mm)']);
      _DatenErgaenzen(daten=triax['1-Probenherstellung'], schluessel='Durchmesser [mm]', zusatzwerte=gds['Initial Diameter (mm)']);
      #
      trockenmasse = gds['Initial dry mass (g):'];
      if (trockenmasse == ''):
         trockenmasse = gds['Initial mass (g):'];
         if (trockenmasse == ''):
            print('# Fehler: Keine Anfangs(trocken)masse angegeben');
            return None;
         #
         print('# Warnung: Keine Anfangstrockenmasse eingetragen, nehme Anfangsmasse');
      #
      trockenmasse = float(trockenmasse);
      _DatenErgaenzen(daten=triax['1-Probenherstellung'], schluessel='Trockenmasse [g]', zusatzwerte=trockenmasse);
      #
      stage_number = gds['Daten']['Stage Number'];
      #
      try:
         idx_phase2 = stage_number.index(2.0);
         idx_phase3 = stage_number.index(3.0);
         idx_phase4 = stage_number.index(4.0);
      except:
         print('# Fehler: Stages in ' + einzeldateiname + ' sind nicht wie erwartet von 1 bis 4');
         return None;
      #
      dauer = gds['Daten']['Time since start of stage (s)'];
      #
      _DatenErgaenzen(daten=triax['2-Saettigung'], schluessel='Zelldruck [kN/m^2]', zusatzwerte=gds['Daten']['Radial Pressure (kPa)'][idx_phase2]);
      _DatenErgaenzen(daten=triax['2-Saettigung'], schluessel='Saettigungsdruck [kN/m^2]', zusatzwerte=gds['Daten']['Back Pressure (kPa)'][idx_phase2]);
      _DatenErgaenzen(daten=triax['2-Saettigung'], schluessel='Dauer [h]', zusatzwerte=round(20.0*dauer[idx_phase3-1]/3600.0)/20.0);
      _DatenErgaenzen(daten=triax['2-Saettigung'], schluessel='Backvolume-Start [mm^3]', zusatzwerte=gds['Daten']['Back Volume (mm³)'][idx_phase2]);
      _DatenErgaenzen(daten=triax['2-Saettigung'], schluessel='Backvolume-Ende [mm^3]', zusatzwerte=gds['Daten']['Back Volume (mm³)'][idx_phase3-1]);
      #
      _DatenErgaenzen(daten=triax['3-Konsolidation'], schluessel='Backvolume-Ende [mm^3]', zusatzwerte=gds['Daten']['Back Volume (mm³)'][idx_phase4-1]);
      #
      _DatenErgaenzen(daten=triax['5-Abscheren'], schluessel='Backvolume-Ende [mm^3]', zusatzwerte=gds['Daten']['Back Volume (mm³)'][-1]);
      #
      versuch = 'Versuch ' + str(idx_datei+1);
      triax[versuch].update([('Zeit [s]', gds['Daten']['Time since start of stage (s)'][idx_phase4:])]);
      triax[versuch].update([('Radialdruck [kN/m^2]', gds['Daten']['Radial Pressure (kPa)'][idx_phase4:])]);
      triax[versuch].update([('Radialvolumen [mm^3]', gds['Daten']['Radial Volume (mm³)'][idx_phase4:])]);
      triax[versuch].update([('Porenwasserdruck [kN/m^2]', gds['Daten']['Back Pressure (kPa)'][idx_phase4:])]);
      triax[versuch].update([('Porenwasservolumen [mm^3]', gds['Daten']['Back Volume (mm³)'][idx_phase4:])]);
      triax[versuch].update([('Axialkraft [kN]', gds['Daten']['Load Cell (kN)'][idx_phase4:])]);
      triax[versuch].update([('Porendruck [kN/m^2]', gds['Daten']['Pore Pressure (kPa)'][idx_phase4:])]);
      #
      stauchung = gds['Daten']['Axial Displacement (mm)'][idx_phase4:];
      triax[versuch].update([('Stauchung [mm]', [x-stauchung[0] for x in stauchung])]);
   #
   if (len(dateiname) < 3):
      del triax['Versuch 3'];
      #
      if (len(dateiname) < 2):
         del triax['Versuch 2'];
   #
   # Pruefe zulaessige Werte, gueltigen Bereich und min_schnitt anhand der Triax-D-Vorlage
   if (_RohdatensatzPruefen(daten=triax, vorlage=triaxvorlage, position=[])):
      triax.update([('Status', 'Einlesen erfolgreich')]);
      #
      _KennwerteTriax(daten=triax);
      #
      daten = Datenstruktur();
      daten.update([('Triax-D-' + lagerungsdichte, triax)]);
      return daten;
   else:
      return None;
#
