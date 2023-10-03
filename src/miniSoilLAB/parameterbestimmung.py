# -*- coding: utf-8 -*-
"""
parameterbestimmung.py   v0.6 (2021-06)
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
def HypoplastischeParameterFuerBoden(boden, referenzspannungen, einflussintervall=0.0625):
   """Bestimme die hypoplastischen Parameter aus den unter boden eingelesenen Labordaten des
   Referenzbodens. Durch die Spannungsabhaengigkeit der hypoplastischen Parameter muessen die
   beiden referenzspannungen (untere und obere) angegeben werden, fuer die die Parameter bestimmt
   werden sollen. Fuer Details und Informationen zu den optionalen Parametern siehe auch
   HypoplastischeParameterBestimmen().
   """
   from .datenstruktur import Datenstruktur
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
   #
   direkt = True;
   # Zuerst probieren, aus allen Einzeldaten zu verwenden
   for voraussetzung in ['LoDi', 'Oedo-CRS', 'Triax-D', 'Auswertung-Hypoplastisch']:
      if (voraussetzung not in boden):
         print('# Warnung: Eintrag ' + voraussetzung + ' fehlt zur Direktermittlung der Parameter');
         direkt = False;
         break;
   #
   if (direkt):
      if (any([(daten not in boden['Triax-D']) for daten in ['Triax-D-locker', 'Triax-D-dicht']])):
         print('# Warnung: lockerer und dichter Triax zur Direktermittlung der Parameter benoetigt');
         direkt = False;
   #
   if (direkt):
      try:
         reibungswinkel_krit = boden['Auswertung-Hypoplastisch']['Schuettkegel']['Reibungswinkel-krit [Grad]'];
         porenzahl_min = boden['LoDi']['Porenzahl-min [-]'];
         porenzahl_max = boden['LoDi']['Porenzahl-max [-]'];
         spannungen_oedo_locker = boden['Oedo-CRS']['Oedo-locker']['Spannung [kN/m^2]'];
         porenzahlen_oedo_locker = boden['Oedo-CRS']['Oedo-locker']['Porenzahl [-]'];
         spannungen_oedo_dicht = boden['Oedo-CRS']['Oedo-dicht']['Spannung [kN/m^2]'];
         porenzahlen_oedo_dicht = boden['Oedo-CRS']['Oedo-dicht']['Porenzahl [-]'];
         reibungswinkel_peak_locker = boden['Triax-D']['Triax-D-locker']['Mohr-Coulomb']['Ohne Kohaesion']['Reibungswinkel-eff [Grad]'];
         reibungswinkel_peak_dicht = boden['Triax-D']['Triax-D-dicht']['Mohr-Coulomb']['Ohne Kohaesion']['Reibungswinkel-eff [Grad]'];
         dilatanzwinkel = boden['Triax-D']['Triax-D-dicht']['Versuch 1']['Peakzustand']['Dilatanzwinkel [Grad]'];
         # FIXME: Warum aus Versuch 1 (hat i.d.R. die kleinste Differenz zwischen sig1 und sig3)
         sigma1_prime = boden['Triax-D']['Triax-D-dicht']['Versuch 1']['Peakzustand']['Sigma_1_prime [kN/m^2]'];
         sigma3_prime = boden['Triax-D']['Triax-D-dicht']['Versuch 1']['Peakzustand']['Sigma_3_prime [kN/m^2]'];
         spannung_peak_mittel = (sigma1_prime + 2.0*sigma3_prime)/3.0;
         porenzahl_peak = boden['Triax-D']['Triax-D-dicht']['Versuch 1']['Peakzustand']['Porenzahl [-]'];
      except KeyError as errormessage:
         print('Eintrag ' + str(errormessage) + ' fuer Direktermittlung der Parameter fehlt/ungueltig');
         direkt = False;
   #
   if (not direkt):
      try:
         reibungswinkel_krit = boden['Auswertung-Hypoplastisch']['Schuettkegel']['Reibungswinkel-krit [Grad]'];
         porenzahl_min = boden['Auswertung-Hypoplastisch']['Schuettkegel']['Porenzahl-min [-]'];
         porenzahl_max = boden['Auswertung-Hypoplastisch']['Schuettkegel']['Porenzahl-max [-]'];
         spannungen_oedo_locker = boden['Auswertung-Hypoplastisch']['Oedo-locker']['Spannung [kN/m^2]'];
         porenzahlen_oedo_locker = boden['Auswertung-Hypoplastisch']['Oedo-locker']['Porenzahl [-]'];
         spannungen_oedo_dicht = boden['Auswertung-Hypoplastisch']['Oedo-dicht']['Spannung [kN/m^2]'];
         porenzahlen_oedo_dicht = boden['Auswertung-Hypoplastisch']['Oedo-dicht']['Porenzahl [-]'];
         reibungswinkel_peak_locker = boden['Auswertung-Hypoplastisch']['Triax-D']['Reibungswinkel-Peak-locker [Grad]'];
         reibungswinkel_peak_dicht = boden['Auswertung-Hypoplastisch']['Triax-D']['Reibungswinkel-Peak-dicht [Grad]'];
         dilatanzwinkel = boden['Auswertung-Hypoplastisch']['Triax-D']['Dilatanzwinkel [Grad]'];
         spannung_peak_mittel = boden['Auswertung-Hypoplastisch']['Triax-D']['Spannung-Peak-eff [kN/m^2]'];
         porenzahl_peak = boden['Auswertung-Hypoplastisch']['Triax-D']['Porenzahl-Peak [-]'];
      except KeyError as errormessage:
         print('# Hinweis: Erforderliche Daten ' + str(errormessage) + ' fuer hypoplastische Parameter nicht vorhanden');
         return [];
   #
   parameter = HypoplastischeParameterBestimmen(reibungswinkel_krit=reibungswinkel_krit,
      porenzahl_min=porenzahl_min, porenzahl_max=porenzahl_max,
      spannungen_oedo_locker=spannungen_oedo_locker, porenzahlen_oedo_locker=porenzahlen_oedo_locker,
      spannungen_oedo_dicht=spannungen_oedo_dicht, porenzahlen_oedo_dicht=porenzahlen_oedo_dicht,
      reibungswinkel_peak_locker=reibungswinkel_peak_locker,
      reibungswinkel_peak_dicht=reibungswinkel_peak_dicht, dilatanzwinkel=dilatanzwinkel,
      spannung_peak_mittel=spannung_peak_mittel, porenzahl_peak=porenzahl_peak,
      referenzspannungen=referenzspannungen, einflussintervall=einflussintervall);
   if (parameter != []):
      auswertung = GespeicherterWertOderUebergabe(daten=boden['Auswertung-Hypoplastisch'],
         bezeichnung='Parameter-miniSoilLAB', uebergabe=Datenstruktur());
      auswertung.update([('Parameter', parameter)]);
      auswertung.update([('Parameter-Hilfe', ['phi_c [Grad]', 'h_s [MPa]', 'n [-]', 'e_d [-]',
      'e_c [-]', 'e_i [-]', 'alpha [-]', 'beta [-]'])]);
      #
      einstellungen = GespeicherterWertOderUebergabe(daten=auswertung,
         bezeichnung='Einstellungen', uebergabe=Datenstruktur());
      einstellungen.update([('Referenzspannungen', referenzspannungen)]);
      einstellungen.update([('Einflussintervall', einflussintervall)]);
   #
   return parameter;
#


# -------------------------------------------------------------------------------------------------
def HypoplastischeParameterBestimmen(reibungswinkel_krit, porenzahl_min, porenzahl_max,
   spannungen_oedo_locker, porenzahlen_oedo_locker, spannungen_oedo_dicht, porenzahlen_oedo_dicht,
   reibungswinkel_peak_locker, reibungswinkel_peak_dicht, dilatanzwinkel, spannung_peak_mittel,
   porenzahl_peak, referenzspannungen, einflussintervall=0.0625):
   """Bestimme die hypoplastischen Parameter aus den uebergebenen Parametern verschiedener
   Laborversuche. Es werden benoetigt:
   
   - reibungswinkel_krit (aus Schuettkegelversuch)
   - porenzahl_min und porenzahl_max (aus Dichtebestimmung bei lockerster und dichtester Lagerung)
   - spannungen_oedo_locker und porenzahlen_oedo_locker (aus einem CRS-Oedometer mit lockerer Lagerung)
   - spannungen_oedo_dicht und porenzahlen_oedo_dicht (aus einem CRS-Oedometer mit dichter Lagerung)
   - reibungswinkel_peak_locker (aus einem Triaxialversuch-D mit lockerer Lagerung)
   - reibungswinkel_peak_dicht, dilatanzwinkel und spannung_peak_mittel (aus einem drainierten
         Triaxialversuch (Triax-D) mit dichter Lagerung)
   - referenzspannungen [frei waehlbarer unterer/oberer Referenzspannungspunkt]
   
   Optional kann einflussintervall zur Bestimmung von Stuetzpunkten der referenzspannungen geaendert
   werden. Gibt die hypoplastischen Parameter fuer diese Labordaten zurueck.
   [phi_c,  h_s,   n,   e_d,  e_c,  e_i,  alpha,  beta]
    [rad]   [MPa]  [-]  [-]   [-]   [-]   [-]     [-]
   """
   from math import log10, log, exp, sqrt, sin, tan
   from .konstanten import grad2rad, debugmodus
   from .gleichungsloeser import LinearInterpoliertenIndexUndFaktor
   #
   wertspanne = einflussintervall;
   if (einflussintervall > 1.0/12.0):
      if (debugmodus):
         print('# Hinweis: einflussintervall muss kleiner/gleich 1/12 sein - ersetze aktuellen Wert mit 1/12');
      #
      wertspanne = 1.0/12.0;
   #
   if (spannungen_oedo_dicht[0] == 0.0):
      spannungen_oedo_dicht = spannungen_oedo_dicht[1:];
      porenzahlen_oedo_dicht = porenzahlen_oedo_dicht[1:];
   #
   if (spannungen_oedo_locker[0] == 0.0):
      spannungen_oedo_locker = spannungen_oedo_locker[1:];
      porenzahlen_oedo_locker = porenzahlen_oedo_locker[1:];
   #
   min_spannung = max(min(spannungen_oedo_locker), min(spannungen_oedo_dicht));
   max_spannung = min(max(spannungen_oedo_locker), max(spannungen_oedo_dicht));
   log_spannungsbereich = log10(max_spannung) - log10(min_spannung);
   #
   spannung_C, spannung_F = referenzspannungen;
   if (spannung_F < spannung_C):
      temp_spannung = spannung_F;
      spannung_F = spannung_C;
      spannung_C = temp_spannung;
      #
      if (debugmodus):
         print('# Hinweis: Obere Referenzspannung kleiner als untere Referenzspannung - tausche Werte');
   #
   # Obere Grenze ist egal, aber aufgrund des Logarithmus muss der Minimalwert groesser als Null sein
   if (spannung_C < 1e-6):
      spannung_C = 1e-6;
   #
   if (spannung_C == spannung_F):
      spannung_F = 2.0*spannung_C;
      if (debugmodus):
         print('# Hinweis: Untere und obere Referenzspannung identisch - verdopple obere Referenzspannung');
   #
   # Um sicherzustellen, dass der Wert aufgrund von Rundungs- und Rechenungenauigkeiten echt innerhalb
   # des gueltigen Intervalls liegt, wird ein zusaetzlicher Faktor verwendet
   sicherheitsfak = 1.01;
   if (10**(log10(spannung_C) - wertspanne*log_spannungsbereich) < min_spannung):
      spannung_C = 10**(log10(min_spannung) + sicherheitsfak*wertspanne*log_spannungsbereich);
      if (debugmodus):
         print('# Hinweis: Untere Referenzspannung unter der Intervallgrenze - ersetze durch ' + str(spannung_C));
   #
   if (10**(log10(spannung_F) + wertspanne*log_spannungsbereich) > max_spannung):
      spannung_F = 10**(log10(max_spannung) - sicherheitsfak*wertspanne*log_spannungsbereich);
      if (debugmodus):
         print('# Hinweis: Obere Referenzspannung ueber der Intervallgrenze - ersetze durch ' + str(spannung_F));
   #
   spannung_A = 10**(log10(spannung_C) - wertspanne*log_spannungsbereich); # [kN/m^2]
   spannung_B = 10**(log10(spannung_C) + wertspanne*log_spannungsbereich); # [kN/m^2]
   spannung_D = 10**(log10(spannung_F) - wertspanne*log_spannungsbereich); # [kN/m^2]
   spannung_E = 10**(log10(spannung_F) + wertspanne*log_spannungsbereich); # [kN/m^2]
   #
   phi_c = reibungswinkel_krit*grad2rad;
   spannungen = [spannung_A, spannung_C, spannung_B, spannung_D, spannung_F, spannung_E];
   mitteldruecke = [(1.0 + 2.0*(1.0 - sin(phi_c)))* einzelspannung/3.0 for einzelspannung in spannungen];
   #
   if (debugmodus):
      print('# Debug: Zwischenwerte bei der Berechnung der hypoplastischen Parameter');
      print('   Spannungen: ' + 'kPa, '.join([str(round(x*10.0)/10.0) for x in spannungen]) + 'kPa');
      print('   Reibungswinkel: ' + str(round(reibungswinkel_krit*10.0)/10.0) + 'Grad');
      print('   Mitteldruecke: ' + 'kPa, '.join([str(round(x*10.0)/10.0) for x in mitteldruecke]) + 'kPa');
   #
   # Daten aus lockerem Oedometer
   porenzahlen_locker = [None for idx in range(6)];
   #setzungen = [None for idx in range(6)];
   for idx in range(6):
      idx_unten, faktor = LinearInterpoliertenIndexUndFaktor(vergleichswert=spannungen[idx], vergleichswertliste=spannungen_oedo_locker);
      if (idx_unten is None):
         print('# Fehler: Interpolation fehlgeschlagen');
         return [];
      #
      porenzahlen_locker[idx] = porenzahlen_oedo_locker[idx_unten] + faktor*(porenzahlen_oedo_locker[idx_unten+1]-porenzahlen_oedo_locker[idx_unten]);
   #
   for idx in range(5):
      if (porenzahlen_locker[idx] <= porenzahlen_locker[idx+1]):
         print('# Warnung: Ungültiger Porenzahlverlauf (Oedo-CRS locker)');
         return [];
      #
      if (mitteldruecke[idx] >= mitteldruecke[idx+1]):
         print('# Warnung: Ungültiger Spannungsverlauf (Oedo-CRS locker)');
         return [];
   #
   if (debugmodus):
      print('   Porenzahlen (Oedo-locker): ' + ', '.join([str(round(x*1e3)/1e3) for x in porenzahlen_locker]));
   #
   A_porenzahl, C_porenzahl, B_porenzahl, D_porenzahl, F_porenzahl, E_porenzahl = porenzahlen_locker;
   A_mittelspannung, C_mittelspannung, B_mittelspannung, D_mittelspannung, F_mittelspannung, E_mittelspannung = mitteldruecke;
   #
   # Berechnung von n und h_s
   C_cC = (B_porenzahl-A_porenzahl)/(log(A_mittelspannung)-log(B_mittelspannung));
   C_cF = (E_porenzahl-D_porenzahl)/(log(D_mittelspannung)-log(E_mittelspannung));
   #
   n = log((C_porenzahl*C_cF)/(F_porenzahl*C_cC)) / log(F_mittelspannung/C_mittelspannung);
   h_s = 3.0*C_mittelspannung * (n*C_porenzahl/C_cC)**(1.0/n);
   #
   # Porenzahlen
   e_d = porenzahl_min;
   e_c = porenzahl_max;
   e_i = 1.15*porenzahl_max;
   #
   if (debugmodus):
      print('   C_cC=' + str(round(C_cC*1e5)/1e5) + ', C_cF=' + str(round(C_cF*1e5)/1e5) \
         + ', n=' + str(round(n*1e3)/1e3) + ', h_s=' + str(round(h_s)) + 'kPa');
      print('   e_d=' + str(round(e_d*1e3)/1e3) + ', e_c=' + str(round(e_c*1e3)/1e3) \
         + ', e_i=' + str(round(e_i*1e3)/1e3));
   #
   # Berechnung von alpha
   porenzahl_peak_null = porenzahl_peak / exp(-(3.0*spannung_peak_mittel/h_s)**n);
   r_e = (porenzahl_peak_null-porenzahl_min) / (porenzahl_max-porenzahl_min);
   if (r_e <= 0.0):
      print('# Fehler: r_e=' + str(r_e) + ' muss groesser Null sein ' \
         '(e_peak,0=' + str(round(porenzahl_peak_null*1e3)/1e3) + ')');
      return [];
   #
   K_p = (1.0+sin(reibungswinkel_peak_dicht*grad2rad)) / (1.0-sin(reibungswinkel_peak_dicht*grad2rad));
   a = sqrt(3.0)*(3.0-sin(phi_c)) / (2.0*sqrt(2.0)*sin(phi_c));
   A = (a/(2.0+K_p))**2 * (1.0 - (K_p*(4.0-K_p)) / (5.0*K_p-2.0));
   #
   if (debugmodus):
      print('   e_peak,0=' + str(round(porenzahl_peak_null*1e3)/1e3) + ', r_e=' \
         + str(round(r_e*1e3)/1e3) + ', K_p=' + str(round(K_p*1e3)/1e3) + ', a=' \
         + str(round(a*1e3)/1e3) + ', A=' + str(round(A*1e3)/1e3));
   #
   #tannup = 2.0 * (K_p-4.0+5.0*A*K_p**2-2.0*A*K_p) / ((5.0*K_p-2.0)*(1.0+2.0*A)) - 1.0; # nach Karcher
   tannup = tan(dilatanzwinkel*grad2rad);
   alpha = log(6.0*((2.0+K_p)**2 + a**2 * K_p*(K_p-1.0-tannup)) / (a*(2.0+K_p)*(5*K_p-2)*sqrt(4.0+2.0*(1.0+tannup)**2))) / log(r_e);
   #
   if (debugmodus):
      print('   tannup=' + str(round(tannup*1e3)/1e3) + ', alpha=' + str(round(alpha*1e3)/1e3));
   #
   # Daten aus dichtem Oedometer
   porenzahlen_dicht = [None for idx in range(6)];
   for idx in range(6):
      idx_unten, faktor = LinearInterpoliertenIndexUndFaktor(vergleichswert=spannungen[idx], vergleichswertliste=spannungen_oedo_dicht);
      if (idx_unten is None):
         print('# Fehler: Interpolation fehlgeschlagen');
         return [];
      #
      porenzahlen_dicht[idx] = porenzahlen_oedo_dicht[idx_unten] + faktor*(porenzahlen_oedo_dicht[idx_unten+1]-porenzahlen_oedo_dicht[idx_unten]);
   #
   G_porenzahl, I_porenzahl, H_porenzahl, J_porenzahl, L_porenzahl, K_porenzahl = porenzahlen_dicht;
   G_mittelspannung, I_mittelspannung, H_mittelspannung, J_mittelspannung, L_mittelspannung, K_mittelspannung = mitteldruecke;
   #
   if (debugmodus):
      print('   Porenzahlen (Oedo-dicht): ' + ', '.join([str(round(x*1e3)/1e3) for x in porenzahlen_dicht]));
   #
   # Berechnung von beta
   K_01 = 1.0 - sin(reibungswinkel_peak_locker*grad2rad);
   K_02 = 1.0 - sin(reibungswinkel_peak_dicht*grad2rad);
   #
   F_null_porenzahl = F_porenzahl / exp(-(3.0*F_mittelspannung/h_s)**n);
   r_e1 = (F_null_porenzahl-porenzahl_min)/(porenzahl_max-porenzahl_min);
   #
   C_cL = (K_porenzahl-J_porenzahl) / (log(J_mittelspannung)-log(K_mittelspannung));
   es2_es1 = C_cF/C_cL * (1.0 + L_porenzahl)/(1.0 + F_porenzahl);
   #
   L_null_porenzahl = L_porenzahl / exp(-(3.0*L_mittelspannung/h_s)**n);
   r_e2 = (L_null_porenzahl - porenzahl_min) / (porenzahl_max - porenzahl_min);
   #
   if (debugmodus):
      print('   e_F,null=' + str(round(F_null_porenzahl*1e3)/1e3) + ', r_e1=' \
         + str(round(r_e1*1e3)/1e3));
      print('   e_L,null=' + str(round(L_null_porenzahl*1e3)/1e3) + ', r_e2=' \
         + str(round(r_e2*1e3)/1e3) + ', C_cL=' + str(round(C_cL*1e3)/1e3));
      print('   K_01=' + str(round(K_01*1e3)/1e3) + ', K_02=' + str(round(K_02*1e3)/1e3) \
         + ', es2_es1=' + str(round(es2_es1*1e3)/1e3));
   #
   if ((r_e1 < 0.0) or (r_e2 < 0.0)):
      print('# Fehler: r_e1=' + str(r_e1) + ' und r_e2=' + str(r_e2) + ' muessen groesser Null sein');
      return [];
   #
   fd1 = r_e1**alpha;
   fd2 = r_e2**alpha;
   #
   m1 = (2.0+K_01)**2 + a**2;
   m2 = (2.0+K_02)**2 + a**2;
   #
   n1 = a*(2.0 + K_01)*(5.0 - 2.0*K_01) / 3.0;
   n2 = a*(2.0 + K_02)*(5.0 - 2.0*K_02) / 3.0;
   #
   beta = log(es2_es1*(m1 - n1*fd1)/(m2 - n2*fd2)) / log(F_porenzahl/L_porenzahl);
   #
   if (debugmodus):
      print('   f_d1=' + str(round(fd1*1e3)/1e3) + ', m_1=' + str(round(m1*1e3)/1e3) + ', n_1=' \
         + str(round(n1*1e3)/1e3));
      print('   f_d2=' + str(round(fd2*1e3)/1e3) + ', m_2=' + str(round(m2*1e3)/1e3) + ', n_2=' \
         + str(round(n2*1e3)/1e3) + ', beta=' + str(round(beta*1e3)/1e3));
   #
   return [phi_c, h_s/1000.0, n, e_d, e_c, e_i, alpha, beta];
#


# -------------------------------------------------------------------------------------------------
def ErweiterteHypoplastischeParameterFuerBoden(boden, offset=0, glaettungswert=10, refspanne=3):
   """Bestimme die erweiterten hypoplastischen Parameter aus den unter boden eingelesenen Labordaten
   des Referenzbodens (Triax-p-q). Aufgrund der typischen Schwankungen der Aufzeichnungswerte 
   empfiehlt sich eine Glaettung von Funktionswerten und Ableitung (E-Modul-Entwicklung). Der
   Einflussbereich der Glaettung kann mit glaettungswert gesteuert werden, wobei 0 keiner Glaettung
   entspricht. Der erste zu betrachtende Wert ist offset Stellen nach beginn der letzten Stage des
   Versuchs. Fuer die Bestimmung von R_max werden refspanne Punkte (vor und) nach dem Peakwert
   verwendet, um ein Peakplateau (E_max an der Position R_max) zu bestimmen.
   """
   from .datenstruktur import Datenstruktur
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
   #
   try:
      hoehen = boden['Triax-p-q']['3-Konsolidation']['Hoehe [mm]'];
   except:
      print('# Warnung: Eintrag fuer Hoehe nicht gefunden');
      return [];
   #
   hauptspannungsdifferenzen = [None, None, None];
   stauchungen = [None, None, None];
   for idx in range(3):
      pqvariante = 'Versuch ' + str(int(idx+1));
      try:
         spannungspfad = boden['Triax-p-q'][pqvariante]['Spannungspfad'];
      except:
         print('# Warnung: Nicht alle benoetigen Spannungspfade verfuegbar');
         return [];
      #
      if (spannungspfad == '0 Grad'):
         idx_ausgabe = 0;
      elif (spannungspfad == '90 Grad'):
         idx_ausgabe = 1;
      elif (spannungspfad == '180 Grad'):
         idx_ausgabe = 2;
      else:
         print('# Warnung: Ungueltiger Spannungspfad');
         return [];
      #
      try:
         schritte = boden['Triax-p-q'][pqvariante]['Schritte'][-1];
         stauchungen[idx_ausgabe] = boden['Triax-p-q'][pqvariante]['Stauchung [mm]'][schritte:];
         hauptspannungsdifferenzen[idx_ausgabe] = boden['Triax-p-q'][pqvariante]['Hauptspannungsdifferenz [kN/m^2]'][schritte:];
      except:
         print('# Warnung: \'Schritte\', \'Stauchung [mm]\' oder/und \'Hauptspannungsdifferenz [kN/m^2]\' fuer aktuellen Spannungspfad nicht vorhanden');
         return [];
   #
   if (any([(tempstauchung is None) for tempstauchung in stauchungen])):
      print('# Zuweisung der Spannungspfade fehlerhaft. Es werden exakt ein 0, 90 und 180 Grad Pfad benoetigt');
      return [];
   #
   parameter = ErweiterteHypoplastischeParameterBestimmen(stauchungen=stauchungen, hoehen=hoehen,
      hauptspannungsdifferenzen=hauptspannungsdifferenzen, offset=offset,
      glaettungswert=glaettungswert, refspanne=refspanne);
   if (parameter != []):
      auswertung = GespeicherterWertOderUebergabe(daten=boden['Triax-p-q'],
         bezeichnung='Parameter-miniSoilLAB', uebergabe=Datenstruktur());
      auswertung.update([('Parameter', parameter)]);
      auswertung.update([('Parameter-Hilfen', ['m_T [-]', 'm_R [-]', 'R_max [-]', 'beta_r [-]', 'chi [-]'])]);
      #
      einstellungen = GespeicherterWertOderUebergabe(daten=auswertung,
         bezeichnung='Einstellungen', uebergabe=Datenstruktur());
      einstellungen.update([('Offset', offset)]);
      einstellungen.update([('Glaettungswert', glaettungswert)]);
      einstellungen.update([('Referenzspanne', refspanne)]);
   #
   return parameter;
#


# -------------------------------------------------------------------------------------------------
def _ErweiterteHypoParamHilfsfunktion(eps, q, glaettungswert, refspanne):
   """Hilfsfunktion zur Berechnung der geglaetteten Daten zu eps, q und dem E-Modul.
   Gibt [eps_glatt, q_glatt, e_modul_glatt, R_max, E_max, fitoffset] zurueck.
   """
   from .gleichungsloeser import AbleitungDyNachDx, IntegrationDyMitDx, GlaettungFunktionswerte
   from .gleichungsloeser import SortierenUndDoppelteXEintraegeEntfernen
   from .gleichungsloeser import LinearInterpoliertenIndexUndFaktor
   #
   # Glaetten, Ableiten, Glaetten (und Integrieren fuer noch glattere Funktionswerte)
   epsneu, qneu = SortierenUndDoppelteXEintraegeEntfernen(x=eps, y=q);
   xglatt = GlaettungFunktionswerte(werte=epsneu, glaettungsbereich=glaettungswert);
   yglatt = GlaettungFunktionswerte(werte=qneu, glaettungsbereich=glaettungswert);
   #
   xabl, yabl = AbleitungDyNachDx(x=xglatt, y=yglatt);
   xablglatt = GlaettungFunktionswerte(werte=xabl, glaettungsbereich=glaettungswert);
   yablglatt = GlaettungFunktionswerte(werte=yabl, glaettungsbereich=glaettungswert);
   #
   idx_ablstart, fak_abl = LinearInterpoliertenIndexUndFaktor(vergleichswert=xablglatt[0], vergleichswertliste=xglatt);
   x_0 = xglatt[idx_ablstart] + fak_abl*(xglatt[idx_ablstart+1]-xglatt[idx_ablstart]);
   y_0 = yglatt[idx_ablstart] + fak_abl*(yglatt[idx_ablstart+1]-yglatt[idx_ablstart]);
   #
   dxablglatt = [xablglatt[idx+1] - xablglatt[idx] for idx in range(len(xablglatt)-1)];
   xinteg, yinteg = IntegrationDyMitDx(x0=x_0, y0=y_0, dx=dxablglatt, dy=yablglatt);
   #
   # Werte die y-Daten (q/2) an den x-Werten aus, die fuer die geglaettete Ableitung verwendet werden,
   # damit sowohl das E-Modul als auch q/2 ueber den selben Dehnungen aufgetragen werden kann.
   yglatt_interp = [];
   idx_interpstart = 0;
   for tempx in xablglatt:
      idx_fit, fak_fit = LinearInterpoliertenIndexUndFaktor(vergleichswert=tempx, vergleichswertliste=xglatt[idx_interpstart:]);
      idx_interpstart += idx_fit;
      yglatt_interp += [yglatt[idx_interpstart] + fak_fit*(yglatt[idx_interpstart+1]-yglatt[idx_interpstart])];
   #
   # Bereich um den Maximalwert als Referenzbereich vormerken
   steigung = max(yablglatt);
   x_max = xablglatt[yablglatt.index(steigung)];
   idx_max, fak_max = LinearInterpoliertenIndexUndFaktor(vergleichswert=x_max, vergleichswertliste=xglatt);
   min_idx = max(idx_max-refspanne, 0);
   max_idx = min(idx_max+refspanne, len(xinteg)-1);
   #
   # Mit einem Toleranzwert koennte man auch xinteg[idx_grenz] als R_max betrachten
   xref = xglatt[idx_max] + fak_max * (xglatt[idx_max+1] - xglatt[idx_max]);
   yref = yglatt[idx_max] + fak_max * (yglatt[idx_max+1] - yglatt[idx_max]);
   achsenabstand = yref - steigung*xref;
   #       eps_glatt,  q_glatt,      e_modul_glatt, R_max, E_max,    fitoffset
   return [xablglatt, yglatt_interp, yablglatt,     x_max, steigung, achsenabstand];
#


# -------------------------------------------------------------------------------------------------
def _ErweiterteHypoParamHilfsfunktionEpssom(eps0, eps180, emodul0, emodul180):
   """Bestimme eps_som aus den Verlaufen des E-Moduls ueber der Dehnung. Definitionsgemaess ist
   bei/ab eps_som der Abstand zwischen emodul0 und emodul180 kleiner/gleich 10% von emodul0. Da bei
   der Bestimmung i.A. die E-Module fuer unterschiedliche Dehnungen ausgewertet werden, werden fuer
   einen besseren Vergleich die E-Module an allen gemeinsamen Punkten interpoliert.
   """
   from .gleichungsloeser import FunktionswerteAnGleichenXWerten
   #
   xwerte, emod_R, emod_N = FunktionswerteAnGleichenXWerten(fx=eps180, fy=emodul180,
      gx=eps0, gy=emodul0);
   idx_emax = emod_R.index(max(emod_R));
   idx_som = 0;
   for idx in range(idx_emax, len(xwerte)):
      if (abs((emod_R[idx] - emod_N[idx])/emod_N[idx]) < 0.1):
         idx_som = idx;
         break;
   #
   if (idx_som == len(xwerte)-1):
      print('# Warnung: Bestimmung von eps_som fehlgeschlagen');
   #
   return xwerte[idx_som];
#


# -------------------------------------------------------------------------------------------------
def ErweiterteHypoplastischeParameterBestimmen(stauchungen, hoehen, hauptspannungsdifferenzen,
   offset=0, glaettungswert=10, refspanne=3):
   """Bestimme die erweiterten hypoplastischen Parameter aus den uebergebenen Parametern von
   Triaxialversuchen mit speziellem Spannungspfaden (Triax-p-q). Es werden benoetigt:
   
   - stauchungen von Triaxialversuchen (Triax-p-q) mit einer Lastaenderung von 0, 90 und 180 Grad
   - hoehen der Proben nach dem Konsolidieren von Triaxialversuchen (Triax-p-q) mit einer
         Lastaenderung von 0, 90 und 180 Grad
   - hauptspannungsdifferenzen von Triaxialversuchen (Triax-p-q) mit einer Lastaenderung von 0, 90
         und 180 Grad
   - offset [frei waehlbarer Startpunkt nach Beginn der letzten Stage]
   - glaettungswert [frei waehlbarer Glaettungsparameter, wobei 0 keiner Glaettung entspricht]
   - refspanne [frei waehlbare Spanne an Punkten, die um den Peak zur Bestimmung von E_max genutzt wird]
   """
   from math import exp, log
   from .konstanten import debugmodus
   #
   if (debugmodus):
      print('# Debug: Zwischenwerte bei der Berechnung der erweiterten hypoplastischen Parameter');
   #
   R = [];
   E_modul = [];
   epsglatt = [];
   emodulglatt = [];
   for idx_versuch in range(3):
      # FIXME: q oder q/2
      q2 = [x/2.0 for x in hauptspannungsdifferenzen[idx_versuch][offset:]];
      #q2 = hauptspannungsdifferenzen[idx_versuch][offset:];
      # FIXME: neues epsilon fuer die aktuelle Dehnung?
      eps = [(einzelstauchung-stauchungen[idx_versuch][offset])/(hoehen[idx_versuch]-stauchungen[idx_versuch][offset]) for einzelstauchung in stauchungen[idx_versuch][offset:]];
      #
      tempeps, tempq, tempemodul, R_max, E_max, fitoffset = _ErweiterteHypoParamHilfsfunktion(eps=eps,
         q=q2, glaettungswert=glaettungswert, refspanne=refspanne);
      #
      if (debugmodus):
         print('   Versuch (' + str(idx_versuch+1) + '): R=' + str(round(R_max*1e6)/1e6) + ', E=' \
            + str(round(E_max*1e6)/1e6));
      #
      R += [R_max];
      E_modul += [E_max];
      epsglatt += [tempeps];
      emodulglatt += [tempemodul];
   #
   R_max = R[2];
   m_R = E_modul[2]/E_modul[0];
   m_T = E_modul[1]/E_modul[0];
   #
   # Falls die Kurve von E_90 tendenziell unter E_0 liegt und somit m_T kleiner als eins ist,
   # so kann dies als Spielraum fuer die Werte interpretiert werden (deshalb wird Kehrwert verwendet)
   if (m_T < 1.0):
      m_T = 1.0/m_T;
      if (debugmodus):
         print('# Hinweis: m_T wurde invertiert');
   #
   if (debugmodus):
      print('   R_max=' + str(round(R_max*1e6)/1e6) + ', m_T=' + str(round(m_T*1e2)/1e2) + ', m_R=' \
         + str(round(m_R*1e2)/1e2));
   #
   eps_som = _ErweiterteHypoParamHilfsfunktionEpssom(eps0=epsglatt[0], eps180=epsglatt[2],
      emodul0=emodulglatt[0], emodul180=emodulglatt[2]);
   #
   # FIXME: Bestimmung/Abschaetzung von Chi aus der Kurve selbst
   #        Chi muss echt groesser als eins sein!
   chi = 4.0;
   # Berechnung approximiert an die Kurven aus Bild 13 aus A. Niemunis und I. Herle (1997): Hypoplastic model for cohesionless soil
   zaehler = exp(log(2.25) + (log(4.62) - log(2.25))*((chi-1.0)/9.0)**0.38);
   beta_r = (zaehler*R_max/eps_som)**1.055;
   #
   if (debugmodus):
      print('   eps_som=' + str(round(eps_som*1e6)/1e6) + ', chi=' + str(round(chi*1e2)/1e2) \
         + ', beta_r=' + str(round(beta_r*1e3)/1e3));
   #
   return [m_T, m_R, R_max, beta_r, chi];
#


# -------------------------------------------------------------------------------------------------
def ViskohypoplastischeParameterFuerBoden(boden, intervallgroesse=25, p1logverhaeltnis=0.5,
   p5logverhaeltnis=0.5, zwischenpunkte=5):
   """Bestimme die viskohypoplastischen Parameter aus den unter boden eingelesenen Labordaten des
   Referenzbodens. Fuer Details und Informationen zu den optionalen Parametern siehe auch
   ViskohypoplastischeParameterBestimmen().
   """
   from .datenstruktur import Datenstruktur
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
   #
   try:
      spannungen_crs = boden['Oedo-CRS-Visko']['Spannung [kN/m^2]'];
      porenzahlen_crs = boden['Oedo-CRS-Visko']['Porenzahl [-]'];
      hoehe_crs = boden['Oedo-CRS-Visko']['Hoehe [mm]'];
      stauchungsrate_crs = boden['Oedo-CRS-Visko']['Stauchungsrate [mm/min]'];
      # FIXME: Stimmt so nicht (oder?)
      reibungswinkel_krit = boden['Triax-CU']['Mohr-Coulomb']['Mit Kohaesion']['Reibungswinkel-eff [Grad]'];
   except:
      print('# Warnung: Erforderliche Daten fuer viskohypoplastische Parameter nicht vorhanden');
      return [];
   #
   stunden_crl = [];
   porenzahlen_crl = [];
   laststufen_crl = [];
   for idx in range(1, 9):
      einzelversuch = 'Laststufe ' + str(idx);
      try:
         temp_stunden = boden['Oedo-CRL'][einzelversuch]['Zeit [h]'];
         temp_porenzahlen = boden['Oedo-CRL'][einzelversuch]['Porenzahl [-]'];
         temp_laststufen = boden['Oedo-CRL'][einzelversuch]['Laststufen [kN/m^2]'];
      except:
         continue;
      #
      stunden_crl += [temp_stunden];
      porenzahlen_crl += [temp_porenzahlen];
      laststufen_crl += [temp_laststufen];
   #
   if (len(stunden_crl) < 2):
      print('# Warnung: Weniger als zwei Laststufen mit Oedo-CRL');
      return [];
   #
   parameter = ViskohypoplastischeParameterBestimmen(spannungen_crs=spannungen_crs,
      porenzahlen_crs=porenzahlen_crs, hoehe_crs=hoehe_crs, stauchungsrate_crs=stauchungsrate_crs,
      reibungswinkel_krit=reibungswinkel_krit, stunden_crl=stunden_crl,
      porenzahlen_crl=porenzahlen_crl, laststufen_crl=laststufen_crl,
      intervallgroesse=intervallgroesse, p1logverhaeltnis=p1logverhaeltnis,
      p5logverhaeltnis=p5logverhaeltnis, zwischenpunkte=zwischenpunkte);
   #
   if (parameter != []):
      auswertung = GespeicherterWertOderUebergabe(daten=boden['Oedo-CRS-Visko'],
         bezeichnung='Parameter-miniSoilLAB', uebergabe=Datenstruktur());
      auswertung.update([('Parameter', parameter)]);
      auswertung.update([('Parameter-Hilfen', ['e100 [-]', 'lambda [-]', 'kappa [-]', 'beta_x [-]', 'I_v [-]', 'D_r [-]', 'OCR [-]'])]);
      #
      einstellungen = GespeicherterWertOderUebergabe(daten=auswertung,
         bezeichnung='Einstellungen', uebergabe=Datenstruktur());
      einstellungen.update([('Intervallgroesse', intervallgroesse)]);
      einstellungen.update([('P1 Logverhaeltnis', p1logverhaeltnis)]);
      einstellungen.update([('P5 Logverhaeltnis', p5logverhaeltnis)]);
      einstellungen.update([('Zwischenpunkte', zwischenpunkte)]);
   #
   return parameter;
#


# -------------------------------------------------------------------------------------------------
def _ViskohypoplastischTangentenpunkte(zeit, spez_setzung, log_zu_sqrt=[1, 1], zwischenpunkte=5,
   glaettungswert=10, linearbereich=0.1):
   """Schaetzt die 100%-Setzung aus zwei Verfahren aus den uebergebenen zeit und spez_setzung-Daten
   eines Oedometerversuchs mit konstanten Lasten (Oedo-CRL) ab. Dazu werden in beiden Verfahren
   jeweils zwei Punkte bestimmt und deren Koordinaten zurueckgegeben. Im logarithmischen
   Zeit-Setzungs-Diagramm wird der Wendepunkt und der Schnittpunkt zwischen der Tangente am
   Wendepunkt und Tangente am Endpunkt (100%-Setzung) ermittelt. Im Zeit-Setzungs-Diagramm im
   Wurzelmassstab werden der Schnittpunkt der 90%-Setzung mit der 100%-Setzungslinie und die
   abgeschaetzte 100%-Setzung (auf der Linie selbst) ermittelt. Anschliessend wird ein mit Hilfe von
   log_zu_sqrt bestimmter Mittelwert zwischen den beiden 100%-Setzungsabschaetzungen bestimmt und
   der dazugehoerige Punkt auf der Linie fuer diesen Wert (m100) und den Punkt fuer 90% davon (m90)
   berechnet. Gibt den Vektor
   [logschnittpunkt, logwendepunkt, sqrt100punkt, sqrt90punkt, m100, m90] zurueck.
   """
   from math import log10, sqrt
   from .gleichungsloeser import Spline2DInterpolation, AbleitungDyNachDx, GlaettungFunktionswerte
   from .gleichungsloeser import LinearInterpoliertenIndexUndFaktor#, QuadratischesAusgleichsproblem
   from .gleichungsloeser import SortierenUndDoppelteXEintraegeEntfernen
   #
   sortzeit, sortsetzung = SortierenUndDoppelteXEintraegeEntfernen(x=zeit, y=spez_setzung);
   for idx in range(len(sortsetzung)-1):
      if (sortsetzung[idx+1] < sortsetzung[idx]):
         # FIXME: Daten ab Minimum abschneiden?
         print('# Warnung: Setzung des Oedo-CRL Versuchs nimmt ab statt zu');
         return [None, None, None, None, None, None];
   #
   # --- Variante log ---
   # In lineare Koordinaten umwandeln und alle Operationen dann erst durchfuehren
   #
   # Da Logarithmus von 0 zu einem Fehler fuehrt, wird der erste Wert davon ignoriert.
   # Fuer die Wurzelvariante ist das optional, aber aufgrund der Einheitlichkeit wird das auch dort
   # angewandt.
   xlogzeit = [log10(x) for x in sortzeit[1:]];
   ylogsetz = sortsetzung[1:];
   xlog, ylog = Spline2DInterpolation(xwerte=[xlogzeit[0]] + xlogzeit,
      ywerte=[ylogsetz[0]] + ylogsetz, zwischenpunkte=zwischenpunkte, tangentenfaktor=1.0);
   xabllog, yabllog = AbleitungDyNachDx(x=xlog, y=ylog);
   #
   xabllogglatt = GlaettungFunktionswerte(werte=xabllog, glaettungsbereich=glaettungswert);
   yabllogglatt = GlaettungFunktionswerte(werte=yabllog, glaettungsbereich=glaettungswert);
   #
   idxmaxglatt = yabllogglatt.index(max(yabllogglatt));
   idxmax, fakmax = LinearInterpoliertenIndexUndFaktor(vergleichswert=xabllogglatt[idxmaxglatt], vergleichswertliste=xlog);
   #
   x_wende = xlog[idxmax];
   y_wende = ylog[idxmax];
   yabllog_wende = yabllog[idxmax];
   xlog100 = (100.0-y_wende)/yabllog_wende + x_wende;
   xlog0 = -y_wende/yabllog[idxmax] + x_wende;
   #
   # FIXME: Minimalwert noch zusaetzlich pruefen, nicht dass ein Ausreisser verwendet wird
   yabllog_ende = min(yabllog[-15:]);
   x_ende = xlog[-1];
   y_ende = ylog[-1];
   xlogp = xlog[int(0.5*len(xlog))];
   ylogp = yabllog_ende*(xlogp-x_ende) + y_ende;
   #
   # Aus Tangente am Umkehrpunkt und Tangente am Endpunkt den gemeinsamen Schnittpunkt bestimmen
   t = ((x_wende-x_ende)*yabllog_ende - (y_wende-y_ende))/(yabllog_wende - yabllog_ende);
   x_schnitt = x_wende + t;
   y_schnitt = y_wende + t*yabllog_wende;
   #
   ## Bestimmung der Sofortsetzung
   #idxa, faka = LinearInterpoliertenIndexUndFaktor(vergleichswert=-1.5, vergleichswertliste=xlog);
   #a, b, c = QuadratischesAusgleichsproblem(x=xlog[:idxa], y=ylog[:idxa]);
   #x_offset = -b/(2.0*a);
   #setzung_0 = c - b*b/(4.0*a);
   #
   logschnittpunkt = [10**x_schnitt, y_schnitt];
   logwendepunkt = [10**x_wende, y_wende];
   #
   # --- Variante sqrt ---
   xsqrtzeit = [sqrt(x) for x in sortzeit[1:]];
   ysqrtsetz = sortsetzung[1:];
   xsqrt, ysqrt = Spline2DInterpolation(xwerte=[xsqrtzeit[0]] + xsqrtzeit, ywerte=[ysqrtsetz[0]] + ysqrtsetz,
      zwischenpunkte=zwischenpunkte, tangentenfaktor=1.0);
   #
   idxende, fakende = LinearInterpoliertenIndexUndFaktor(vergleichswert=sqrt(linearbereich),
      vergleichswertliste=xsqrt);
   if (idxende is None):
      print('# Warnung: Zu wenig/ungueltige x-Werte');
      return [None, None, None, None, None, None];
   #
   idxende += 1;
   #
   xablsqrt, yablsqrt = AbleitungDyNachDx(x=xsqrt[:idxende], y=ysqrt[:idxende]);
   yablsqrt_start = sum(yablsqrt)/len(yablsqrt);
   #
   xsqrt0 = (100.0 - ysqrt[0])/yablsqrt_start + xsqrt[0];
   xsqrt90 = 1.15*xsqrt0;
   idx90, fak90 = LinearInterpoliertenIndexUndFaktor(vergleichswert=xsqrt90, vergleichswertliste=xsqrt);
   ysqrt90 = ysqrt[idx90] + fak90*(ysqrt[idx90+1] - ysqrt[idx90]);
   ysqrt100 = ysqrt[0] + (ysqrt90-ysqrt[0])/0.9;
   if (ysqrt100 > ysqrt[-1]):
      print('# Warnung: y100 kann nicht genau bestimmt werden');
      ysqrt100 = ysqrt[-1];
   #
   idx100, fak100 = LinearInterpoliertenIndexUndFaktor(vergleichswert=ysqrt100, vergleichswertliste=ysqrt);
   xsqrt100 = xsqrt[idx100] + fak100*(xsqrt[idx100+1] - xsqrt[idx100]);
   sqrt100punkt = [xsqrt100**2, ysqrt100];
   sqrt90punkt = [xsqrt90**2, ysqrt90];
   #
   # --- Mittelpunkt ---
   y_m100 = (log_zu_sqrt[0]*logschnittpunkt[1] + log_zu_sqrt[1]*sqrt100punkt[1])/sum(log_zu_sqrt);
   idxm, fakm = LinearInterpoliertenIndexUndFaktor(vergleichswert=y_m100, vergleichswertliste=ysqrt);
   xsqrtm100 = xsqrt[idxm] + fakm * (xsqrt[idxm+1] - xsqrt[idxm]);
   y_m90 = ysqrt[0] + 0.9*(y_m100-ysqrt[0]);
   idxm90, fakm90 = LinearInterpoliertenIndexUndFaktor(vergleichswert=y_m90, vergleichswertliste=ysqrt);
   xsqrtm90 = xsqrt[idxm90] + fakm90 * (xsqrt[idxm90+1] - xsqrt[idxm90]);
   m100 = [xsqrtm100**2, y_m100];
   m90 = [xsqrtm90**2, y_m90];
   #
   return [logschnittpunkt, logwendepunkt, sqrt100punkt, sqrt90punkt, m100, m90];
#


# -------------------------------------------------------------------------------------------------
def _ViskohypoplastischCalphaUndIv(zeit, porenzahl, laststufen=[1, 10], reibungswinkel=False,
   zwischenpunkte=5, einflussbereich_ca=0.25):
   """Berechnet aus der uebergebenen zeit (in Stunden) und porenzahl eines CRL-Oedometerversuchs
   den Kriechbeiwert c_alpha und (wenn reibungswinkel nicht False sondern ein Wert in Grad ist)
   den Viskositaetsindex I_v. Fuer die Berechnung von I_v werden auch die beiden laststufen
   [sigma_start, sigma_ende] benoetigt. Mit zwischenpunkte kann gesteuert werden, wie fein zwischen
   den Punkten mit einer Spline interpoliert werden soll. Gibt [c_alpha, I_v] zurueck.
   
   Fuer die Berechnung von c_alpha wird die mittlere Steigung in einem Bereich der Groesse
   einflussbereich_ca am Ende der logarithmierten zeit betrachtet.
   """
   from math import sin, log10
   from .konstanten import grad2rad
   from .gleichungsloeser import LinearInterpoliertenIndexUndFaktor
   from .gleichungsloeser import SortierenUndDoppelteXEintraegeEntfernen
   #
   sortzeit, sortporenzahl = SortierenUndDoppelteXEintraegeEntfernen(x=zeit, y=porenzahl);
   xlogzeit = [log10(x) for x in sortzeit[1:]];
   ypor = sortporenzahl[1:];
   #
   grenzwert = xlogzeit[0] + (1.0-einflussbereich_ca)*(xlogzeit[-1]-xlogzeit[0]);
   idx_davor, faktor = LinearInterpoliertenIndexUndFaktor(vergleichswert=grenzwert, vergleichswertliste=xlogzeit);
   xwerte = [xlogzeit[idx_davor] + faktor*(xlogzeit[idx_davor+1]-xlogzeit[idx_davor])] + xlogzeit[idx_davor+1:];
   ywerte = [ypor[idx_davor] + faktor*(ypor[idx_davor+1]-ypor[idx_davor])] + ypor[idx_davor+1:];
   #
   gesamtsteigung = (ywerte[-1]-ywerte[0])/(xwerte[-1]-xwerte[0]);
   if (gesamtsteigung >= 0.0):
      print('# Warnung: Gesamtsteigung im Einflussbereich bei Bestimmung von c_alpha ungueltig (>= Null)');
      c_alpha = 0.0;
   else:
      xmittel = 0;
      ymittel = 0;
      # Nur Anteile beruecksichtigen, deren Steigung groesser als gesamtsteigung und kleiner als Null sind.
      for idx in range(len(xwerte)-1):
         xdiff = xwerte[idx+1]-xwerte[idx];
         ydiff = ywerte[idx+1]-ywerte[idx];
         steigung = ydiff/xdiff;
         if ((steigung < 0.0) and (steigung >= gesamtsteigung)):
            xmittel += xdiff;
            ymittel += ydiff;
      #
      if (xmittel == 0.0):
         print('# Warnung: c_alpha ungueltig (setze auf Null)');
         c_alpha = 0.0;
      else:
         c_alpha = ymittel/xmittel;
   #
   if (not reibungswinkel):
      I_v = None;
   else:
      phi_c = reibungswinkel*grad2rad;
      mittelspannungen = [(1.0 + 2.0*(1.0 - sin(phi_c))) * einzellast/3.0 for einzellast in laststufen];
      C_cC = (porenzahl[-1] - porenzahl[0]) / (log10(mittelspannungen[0]) - log10(mittelspannungen[-1]));
      I_v = c_alpha/C_cC;
   #
   return [c_alpha, I_v];
#


# -------------------------------------------------------------------------------------------------
def _ViskohypoplastischCRSPunkte(spannungen, intervallgroesse, p1logverhaeltnis, p5logverhaeltnis):
   """Ermittle aus den uebergebenen spannungen eines Oedo-CRS-Versuchs (Oedometerversuch mit
   konstanter Dehnungsrate) charakteristische Punkte auf den drei Belastungsabschnitten
   (Erstbelastung, Entlastung, Wiederbelastung). Zum Erkennen der beiden Umkehrpunkte zwischen den
   Belastungsabschnitten wird ein lokales Extremum in einem Bereich intervallgroesse ermittelt.
   Die charakteristischen Punkte sind: Start (0), auf Erstbelastungsast (1), Umkehrpunkt
   Entlastung (2), Umkehrpunkt Wiederbelastung (3), Punkt auf Wiederbelastungsast bei Spannung des
   ersten Umkehrpunkts (4), auf Wiederbelastungsast (5), Ende (6).
   Fuer Punkt Punkt 1 und Punkt 5 kann mit p1logverhaeltnis und p5logverhaeltnis gewaehlt werden,
   wo sich der Punkt geometrisch zwischen dem vorangegangenem und nachfolgendem Punkt befindet
   (Der Zahlenwert (0-1) wird in den Anteil des logarithmischen Abstands umgerechnet).
   Gibt eine Liste der Indizes zurueck.
   """
   from math import log10
   from .konstanten import debugmodus
   from .gleichungsloeser import LokalerExtremwert, LinearInterpoliertenIndexUndFaktor
   #
   idxmaxliste = LokalerExtremwert(werte=spannungen, intervall=intervallgroesse, maximum=True);
   idxminliste = LokalerExtremwert(werte=spannungen, intervall=intervallgroesse, maximum=False);
   if (debugmodus):
      print('# Debug: Indizes lokaler Maxima: ' + ', '.join([str(x) for x in idxmaxliste]));
      print('#        Indizes lokaler Minima: ' + ', '.join([str(x) for x in idxminliste]));
   #
   if (len(idxmaxliste) != 2):
      print('# Warnung: Lokales Maximum beim Oedo-CRS konnte nicht gefunden werden');
      return [];
   #
   if (len(idxminliste) != 2):
      print('# Warnung: Lokales Minimum beim Oedo-CRS konnte nicht gefunden werden');
      return [];
   #
   idx0 = 0;
   idx2 = idxmaxliste[0];
   idx3 = idxminliste[1];
   idx6 = len(spannungen)-1;
   #
   spg1 = 10**(log10(spannungen[idx0])+p1logverhaeltnis*(log10(spannungen[idx2])-log10(spannungen[idx0])));
   idx1, fak1 = LinearInterpoliertenIndexUndFaktor(vergleichswert=spg1, vergleichswertliste=spannungen[:idx2]);
   idx1 += 1;
   idx4, fak4 = LinearInterpoliertenIndexUndFaktor(vergleichswert=spannungen[idx2], vergleichswertliste=spannungen[idx3:]);
   idx4 += idx3 + 1;
   spg5 = 10**(log10(spannungen[idx4])+p5logverhaeltnis*(log10(spannungen[idx6])-log10(spannungen[idx4])));
   idx5, fak5 = LinearInterpoliertenIndexUndFaktor(vergleichswert=spg5, vergleichswertliste=spannungen[idx4:]);
   idx5 += idx4 + 1;
   return [idx0, idx1, idx2, idx3, idx4, idx5, idx6];
#



# -------------------------------------------------------------------------------------------------
def ViskohypoplastischeParameterBestimmen(spannungen_crs, porenzahlen_crs, hoehe_crs,
   stauchungsrate_crs, reibungswinkel_krit, stunden_crl, porenzahlen_crl, laststufen_crl,
   intervallgroesse=25, p1logverhaeltnis=0.5, p5logverhaeltnis=0.5, zwischenpunkte=5):
   """Bestimme die viskohypoplastischen Parameter aus den uebergebenen Parametern verschiedener
   Laborversuche. Es werden benoetigt:
   
   - spannungen_crs (aus einem CRS-Oedometerversuch mit Belastung, Entlastung und Wiederbelastung)
   - porenzahlen_crs (aus einem CRS-Oedometerversuch mit Belastung, Entlastung und Wiederbelastung)
   - hoehe_crs (Anfangsprobenhoehe aus einem CRS-Oedometerversuch)
   - stauchungsrate_crs (aus einem CRS-Oedometerversuch)
   - [stunden_crl] (min. zwei Zeitverlaeufe (in [h]) aus CRL-Oedometerversuchen)
   - [porenzahlen_crl] (min. zwei Porenzahlentwicklungen aus CRL-Oedometerversuchen)
   - [laststufen_crl] (min. zwei Laststufenpaare [last_start, last_ende] aus CRL-Oedometerversuchen)
   - reibungswinkel_krit (aus einem undraiierten Triaxialversuch (Triax-CU))

   Optional kann mit intervallgroesse der Bereich zum Erkennen lokaler Extrema in den Daten des
   CRS-Oedometerversuchs angepasst werden. Fuer die Bestimmung der charakteristischen Punkte kann
   ausserdem p1logverhaeltnis und p5logverhaeltnis (beide im Intervall [0-1]) angepasst werden.
   Fuer die Bestimmung von I_v wird zur Ermittlung der Tangentenpunkte noch mit zusaetzlichen Werten
   interpoliert, was mit zwischenpunkte eingestellt werden kann.
   Gibt die viskohypoplastischen Parameter fuer diese Labordaten zurueck.
   [e100,  lambda,  kappa,  beta_x,  I_v,  D_r,  OCR]
    [-]    [-]      [-]     [-]      [-]   [-]   [-]
   """
   from math import sqrt, sin, log
   from .konstanten import grad2rad, debugmodus
   #
   # FIXME: Rueckgabewerte und Nenner (Teilung durch Null) pruefen!
   # I_v aus den Daten der CRL-Oedometerversuche bestimmen
   I_v = [];
   for idx in range(len(stunden_crl)):
      if (idx < len(stunden_crl)/2.0):
         continue;
      #
      temp_c_alpha, temp_I_v = _ViskohypoplastischCalphaUndIv(zeit=stunden_crl[idx],
         porenzahl=porenzahlen_crl[idx], laststufen=laststufen_crl[idx],
         reibungswinkel=reibungswinkel_krit, zwischenpunkte=zwischenpunkte);
      if (temp_I_v is not None):
         I_v += [temp_I_v];
   #
   if (I_v == []):
      return [];
   #
   if (debugmodus):
      print('# Debug: Zwischenwerte bei der Berechnung der viskohypoplastischen Parameter');
      print('   I_v-Werte: ' + ', '.join([str(round(x*1e4)/1e4) for x in I_v]));
   #
   I_v = sum(I_v)/len(I_v);
   #
   # Die restlichen Parameter aus den Daten der CRS-Oedometerversuche und Triax-CU bestimmen
   idxliste = _ViskohypoplastischCRSPunkte(spannungen=spannungen_crs, intervallgroesse=intervallgroesse,
      p1logverhaeltnis=p1logverhaeltnis, p5logverhaeltnis=p5logverhaeltnis);
   if (idxliste == []):
      return [];
   #
   punktspannung = [spannungen_crs[idx] for idx in idxliste];
   punktporenzahl = [porenzahlen_crs[idx] for idx in idxliste];
   #
   if (debugmodus):
      print('   Ref-Spannungen: ' + 'kPa, '.join([str(round(x*10)/10) for x in punktspannung]) + 'kPa');
      print('   Ref-Porenzahlen: ' + ', '.join([str(round(x*1e3)/1e3) for x in punktporenzahl]));
   #
   # lambda nicht als Name verwenden - Konflikte mit der internen lambda-Funktionalitaet
   lambd = log((1.0 + punktporenzahl[5])/(1.0 + punktporenzahl[6]))/log(punktspannung[6]/punktspannung[5]);
   kappa_0 = log((1.0 + punktporenzahl[3])/(1.0 + punktporenzahl[4]))/log(punktspannung[4]/punktspannung[3]);
   phi_c = reibungswinkel_krit*grad2rad;
   a = sqrt(3.0)*(3.0-sin(phi_c)) / (sqrt(8.0)*sin(phi_c));
   K_0 = (-2.0 -a**2 + sqrt(36.0 + 36.0*a**2 + a**4))/16.0;
   kappa = (1.0 + a**2/(1.0 + 2.0*K_0)) * kappa_0/(1.0 + a**2/3.0);
   #
   if (debugmodus):
      print('   lambda=' + str(round(lambd*1e4)/1e4) + ', kappa_0=' + str(round(kappa_0*1e4)/1e4) \
         + ', a=' + str(round(a*1e3)/1e3) + ', K_0=' + str(round(K_0*1e3)/1e3) + ', kappa=' \
         + str(round(kappa*1e4)/1e4));
   #
   mittelspannung1 = punktspannung[1]/3.0 * (1.0 + 2.0*K_0);
   mittelspannung6 = punktspannung[6]/3.0 * (1.0 + 2.0*K_0);
   #
   eps = log((1.0 + punktporenzahl[2])/(1.0 + punktporenzahl[0]));
   D11 = eps/((punktporenzahl[0] - punktporenzahl[2]) / (1.0 + punktporenzahl[0]) * hoehe_crs/(stauchungsrate_crs/60.0));
   #
   # FIXME: Verhaeltnis Dehnung zu Referenzdehnung (woher?)
   # Zur Bestimmung/Abschaetzung fuer OCR=1 siehe auch Karcher S. 14f
   d11_dr = 1.035;
   D_r = -D11/d11_dr;
   #
   if (debugmodus):
      print('   eps=' + str(round(eps*1e4)/1e4) + ', D_11=' + str(round(D11*1e9)/1e9) + ', D_r=' \
         + str(round(D_r*1e9)/1e9));
   #
   # FIXME: Form der Belastungsflaeche (woher?) Nachrechnung von undrainierten Schertests?!
   beta_x = 0.95;
   #
   steigung_m = 6.0*sin(phi_c)/(3.0 - sin(phi_c));
   eta = punktspannung[6] * (1.0 - K_0)/mittelspannung6/steigung_m;
   #
   zwischenwert_bet = (beta_x * sqrt(1.0 + eta**2 * (beta_x**2 - 1.0)) - 1.0)/(beta_x - 1.0);
   e100 = (1.0 + punktporenzahl[6]) * (mittelspannung6 * zwischenwert_bet/100.0)**lambd - 1.0;
   #
   if (debugmodus):
      print('   beta_x=' + str(round(beta_x*1e3)/1e3) + ', steigung_m=' \
         + str(round(steigung_m*1e3)/1e3) + ', eta=' + str(round(eta*1e3)/1e3) + ', e_100=' \
         + str(round(e100*1e3)/1e3));
   #
   pep = mittelspannung1 * zwischenwert_bet;
   pe = mittelspannung6 * ((1.0 + punktporenzahl[6]) / (1.0 + punktporenzahl[1]))**(1.0/lambd);
   OCR = pe/pep;
   #
   if (debugmodus):
      print('   pe+=' + str(round(pep*1e3)/1e3) + ', pe=' + str(round(pe*1e3)/1e3) + ', OCR=' \
         + str(round(OCR*1e2)/1e2));
   #
   return [e100, lambd, kappa, beta_x, I_v, D_r, OCR];
#
