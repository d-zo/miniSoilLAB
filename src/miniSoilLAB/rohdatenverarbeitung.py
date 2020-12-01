# -*- coding: utf-8 -*-
"""
rohdatenverarbeitung.py   v0.1 (2020-09)
"""

# Copyright 2020 Dominik Zobel.
# All rights reserved.
#
# This file is part of the SimpleScriptGenerator package.
# SimpleScriptGenerator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SimpleScriptGenerator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SimpleScriptGenerator. If not, see <http://www.gnu.org/licenses/>.


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
         print('# Abbruch: Wert ' + bezeichnung+ ' aus Gruppe ' + position[-1] + ' nicht in gueltigen Grenzen');
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
            if (bezeichnung == '[Checks]'):
               continue;
            #
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
            print('# Abbruch: Wert ' + position[-1] + ' nicht in gueltigen Grenzen');
            return False;
         #
         if (idx_start > 0):  
            print('# Hinweis: Schneide ungueltige Werte fuer ' + position[-1] + ' bis nach Index ' \
               + str(idx_start) + ' ab');
            cur_daten = cur_list[idx_start:];
         #
         return True;
   else:
      print('Abbruch: Unbekannter Typ in Dict');
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
   from .dateneinlesen import _JSONDateiEinlesen
   from .rohdaten import LeseGDSDaten
   from .kennwerte import _KennwerteTriax
   from .konstanten import basispfad
   from .vorlagen import VorlagenstrukturZuDatenstruktur
   #
   if (not isinstance(dateiname, list)):
      dateiname = [dateiname];
   #
   vorlage = _JSONDateiEinlesen(dateiname=basispfad + 'Triax-D/Triax-D_01.json',
      bezeichnung='Vorlage Triax-D');
   if (vorlage is None):
      return None;
   #
   vorlage = vorlage['Triax-D_01'];
   triax = VorlagenstrukturZuDatenstruktur(vorlage=vorlage);
   #
   # Entferne Eintraege, die nicht in den gds-Daten zu finden sein werden
   del triax['Dichte-dichteste-Lagerung [g/cm^3]'];
   del triax['Dichte-lockerste-Lagerung [g/cm^3]'];
   del triax['Porenzahl-max [-]'];
   del triax['Porenzahl-min [-]'];
   del triax['2-Saettigung']['Drucksteigerung [kN/m^2/min]'];
   #
   for idx_datei, einzeldateiname in enumerate(dateiname):
      gds = LeseGDSDaten(dateiname=einzeldateiname);
      gds = gds['Triax'];
      #
      if (idx_datei == 0):
         triax.update([('Projektname', 'GDS-Rohdaten')]);
         triax.update([('Bodenname', gds['Description of Sample:'])]);
         triax.update([('Datum', gds['Date of Test'])]);
         #triax.update([('Dateiname', gds['Dateiname'])]);
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
         # FIXME: Immer am Institut eine gueltige Annahme?
         trockenmasse = gds['Initial mass (g):'];
      else:
         trockenmasse = float(trockenmasse);
      #
      _DatenErgaenzen(daten=triax['1-Probenherstellung'], schluessel='Trockenmasse [g]', zusatzwerte=trockenmasse);
      #
      stage_number = gds['Daten']['Stage Number'];
      #
      try:
         idx_phase2 = stage_number.index(2.0);
         idx_phase3 = stage_number.index(3.0);
         idx_phase4 = stage_number.index(4.0);
      except:
         print('# Abbruch: Stages in ' + einzeldateiname + ' sind nicht wie erwartet von 1 bis 4');
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
      print([stauchung[0], idx_phase4]);
   #
   if (len(dateiname) < 3):
      del triax['Versuch 3'];
      #
      if (len(dateiname) < 2):
         del triax['Versuch 2'];
   #
   # Pruefe zulaessige Werte, gueltigen Bereich und min_schnitt anhand der Triax-D-Vorlage
   if (_RohdatensatzPruefen(daten=triax, vorlage=vorlage, position=[])):
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
