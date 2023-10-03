# -*- coding: utf-8 -*-
"""
rohdaten.py   v0.3 (2019-09)
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
def LeseEAXDaten(dateiname):
   """Lese und interpretiere eax-Dateien, die nach folgendem Schema aufgebaut sind:
   Die Datei ist in die beiden Abschnitte [Eingaben] und [Daten] unterteilt. Alle Felder im
   ersten Abschnitt folgen dem Muster schluessel=wert und werden entsprechend eingelesen und
   gespeichert (ausgewaehlte Felder als float, der Rest als Strings).
   Der zweite Abschnitt startet nach [Daten] mit einer Kopfzeile. Anschliessend folgen mehrere
   Zeilen an Messdaten, wobei die einzelnen Felder jeweils durch Semikolons getrennt sind.
   Gibt die eingelesenen Daten als Struktur mit dem Schluessel Einax zurueck.
   """
   import csv
   from .datenstruktur import Datenstruktur
   #
   daten = Datenstruktur();
   headerzahlen = ['Probenhoehe', 'Probendurchmesser', 'Probenmasse', 'Setzungsdifferenz',
                   'delta Sigma', 'Zeit', 'Aufnehmernummer', 'Versuchsende', 'Schergeschwindigkeit'];
   spaltennamen = [];
   versuchsdaten = [];
   with open(dateiname, 'r', encoding='iso-8859-15') as eingabe:
      eingelesen = csv.reader(eingabe, delimiter=';');
      datenbereich = False;
      for zeile in eingelesen:
         # Header gesondert betrachten
         if (len(zeile) == 1):
            if (zeile[0][0] == '['):
               continue;
            #
            schluessel, wert = zeile[0].split('=');
            if (schluessel in headerzahlen):
               daten.update([(schluessel, float(wert.replace(',', '.')))]);
            else:
               daten.update([(schluessel, wert)]);
            #
            continue;
         #
         if (not datenbereich):
            spaltennamen = zeile;
            datenbereich = True;
            continue;
         #
         temp_daten = [];
         for idx_wert, wert in enumerate(zeile):
            if (idx_wert == 1):
               temp_daten += [wert];
            else:
               temp_daten += [float(wert.replace(',', '.'))];
         #
         versuchsdaten += [temp_daten];
   #
   messdaten = Datenstruktur();
   for idx_eintrag, name in enumerate(spaltennamen):
      messdaten.update([(name, [datenzeile[idx_eintrag] for datenzeile in versuchsdaten])]);
   #
   daten.update([('Daten', messdaten)]);
   daten.update([('Dateiname', dateiname)]);
   rueckgabe = Datenstruktur();
   rueckgabe.update([('EAX', daten)]);
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def LeseDTADaten(dateiname):
   """Lese und interpretiere dta-Dateien, die nach folgendem Schema aufgebaut sind:
   Die Datei ist in die beiden Abschnitte [Versuchsdaten] und [Daten] unterteilt. Alle Felder im
   ersten Abschnitt folgen dem Muster schluessel=wert und werden entsprechend eingelesen und
   gespeichert (ausgewaehlte Felder als float, der Rest als Strings).
   Der zweite Abschnitt startet nach [Daten] mit einer Kopfzeile. Anschliessend folgen mehrere
   Zeilen an Messdaten, wobei die einzelnen Felder jeweils durch Tabulatoren getrennt sind.
   Gibt die eingelesenen Daten als Struktur mit dem Schluessel Einax zurueck.
   """
   import csv
   from .datenstruktur import Datenstruktur
   #
   daten = Datenstruktur();
   headerzahlen = ['Durchmesser', 'Einbauprobenfeuchtmasse', 'Anfangshöhe', 'Masse Kopfplatte'];
   spaltennamen = [];
   versuchsdaten = [];
   with open(dateiname, 'r', encoding='iso-8859-15') as eingabe:
      eingelesen = csv.reader(eingabe, delimiter='\t');
      datenbereich = False;
      for zeile in eingelesen:
         # Header gesondert betrachten
         if (len(zeile) == 1):
            if (zeile[0][0] == '['):
               continue;
            #
            schluessel, wert = zeile[0].split('=');
            schluessel = schluessel.strip();
            if (schluessel in headerzahlen):
               daten.update([(schluessel, float(wert.replace(',', '.')))]);
            else:
               daten.update([(schluessel, wert)]);
            #
            continue;
         #
         if (not datenbereich):
            spaltennamen = zeile;
            datenbereich = True;
            continue;
         #
         temp_daten = [];
         for idx_wert, wert in enumerate(zeile):
            if ((idx_wert == 1) or (idx_wert >= 6)):
               temp_daten += [wert];
            else:
               temp_daten += [float(wert.replace(',', '.'))];
         #
         versuchsdaten += [temp_daten];
   #
   messdaten = Datenstruktur();
   for idx_eintrag, name in enumerate(spaltennamen):
      messdaten.update([(name, [datenzeile[idx_eintrag] for datenzeile in versuchsdaten])]);
   #
   daten.update([('Daten', messdaten)]);
   daten.update([('Dateiname', dateiname)]);
   rueckgabe = Datenstruktur();
   rueckgabe.update([('DTA', daten)]);
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def LeseGDSDaten(dateiname):
   """Lese und interpretiere gds-Dateien, die nach folgendem Schema aufgebaut sind:
   Alle Eintraege sind in doppelten Anfuehrungszeichen und mit Kommata voneinander getrennt. Im
   Header der Datei steht immer ein Wert und ein Schluessel, die alle eingelesen werden
   (ausgewaehlte Felder als float, der Rest als Strings).
   Der Header wird vom Rest durch eine Zeile getrennt, die mehr als zwei Eintraege enthaelt (die
   Bezeichnungen fuer die folgenden Messdaten). Anschliessend folgen Zeilen an Messdaten,
   die wiederum in Anfuehrungszeichen stehen und durch Kommata voneinander getrennt sind.
   Gibt die eingelesenen Daten als Struktur mit dem Schluessel Triax zurueck.
   """
   from .datenstruktur import Datenstruktur
   #
   daten = Datenstruktur();
   headerzahlen = ['Initial Height (mm)', 'Initial Diameter (mm)', 'Ram Diameter',
                   'Specific Gravity (kN/m³):', 'Depth:', 'Initial mass (g):', 'Initial dry mass (g):',
                   'Specific Gravity (ass/meas):', 'Final Mass:', 'Final Dry Mass:', 'Cell No.:',
                   'Membrane Thickness (mm):', 'Start of Repeated Data'];
   spaltennamen = [];
   versuchsdaten = [];
   with open(dateiname, 'r', encoding='iso-8859-15') as eingabe:
      datenbereich = False;
      for ganzezeile in eingabe:
         ganzezeile = ganzezeile.rstrip('\r\n');
         ganzezeile = ganzezeile[1:-1];
         zeile = ganzezeile.split('","');
         # Header gesondert betrachten
         if (len(zeile) == 2):
            if ((zeile[0] in headerzahlen) and (zeile[1] != '')):
               daten.update([(zeile[0], float(zeile[1].replace(',', '.')))]);
            else:
               daten.update([(zeile[0], zeile[1])]);
            #
            continue;
         #
         if (not datenbereich):
            spaltennamen = zeile;
            datenbereich = True;
            continue;
         #
         versuchsdaten += [[float(wert.replace(',', '.')) for wert in zeile]];
   #
   messdaten = Datenstruktur();
   for idx_eintrag, name in enumerate(spaltennamen):
      messdaten.update([(name, [datenzeile[idx_eintrag] for datenzeile in versuchsdaten])]);
   #
   daten.update([('Daten', messdaten)]);
   daten.update([('Dateiname', dateiname)]);
   #
   rueckgabe = Datenstruktur();
   rueckgabe.update([('GDS', daten)]);
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def LeseTVCDaten(dateiname):
   """Lese und interpretiere tvc-Dateien, die nach folgendem Schema aufgebaut sind:
   Im Header der Datei steht immer ein Wert und ein Schluessel durch ein Gleichheitszeichen
   getrennt, die alle eingelesen werden (ausgewaehlte Felder als float, der Rest als Strings).
   Der Header wird vom Rest durch eine Ende-Zeile getrennt, und anschliessend folgen betitelte
   Abschnitte mit Messdaten (ohne Header). Die Messdaten aus allen Abschnitten werden
   zusammengefuegt, aber die Indizes zum Start jedes (neuen) Abschnitts werden ebenfalls
   gespeichert. Gibt die eingelesenen Daten als Struktur mit dem Schluessel Triax zurueck.
   """
   from .datenstruktur import Datenstruktur
   #
   daten = Datenstruktur();
   headerzahlen = ['Intervall', 'Zelle', 'Hoehe', 'Durchmesser', 'Anf-Feuchtmasse', 'Trockenmasse',
                   'End-Feuchtmasse', 'Sättigungsdruck', 'Zelldruch', 'Schergeschwindigkeit',
                   'Korndichte', 'Fläche-Beginn', 'Höhe-Beginn', 'TA - Spannungskreise'];
   spaltennamen = ['Datum/Zeit', 'Radialdruck [kN/m^2]', 'Porenwasserdruck [kN/m^2]',
                   'Druck_undef [kN/m^2]', 'Axialkraft [kN]', 'Stauchung [mm]',
                   'Stauchung_undef [mm]', 'Stauchung_undef(2) [mm]'];
   versuchsdaten = [];
   header = True;
   idx_daten = 0;
   schritte = [];
   with open(dateiname, 'r', encoding='iso-8859-15') as eingabe:
      for zeile in eingabe:
         zeile = zeile.rstrip('\r\n');
         if (header):
            tempzeile = zeile.split('=');
            # Header gesondert betrachten
            if (len(tempzeile) == 2):
               if ((tempzeile[0] in headerzahlen) and (tempzeile[1] != '')):
                  daten.update([(tempzeile[0], float(tempzeile[1].replace(',', '.')))]);
               else:
                  daten.update([(tempzeile[0], tempzeile[1])]);
               #
               continue;
            #
            if (zeile == '---- Ende ----'):
               header = False;
               continue;
         #
         if ('---' in zeile):
            schritte += [[zeile[4:-4], idx_daten]];
            continue;
         #
         idx_daten += 1;
         #
         tempzeile = zeile.split();
         temp_daten = [];
         for idx_wert, wert in enumerate(tempzeile):
            if (idx_wert == 0):
               continue;
            if (idx_wert == 1):
               temp_daten += [tempzeile[0] + ' ' + tempzeile[1]];
            else:
               temp_daten += [float(wert.replace(',', '.'))];
         #
         versuchsdaten += [temp_daten];
   #
   messdaten = Datenstruktur();
   for idx_eintrag, name in enumerate(spaltennamen):
      messdaten.update([(name, [datenzeile[idx_eintrag] for datenzeile in versuchsdaten])]);
   #
   messdaten.update([('Schritte', schritte)]);
   daten.update([('Daten', messdaten)]);
   daten.update([('Dateiname', dateiname)]);
   #
   rueckgabe = Datenstruktur();
   rueckgabe.update([('TVC', daten)]);
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def Interpolationsblock_Aus_KVSdaten(korndurchmesser, sum_masseprozent, interpolationspunkte=24,
   nursiebung=True):
   """Ermittle anhand von der uebergebenen Werte korndurchmesser und sum_masseprozent eine geeignete
   Interpolation der Daten. Bestimme zusaetzlich die Ungleichfoermigkeitszahl und Kruemmungszahl,
   falls nursiebung=True. Gibt eine Struktur mit den interpolierten und berechneten Werten zurueck.
   """
   from .datenstruktur import Datenstruktur
   from .gleichungsloeser import Spline2DInterpolation, LinearInterpoliertenIndexUndFaktor
   #
   block_interpoliert = Datenstruktur();
   # Fuege fuer die Interpolation eine Punkt direkt hinter dem Startpunkt und direkt vor dem Endpunkt hinzu,
   # um eine horizontale Tangente am Anfang und am Ende zu erzielen
   tol = 1e-6;
   #
   x_inter, y_inter = Spline2DInterpolation(xwerte=[korndurchmesser[0]+tol] + korndurchmesser + [korndurchmesser[-1]-tol],
      ywerte=[sum_masseprozent[0]] + sum_masseprozent + [sum_masseprozent[-1]],
      zwischenpunkte=interpolationspunkte, tangentenfaktor=0.75);
   if (nursiebung):
      if ((min(y_inter) < 10.0) and (max(y_inter) > 60.0)):
         idx10, faktor10 = LinearInterpoliertenIndexUndFaktor(vergleichswert=10.0, vergleichswertliste=y_inter);
         idx30, faktor30 = LinearInterpoliertenIndexUndFaktor(vergleichswert=30.0, vergleichswertliste=y_inter);
         idx60, faktor60 = LinearInterpoliertenIndexUndFaktor(vergleichswert=60.0, vergleichswertliste=y_inter);
         d10 = x_inter[idx10] + faktor10*(x_inter[idx10+1] - x_inter[idx10]);
         d30 = x_inter[idx30] + faktor30*(x_inter[idx30+1] - x_inter[idx30]);
         d60 = x_inter[idx60] + faktor60*(x_inter[idx60+1] - x_inter[idx60]);
         Ungleichfoermigkeitszahl = d60/d10;
         Kruemmungszahl = d30*d30/(d10*d60);
         block_interpoliert.update([('Ungleichfoermigkeitszahl [-]', round(10.0*Ungleichfoermigkeitszahl)/10.0)]);
         block_interpoliert.update([('Kruemmungszahl [-]', round(10.0*Kruemmungszahl)/10.0)]);
   #
   block_interpoliert.update([('Siebdurchmesser [mm]', x_inter)]);
   block_interpoliert.update([('Summierte Masseanteile Gesamtmenge [%]', y_inter)]);
   #
   return block_interpoliert;
#


# -------------------------------------------------------------------------------------------------
def LeseKVSDaten(dateiname):
   """Lese und interpretiere kvs-Dateien, die mit der Software GGU Sieve erstellt worden sind.
   In diesen Dateien befinden sich fuer jede Koernungslinie Bloecke mit allgemeinen Informationen
   zum Boden (Name, Bezeichnung, Trockendichte) sowie ggfs. verwendeten Werten (Araeometerdaten)
   und Messdaten der Siebung und Schlaemmung.
   Die Datenpunkte werden zuerst in die prozentualen Masseanteile an der Gesamtmenge umgerechnet
   und dann (mit kubischen Splines) an mehreren Stuetzstellen interpoliert. Anschliessend werden
   charakteristische Werte fuer jede Koernungslinie bestimmt. Gibt die eingelesenen und berechneten
   Daten als Struktur mit dem Schluessel Kornverteilung zurueck.
   """
   from math import sqrt
   from .datenstruktur import Datenstruktur
   #
   daten = Datenstruktur();
   #
   zeile_Ignorieren = True;
   # 5 und 6 sind in diesen Dateien Schalter fuer True/Aktiviert (5) oder False/Deaktiviert (6)
   start_Code = ['\n5\n6\n6\n', '\n6\n6\n6\n'];
   # start_Code '5\n\n6\n6\n' sind scheinbar die deaktivierten, d.h. nur als Flaeche eingezeichneten Daten
   end_Code = '\n\n\n\n';
   codefolge = ['', '', '', ''];
   len_folge = len(codefolge);
   #
   araeometerbezeichnungen = ['Volumen Birne [cm^3]', 'Flaeche Messzylinder [cm^2]',
      'Laenge Birne [cm]', 'Laenge Skala [cm]', 'Abstand Birne-Skala [cm]', 'Meniskuskorrektur'];
   #
   idx_blockzeile = -1;
   teilsiebung = False;
   idx_block = 0;
   with open(dateiname, 'r', encoding='iso-8859-15') as eingabe:
      for idx_zeile, zeile in enumerate(eingabe):
         zeile = zeile.rstrip('\n');
         zeile = zeile.rstrip('\r');
         zeile += '\n';
         codefolge[idx_zeile % len_folge] = zeile;
         code = ''.join([codefolge[(1 + idx_eintrag + idx_zeile) % len_folge] for idx_eintrag in range(len_folge)]);
         #print(repr(code))
         if (code in start_Code) and (zeile_Ignorieren):
            gleichemassen = True;
            if (code == '\n5\n6\n6\n'):
               gleichemassen = False;
            #
            temp_block = Datenstruktur();
            idx_block += 1;
            siebwerte = [];
            siebung = False;
            schlaemmwerte = [];
            schlaemmung = False;
            teilsiebung = False;
            temp_araeometer = Datenstruktur();
            zeile_Ignorieren = False;
            continue;
         #
         if ((code == end_Code) or ('MINCAD' in zeile)) and (not zeile_Ignorieren):
            siebdurchmesser = [];
            schlaemmdurchmesser = [];
            sum_masseprozent = [];
            if (siebung):
               trockenmasse_sieb = temp_block['Trockenmassen [g]'][0];
               siebdurchmesser = [eintrag[0] for eintrag in siebwerte];
               siebdurchmesser = list(reversed(siebdurchmesser[:-1]));
               temp_block.update([('Siebdurchmesser [mm]', siebdurchmesser)]);
               #
               siebmassen = [eintrag[1] for eintrag in siebwerte];
               siebmassen = list(reversed(siebmassen[1:]));
               temp_block.update([('Siebmassen [g]', siebmassen)]);
               #
               sum_massen = [sum(siebmassen[:idx+1]) for idx in range(len(siebmassen))];
               if ('Teilsiebung-Durchmesser [mm]' in temp_block):
                  teilsiebunggroesse = temp_block['Teilsiebung-Durchmesser [mm]'];
                  teilsiebungmasse = temp_block['Teilsiebung-Masse [g]'];
                  idx_teilsieb = None;
                  for idx_sieb, temp_siebgroesse in enumerate(siebdurchmesser):
                     if (temp_siebgroesse > teilsiebunggroesse):
                        idx_teilsieb = idx_sieb;
                        break;
                  #
                  prozentrest = 1.0 - sum([einzelmasse for einzelmasse in siebmassen[idx_teilsieb:]])/trockenmasse_sieb;
                  for idx_sieb, temp_siebgroesse in enumerate(siebdurchmesser):
                     if (idx_sieb <= idx_teilsieb):
                        sum_masseprozent += [100.0*sum_massen[idx_sieb]/teilsiebungmasse*prozentrest];
                     else:
                        sum_masseprozent += [sum_masseprozent[idx_teilsieb] + 100.0*(sum_massen[idx_sieb]-sum_massen[idx_teilsieb])/trockenmasse_sieb];
                  #
               else:
                  sum_masseprozent = [100.0*sum_massen[idx]/sum_massen[-1] for idx in range(len(siebmassen))];
            #
            if (schlaemmung):
               temp_korndichte = temp_block['Korndichte [g/cm^3]'];
               trockenmasse_schlaemm = temp_block['Trockenmassen [g]'][1];
               if (gleichemassen):
                  if (siebung):
                     trockenmasse_schlaemm = sum_massen[0];
                  else:
                     print('# Warnung: Die Referenzmasse bei der Schlaemmung ist uneindeutig');
               #
               schlaemmzeiten = [eintrag[0] for eintrag in schlaemmwerte];
               schlaemmzeiten = list(reversed(schlaemmzeiten));
               schlaemmtemperaturen = [eintrag[1] for eintrag in schlaemmwerte];
               schlaemmtemperaturen = list(reversed(schlaemmtemperaturen));
               schlaemmdichten = [eintrag[2] for eintrag in schlaemmwerte]; # Sind bei uns schon die R-Werte der Norm
               schlaemmdichten = list(reversed(schlaemmdichten));
               #
               # Formeln (4) und (5) sowie Stokessche Gleichung aus Bild 3 von DIN 18123
               zaehigkeit_w = [0.00178/(1.0 + 0.0337*temp + 0.00022*temp**2) for temp in schlaemmtemperaturen];
               dichte_w = [1.0/(1.0+((2.31*temp-2.0)**2 -182.0)*1e-6) for temp in schlaemmtemperaturen];
               #
               h_s = [temp_araeometer['Laenge Skala [cm]'] / (1.03 - 0.995)*(1.03 - (wert/1000.0 + 1.0)) for wert in schlaemmdichten];
               refhoehen = [einzel_h_s + temp_araeometer['Abstand Birne-Skala [cm]'] \
                  + 0.5*(temp_araeometer['Laenge Birne [cm]'] - temp_araeometer['Volumen Birne [cm^3]']/temp_araeometer['Flaeche Messzylinder [cm^2]']) for einzel_h_s in h_s];
               refdurchmesser = [sqrt(18.35*zaehigkeit_w[idx]/(temp_korndichte - dichte_w[idx])*refhoehen[idx]/(60.0*schlaemmzeiten[idx])) for idx in range(len(schlaemmzeiten))];
               schlaemmdurchmesser = [round(refwert*1e4)/1e4 for refwert in refdurchmesser];
               #
               # Formel fuer Temperaturkorrekturwert aus Tabelle 3 von DIN 18123
               massetempkorrektur = [0.0053*schlaemmtemperaturen[idx]**2-0.0082*schlaemmtemperaturen[idx]-1.9568 for idx in range(len(schlaemmtemperaturen))];
               masse_korrigiert = [schlaemmdichten[idx] + temp_araeometer['Meniskuskorrektur'] + massetempkorrektur[idx] for idx in range(len(schlaemmtemperaturen))];
               masseprozent = [100.0/trockenmasse_schlaemm*temp_korndichte/(temp_korndichte - 1.0)*masse for masse in masse_korrigiert];
               #
               temp_block.update([('Schlaemmzeiten [min]', schlaemmzeiten)]);
               temp_block.update([('Schlaemmtemperaturen [C]', schlaemmtemperaturen)]);
               temp_block.update([('Schlaemmdichten [g/cm^3]', schlaemmdichten)]);
               temp_block.update([('Schlaemmdurchmesser [mm]', schlaemmdurchmesser)]);
               temp_block.update([('Schlaemmmasse-korrigiert [g]', masse_korrigiert)]);
               temp_block.update([('Schlaemm-Masseprozent [%]', masseprozent)]);
               #
               temp_block.update([('Araeometerdaten', temp_araeometer)]);
               #
               if (siebung):
                  while (schlaemmdurchmesser[-1] > siebdurchmesser[0]):
                     schlaemmdurchmesser = schlaemmdurchmesser[:-1];
                     masseprozent = masseprozent[:-1];
                  #
                  sum_masseprozent = [sum_massen[0]/trockenmasse_sieb*temp_masse for temp_masse in masseprozent] + sum_masseprozent;
               else:
                  sum_masseprozent = [100.0/masseprozent[-1]*temp_masse for temp_masse in masseprozent];
            #
            korndurchmesser = schlaemmdurchmesser + siebdurchmesser;
            temp_block.update([('Korndurchmesser [mm]', korndurchmesser)]);
            temp_block.update([('Summierte Masseanteile Gesamtmenge [%]', sum_masseprozent)]);
            #
            daten.update([('Sieblinie ' + str(idx_block), temp_block)]);
            idx_blockzeile = -1;
            zeile_Ignorieren = True;
            continue;
         #
         if (zeile_Ignorieren):
            continue;
         #
         # Hier angekommen befinden wir uns im aktuellen Block
         mod_zeile = zeile[:-1];
         if ('\t' in mod_zeile):
            mod_zeile = mod_zeile[0:mod_zeile.index('\t')];
         #
         idx_blockzeile += 1;
         if (idx_blockzeile < 4):
            schluesselliste = ['Ort', 'Entnahmestelle', 'Tiefe', 'Bodenart'];
            temp_block.update([(schluesselliste[idx_blockzeile], mod_zeile)]);
         elif (idx_blockzeile == 4):
            # Trockenmasse Siebung und Trockenmasse Schlaemmung
            temp_block.update([('Trockenmassen [g]', [float(eintrag) for eintrag in mod_zeile.split()])]);
         elif (idx_blockzeile == 5):
            temp_block.update([('Korndichte [g/cm^3]', float(mod_zeile))]);
         elif (idx_blockzeile == 6):
            if ('5' in mod_zeile):
               teilsiebung = True;
         elif (idx_blockzeile == 7):
            if (teilsiebung):
               temp_block.update([('Teilsiebung-Durchmesser [mm]', float(mod_zeile))]);
         elif (idx_blockzeile == 8):
            if (teilsiebung):
               temp_block.update([('Teilsiebung-Masse [g]', float(mod_zeile))]);
         elif (idx_blockzeile == 9):
            continue;
         elif (idx_blockzeile == 10):
            araeometerdaten = [float(eintrag) for eintrag in mod_zeile.split()];
            for idx_wert in range(len(araeometerbezeichnungen)):
               temp_araeometer.update([(araeometerbezeichnungen[idx_wert], araeometerdaten[idx_wert])]);
            #
         elif (idx_blockzeile == 11):
            schalter = mod_zeile.split();
            if (schalter[0] == '5'):
               siebung = True;
            #
            if (schalter[1] == '5'):
               schlaemmung = True;
         #
         elif ((idx_blockzeile > 10) and (idx_blockzeile < 44)):
            zeilenstuecke = mod_zeile.split();
            if (len(zeilenstuecke) == 3):
               if (zeilenstuecke[2] == '5'):
                  siebwerte += [(float(zeilenstuecke[0]), float(zeilenstuecke[1]))];
            #
            elif (len(zeilenstuecke) == 4):
               stunden = float(zeilenstuecke[0]);
               if (stunden >= 0.0):
                  schlaemmwerte += [(stunden*60.0 + float(zeilenstuecke[1]), float(zeilenstuecke[2]), float(zeilenstuecke[3]))];
   #
   daten.update([('Dateiname', dateiname)]);
   #
   rueckgabe = Datenstruktur();
   rueckgabe.update([('KVS', daten)]);
   return rueckgabe;
#

