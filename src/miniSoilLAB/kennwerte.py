# -*- coding: utf-8 -*-
"""
kennwerte.py   v0.2 (2019-12)
"""

# Copyright 2020-2021 Dominik Zobel.
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
def Kennwertberechnungen(daten, vorlage):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der uebergebenen vorlage und
   speichere sie in der uebergebenen Struktur daten, sofern diese den gueltigen Vorgaben entspricht.
   """
   from .konstanten import gueltige_vorlagen
   #
   if (vorlage not in gueltige_vorlagen):
      print('# Warnung: Ungueltige Vorlage');
      return False;
   #
   if (vorlage == 'Atterberg'):
      status = _KennwerteAtterberg(daten=daten);
   elif (vorlage == 'LoDi'):
      status = _KennwerteLodi(daten=daten);
   elif (vorlage == 'Auswertung-Hypoplastisch'):
      status = _KennwerteHypo(daten=daten);
   elif (vorlage == 'Oedo'):
      status = _KennwerteOedo(daten=daten);
   elif (vorlage == 'Oedo-CRL'):
      status = _KennwerteOedoCrl(daten=daten);
   elif (vorlage == 'Oedo-CRS'):
      status = _KennwerteOedoCrs(daten=daten);
   elif (vorlage == 'Oedo-CRS-Visko'):
      status = _KennwerteOedoCrsvisko(daten=daten);
   elif ((vorlage == 'Triax-CU') or (vorlage == 'Triax-D')):
      status = _KennwerteTriax(daten=daten);
   elif (vorlage == 'Triax-p-q'):
      status = _KennwerteTriaxpq(daten=daten);
   else:
      print('# Hinweis: Vorlage nicht gefunden');
      status = False;
   #
   return status;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteAtterberg(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Atterberg und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   from math import log10
   #
   try:
      fliess = daten['Daten-Fliessgrenze'];
      ausroll = daten['Daten-Ausrollgrenze'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
      return False;
   #
   try:
      wassergehalt = daten['Wassergehalt [%]'];
      ueberkornanteil = daten['Ueberkornanteil [%]'];
      schlaege = daten['Daten-Fliessgrenze']['Schlaege-Anzahl [-]'];
      massefeucht_f = daten['Daten-Fliessgrenze']['Feuchtmasse mit Behaelter [g]'];
      massetrocken_f = daten['Daten-Fliessgrenze']['Trockenmasse mit Behaelter [g]'];
      massebehaelter_f = daten['Daten-Fliessgrenze']['Behaeltermasse [g]'];
      massefeucht_a = daten['Daten-Ausrollgrenze']['Feuchtmasse mit Behaelter [g]'];
      massetrocken_a = daten['Daten-Ausrollgrenze']['Trockenmasse mit Behaelter [g]'];
      massebehaelter_a = daten['Daten-Ausrollgrenze']['Behaeltermasse [g]'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   # ----------------------- Fliessgrenze -----------------------
   if (any([(abs(massetrocken_f[idx]-massebehaelter_f[idx]) < tol) for idx in range(len(massefeucht_f))])):
      print('# Warnung: Behaeltermasse und Trockenmasse fuer Fliessgrenze fast identisch');
      return False;
   #
   wassergehalt_f = [100.0*(massefeucht_f[idx]-massetrocken_f[idx])/(massetrocken_f[idx]-massebehaelter_f[idx]) for idx in range(len(massefeucht_f))];
   fliess.update([('Wassergehalt [%]', wassergehalt_f)]);
   #
   if (any([(schlag < tol) for schlag in schlaege])):
      print('# Warnung: Schlaganzahl muss eine ganze Zahl groesser als Null sein');
      return False;
   #
   logschlaege = [log10(schlag) for schlag in schlaege];
   sumlog2schlaege = sum([schlag**2 for schlag in logschlaege]);
   sumlogschlaegewasser = sum([logschlaege[idx]*wassergehalt_f[idx] for idx in range(len(logschlaege))]);
   A_wert = ((len(schlaege)*sumlogschlaegewasser)-(sum(logschlaege)*sum(wassergehalt_f))) / ((len(schlaege)*sumlog2schlaege)-(sum(logschlaege)**2));
   B_wert = (sum(wassergehalt_f)-(A_wert*sum(logschlaege)))/len(logschlaege);
   #
   fliess.update([('A-Wert [-]', A_wert)]);
   fliess.update([('B-Wert [-]', B_wert)]);
   #
   if ((schlaege[0] == schlaege[1]) and (schlaege[1] == schlaege[2])):
      # Einpunktmethode nach DIN 18122-1 Gleichung 5 und Anmerkungen
      wassergehalt_mittel = sum(wassergehalt_f)/len/(wassergehalt_f);
      einpunktexp = 0.112;
      if (wassergehalt_mittel < 40.0):
         einpunktexp = 0.14;
      #
      if (wassergehalt_mittel > 60.0):
         einpunktexp = 0.1;
      #
      fliess.update([('Exponent-Einpunktmethode [-]', einpunktexp)]);
      # Nur die ersten drei Werte beruecksichtigen
      fliessgrenze = sum(wassergehalt_f[:3])/3.0 * (schlaege[0]/25.0)**einpunktexp;
   else:
      fliessgrenze = B_wert + log10(25)*A_wert;
   #
   daten.update([('Fliessgrenze [%]', fliessgrenze)]);
   #
   # ---------------------- Ausrollgrenze -----------------------
   if (any([(abs(massetrocken_a[idx]-massebehaelter_a[idx]) < tol) for idx in range(len(massefeucht_a))])):
      print('# Warnung: Behaeltermasse und Trockenmasse fuer Ausrollgrenze fast identisch');
      return False;
   #
   wassergehalt_a = [100.0*(massefeucht_a[idx]-massetrocken_a[idx])/(massetrocken_a[idx]-massebehaelter_a[idx]) for idx in range(len(massefeucht_a))];
   ausroll.update([('Wassergehalt [%]', wassergehalt_a)]);
   ausrollgrenze = sum(wassergehalt_a)/len(wassergehalt_a);
   daten.update([('Ausrollgrenze [%]', ausrollgrenze)]);
   #
   if (abs(100.0 - ueberkornanteil) < tol):
      print('# Warnung: Ueberkornanteil annaehernd 100%');
      return False;
   #
   plastizitaetszahl = fliessgrenze - ausrollgrenze;
   if (abs(plastizitaetszahl) < tol):
      print('# Warnung: Plastizitaetszahl annaehernd Null');
      return False;
   #
   wassergehalt_korr = 100.0*wassergehalt/(100.0 - ueberkornanteil);
   konsistenzzahl = (fliessgrenze - wassergehalt_korr)/plastizitaetszahl;
   daten.update([('Plastizitaetszahl [%]', plastizitaetszahl)]);
   daten.update([('Konsistenzzahl [-]', konsistenzzahl)]);
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteHypo(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage
   Auswertung-Hypoplastisch und speichere sie in der uebergebenen Struktur daten, sofern diese
   den Vorgaben entspricht.
   """
   from .konstanten import pi
   #
   try:
      schuettkegel = daten['Schuettkegel'];
      oedo_locker = daten['Oedo-locker'];
      oedo_dicht = daten['Oedo-dicht'];
      triax = daten['Triax-D'];
      parameter = daten['Parameter'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
      return False;
   #
   try:
      korndichte = schuettkegel['Korndichte [g/cm^3]'];
      e_max = schuettkegel['Porenzahl-max [-]'];
      e_min = schuettkegel['Porenzahl-min [-]'];
      #
      masse_oedo_l = oedo_locker['Masse [g]'];
      if ('Hoehe [cm]' in oedo_locker):
         oedo_locker.update([('Hoehe [mm]', 10.0*oedo_locker['Hoehe [cm]'])]);
         del oedo_locker['Hoehe [cm]'];
      #
      hoehe_oedo_l = oedo_locker['Hoehe [mm]'];
      #
      if ('Durchmesser [cm]' in oedo_locker):
         oedo_locker.update([('Durchmesser [mm]', 10.0*oedo_locker['Durchmesser [cm]'])]);
         del oedo_locker['Durchmesser [cm]'];
      #
      durchmesser_oedo_l = oedo_locker['Durchmesser [mm]'];
      setzung_oedo_l = oedo_locker['Setzung [mm]'];
      #
      masse_oedo_d = oedo_dicht['Masse [g]'];
      #
      if ('Hoehe [cm]' in oedo_dicht):
         oedo_dicht.update([('Hoehe [mm]', 10.0*oedo_dicht['Hoehe [cm]'])]);
         del oedo_dicht['Hoehe [cm]'];
      #
      hoehe_oedo_d = oedo_dicht['Hoehe [mm]'];
      #
      if ('Durchmesser [cm]' in oedo_dicht):
         oedo_dicht.update([('Durchmesser [mm]', 10.0*oedo_dicht['Durchmesser [cm]'])]);
         del oedo_dicht['Durchmesser [cm]'];
      #
      durchmesser_oedo_d = oedo_dicht['Durchmesser [mm]'];
      setzung_oedo_d = oedo_dicht['Setzung [mm]'];
      #
      e_peak = triax['Porenzahl-Peak [-]'];
      #
      # Erforderliche Werte zur Bestimmung der hypoplastischen Parameter, deren Existenz hier
      # ueberprueft wird
      testwert = schuettkegel['Reibungswinkel-krit [Grad]'];
      testwert = oedo_locker['Spannung [kN/m^2]'];
      testwert = oedo_dicht['Spannung [kN/m^2]'];
      testwert = triax['Reibungswinkel-Peak-locker [Grad]'];
      testwert = triax['Reibungswinkel-Peak-dicht [Grad]'];
      testwert = triax['Dilatanzwinkel [Grad]'];
      testwert = triax['Spannung-Peak-eff [kN/m^2]'];
      testwert = triax['Porenzahl-Peak [-]'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   # ---------------------- Oedo-locker ----------------------
   if (any([(abs(einzelvar - hoehe_oedo_l) < tol) for einzelvar in setzung_oedo_l])):
      print('# Warnung: Setzung des lockeren Oedometers annaehernd Probenhoehe');
      return False;
   #
   if (abs(masse_oedo_l) < tol):
      print('# Warnung: Masse des lockeren Oedometers annaehernd Null');
      return False;
   #
   if (abs(durchmesser_oedo_l) < tol):
      print('# Warnung: Durchmesser des lockeren Oedometers annaehernd Null');
      return False;
   #
   porenzahlen = [korndichte/(masse_oedo_l /((hoehe_oedo_l - aktuelle_setzung)/10.0 \
               *pi*(durchmesser_oedo_l/20.0)**2)) - 1.0 for aktuelle_setzung in setzung_oedo_l];
   oedo_locker.update([('Porenzahl [-]', porenzahlen)]);
   #
   # ---------------------- Oedo-dicht -----------------------
   if (any([(abs(einzelvar - hoehe_oedo_d) < tol) for einzelvar in setzung_oedo_d])):
      print('# Warnung: Setzung des dichten Oedometers annaehernd Probenhoehe');
      return False;
   #
   if (abs(masse_oedo_l) < tol):
      print('# Warnung: Masse des dichten Oedometers annaehernd Null');
      return False;
   #
   if (abs(durchmesser_oedo_d) < tol):
      print('# Warnung: Durchmesser des dichten Oedometers annaehernd Null');
      return False;
   #
   porenzahlen = [korndichte/(masse_oedo_d /((hoehe_oedo_d - aktuelle_setzung)/10.0 \
               *pi*(durchmesser_oedo_d/20.0)**2))-1.0 for aktuelle_setzung in setzung_oedo_d];
   oedo_dicht.update([('Porenzahl [-]', porenzahlen)]);
   #
   # ----------------------- Triax-D ------------------------
   if (abs(e_max - e_min) < tol):
      print('# Warnung: Differenz zwischen max. und min. Porenzahl annaehernd Null');
      return False;
   #
   bez_lagerungsdichte = (e_max - e_peak)/(e_max - e_min);
   triax.update([('Lagerungsdichte-bez [-]', bez_lagerungsdichte)]);
   #
   # ----------------------- Parameter -----------------------
   parameter.update([('Parameter-Hilfe', ['phi_c [Grad]', 'h_s [MPa]', 'n [-]', 'e_d [-]',
      'e_c [-]', 'e_i [-]', 'alpha [-]', 'beta [-]'])]);
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteLodi(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Lodi und speichere
   sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   try:
      lo_lagerung = daten['Lockerste-Lagerung'];
      di_lagerung = daten['Dichteste-Lagerung'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
      return False;
   #
   try:
      korndichte = daten['Korndichte [g/cm^3]'];
      zylindervolumen_lo = lo_lagerung['Zylindervolumen [cm^3]'];
      if ('Probenmasse [g]' in lo_lagerung):
         masse_lo = lo_lagerung['Probenmasse [g]'];
         if (isinstance(masse_lo, list)):
            masse_lo = sum(masse_lo)/len(masse_lo);
      else:
         temp_masse1 = lo_lagerung['Probenmasse-1 [g]'];
         temp_masse2 = lo_lagerung['Probenmasse-2 [g]'];
         masse_lo = (temp_masse1 + temp_masse2)/2.0;
      #
      zylinderflaeche_di = di_lagerung['Zylindergrundflaeche [cm^2]'];
      zylinderhoehe_di = di_lagerung['Zylinderhoehe [cm]'];
      plattenhoehe = di_lagerung['Plattenhoehe [cm]'];
      if ('Probenmasse [g]' in di_lagerung):
         masse_di = di_lagerung['Probenmasse [g]'];
      else:
         if (('Probenmasse-1 [g]' in di_lagerung) and ('Probenmasse-2 [g]' in di_lagerung)):
            temp_masse1 = di_lagerung['Probenmasse-1 [g]'];
            temp_masse2 = di_lagerung['Probenmasse-2 [g]'];
            masse_di = (temp_masse1 + temp_masse2)/2.0;
         else:
            masse_di = masse_lo;
      #
      if ('Setzung [mm]' in di_lagerung):
         setzung = sum(di_lagerung['Setzung [mm]'])/len(di_lagerung['Setzung [mm]']);
      else:
         temp_setzung1 = di_lagerung['Setzung-1 [mm]'];
         temp_setzung2 = di_lagerung['Setzung-2 [mm]'];
         temp_setzung = [(s_lo + s_di)/2.0 for s_lo, s_di in zip(temp_setzung1, temp_setzung2)];
         setzung = sum(temp_setzung)/len(temp_setzung);
      #
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   except TypeError as errormessage:
      print('# Warnung: Berechnung fehlgeschlagen (ungueltige Werte) - ' + str(errormessage));
      return False;
   except:
      print('# Warnung: Berechnung fehlgeschlagen (ungueltige Werte fuer Massen oder Setzungen?)');
      return False;
   #
   tol = 1e-6;
   # Wenn die folgenden Eintraege fehlen ist das nicht kritisch, deshalb Platzhalter bereitstellen
   if ('Bodenname' not in daten):
      daten.update([('Bodenname', '--undef--')]);
   #
   if ('Bodenart' not in daten):
      daten.update([('Bodenart', '--undef--')]);
   #
   # -------------------- Lockerste Lagerung --------------------
   if (abs(zylindervolumen_lo) < tol):
      print('# Warnung: Zylindervolumen annaehernd Null');
      return False;
   #
   if (abs(korndichte) < tol):
      print('# Warnung: Korndichte annaehernd Null');
      return False;
   #
   if (abs(masse_lo) < tol):
      print('# Warnung: Masse (lo) annaehernd Null');
      return False;
   #
   min_trockendichte = masse_lo/zylindervolumen_lo;
   max_porenanteil = 1.0 - min_trockendichte/korndichte;
   max_porenzahl = korndichte/min_trockendichte - 1.0;
   #
   lo_lagerung.update([('Trockendichte-min [g/cm^3]', min_trockendichte)]);
   lo_lagerung.update([('Porenanteil-max [-]', max_porenanteil)]);
   lo_lagerung.update([('Porenzahl-max [-]', max_porenzahl)]);
   #
   # -------------------- Dichteste Lagerung --------------------
   if (abs(masse_di) < tol):
      print('# Warnung: Masse (di) annaehernd Null');
      return False;
   #
   min_vol = zylinderflaeche_di*(zylinderhoehe_di - plattenhoehe - setzung/10.0);
   if (abs(min_vol) < tol):
      print('# Warnung: Volumen (di) annaehernd Null');
      return False;
   #
   max_trockendichte = masse_di/min_vol;
   min_porenanteil = 1.0 - max_trockendichte/korndichte;
   min_porenzahl = korndichte/max_trockendichte - 1.0;
   #
   di_lagerung.update([('Trockendichte-max [g/cm^3]', max_trockendichte)]);
   di_lagerung.update([('Porenanteil-min [-]', min_porenanteil)]);
   di_lagerung.update([('Porenzahl-min [-]', min_porenzahl)]);
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteOedo(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo und speichere
   sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   from math import log
   from .datenstruktur import Datenstruktur
   from .konstanten import pi, g, oedo_gewichtsplatten, oedo_gewichte_kopfplatte, oedo_hebel
   from .gleichungsloeser import LoeseGleichung
   #
   try:
      korndichte = daten['Korndichte [g/cm^3]'];
      anfangshoehe = daten['Hoehe [mm]'];
      durchmesser = daten['Durchmesser [mm]'];
      
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   try:
      erstbelastung = daten['Erstbelastung'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
      return False;
   #
   if ('Anfangsporenzahl [-]' in daten):
      variante = 'neu';
      try:
         trockenmasse = daten['Trockenmasse [g]'];
         porenzahl_anfang = daten['Anfangsporenzahl [-]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
         return False;
   else:
      variante = 'alt';
      try:
         kopfplatte = daten['Kopfplatte'];
         gesamttrockenmasse = daten['Trockenmasse mit Behaelter [g]'];
         behaeltermasse = daten['Behaeltermasse [g]'];
         refgewicht = kopfplatte['Last-ref [kg]'];
         refspannung = kopfplatte['Spannung-ref [kN/m^2]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
         return False;
   #
   tol = 1e-6;
   # --------------------------- Tab1 ---------------------------
   if (variante == 'alt'):
      trockenmasse = gesamttrockenmasse - behaeltermasse;
   #
   volumen_e = anfangshoehe * pi *(durchmesser/2.0)**2 / 1000.0; # [cm^3]
   #
   nulltests = [('Anfangshoehe', anfangshoehe), ('Trockenmasse', trockenmasse),
               ('Volumen', volumen_e), ('Korndichte', korndichte)];
   for bezeichnung, variable in nulltests:
      if (abs(variable) < tol):
         print('# Warnung: ' + bezeichnung + ' annaehernd Null');
         return False;
   #
   trockendichte = trockenmasse/volumen_e;
   daten.update([('Trockendichte [g/cm^3]', trockendichte)]);
   if (variante == 'alt'):
      porenzahl_anfang = korndichte/trockendichte - 1.0;
   #
   daten.update([('Volumen [cm^3]', volumen_e)]);
   #
   hs = anfangshoehe * trockendichte/korndichte;
   druckflaeche = pi*(durchmesser/2000.0)**2; # [m^2]
   if (variante == 'alt'):
      abgeleitetes_gewicht_kopfplatte = 1000.0*refspannung*druckflaeche/9.80665 - oedo_hebel*refgewicht;
      gewicht_kopfplatte = None;
      for ref_gewicht in oedo_gewichte_kopfplatte:
         if (abs(abgeleitetes_gewicht_kopfplatte - ref_gewicht) < 1e-3):
            gewicht_kopfplatte = ref_gewicht;
            break;
      #
      if (gewicht_kopfplatte is None):
         print('# Warnung: Konnte Gewicht der Oedometer-Kopfplatte nicht aus Referenzgewichten ableiten');
         gewicht_kopfplatte = abgeleitetes_gewicht_kopfplatte;
      #
      kopfplatte.update([('Gewicht [kg]', gewicht_kopfplatte)]);
      #
      oedo_sumgewicht = [sum(oedo_gewichtsplatten[0:idx_aktuell]) for idx_aktuell in range(len(oedo_gewichtsplatten))];
      oedo_spannungen = [(gewicht*oedo_hebel + gewicht_kopfplatte)*g/1000.0/druckflaeche for gewicht in oedo_sumgewicht]; # [kN/m^2]
      #
      daten.update([('Spannung-neuberechnet [kN/m^2]', oedo_spannungen)]);
   #
   for belastungsart in ['Erstbelastung', 'Entlastung', 'Wiederbelastung']:
      if (belastungsart not in daten):
         continue;
      #
      belastung = daten[belastungsart];
      if (variante == 'alt'):
         try:
            setzung = belastung['Setzung [mm]'];
            spannung = belastung['Spannung [kN/m^2]'];
         except KeyError as errormessage:
            print('# Warnung: Mindestens ein erforderlicher Wert aus ' + belastungsart + \
               ' nicht vorhanden - ' + str(errormessage));
            continue;
      else:
         try:
            setzung = belastung['Weg [mm]'];
            kraft = belastung['Kraft [kN]'];
         except KeyError as errormessage:
            print('# Warnung: Mindestens ein erforderlicher Wert aus ' + belastungsart + \
               ' nicht vorhanden - ' + str(errormessage));
            continue;
         #
         spannung = [einzelkraft/druckflaeche for einzelkraft in kraft];
         belastung.update([('Setzung [mm]', setzung)]);
         belastung.update([('Spannung [kN/m^2]', spannung)]);
      #
      if (any([(abs(tempsetzung - anfangshoehe) < tol) for tempsetzung in setzung])):
         print('# Warnung: Setzung erreicht Probenhoehe');
         continue;
      #
      porenzahl = [porenzahl_anfang - tempsetzung/100.0 * (1.0 + porenzahl_anfang) for tempsetzung in setzung];
      dehnung = [log(anfangshoehe/(anfangshoehe - tempsetzung)) for tempsetzung in setzung];
      #
      belastung.update([('Porenzahl [-]', porenzahl)]);
      belastung.update([('Dehnung-axial [-]', dehnung)]);
      #
      einstellungen = Datenstruktur();
      # FIXME: Einstellbare Parameter am besten an anderer Stelle definieren
      max_it = 500;
      puffergroesse = 0.95;
      intervall = [2*10**(idx) - min(spannung) for idx in range(-10, 6)];
      #
      einstellungen.update([('Iterationen-max', max_it)]);
      einstellungen.update([('Toleranz', tol)]);
      einstellungen.update([('Puffergroesse', puffergroesse)]);
      einstellungen.update([('Intervall', intervall)]);
      belastung.update([('Einstellungen', einstellungen)]);
      #
      a, b, c = LoeseGleichung(gleichung='y = a*ln(x+b)+c', x=spannung, y=dehnung,
         intervall=intervall, max_it=max_it, puffergroesse=puffergroesse, tol=tol);
      belastung.update([('Ausgleichs-Koeffizienten', [a, b, c])]);
      if (abs(a) < tol):
         print('# Warnung: Erster Ausgleichskoeffizient annaehernd Null');
         continue;
      #
      steifemodul = [(tempspannung + b) / a/1000.0 for tempspannung in spannung];
      belastung.update([('Steifemodul [kN/m^2]', steifemodul)]);
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteOedoCrl(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo-CRL und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   import datetime
   from .datenstruktur import Datenstruktur
   from .parameterbestimmung import _ViskohypoplastischTangentenpunkte, _ViskohypoplastischCalphaUndIv
   #
   _KennwerteOedo(daten=daten);
   #
   try:
      anfangshoehe = daten['Hoehe [mm]'];
      trockendichte = daten['Trockendichte [g/cm^3]'];
      korndichte = daten['Korndichte [g/cm^3]'];
      erstbelastung = daten['Erstbelastung'];
      versuch1 = daten['Laststufe 1'];
      versuch2 = daten['Laststufe 2'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
      return False;
   #
   try:
      a, b, c = daten['Erstbelastung']['Ausgleichs-Koeffizienten'];
   except:
      print('# Warnung: Ausgleichskoeffizienten fuer Erstbelastung konnten nicht ermittelt werden');
      return False;
   #
   tol = 1e-6;
   startdate = datetime.datetime(year=1899, month=12, day=30);
   #
   # ----------------- Dat-Seiten mit CRL-Daten -----------------
   hs = anfangshoehe * trockendichte/korndichte;
   for idx_seite in range(1, 9):
      seite = 'Laststufe ' + str(idx_seite);
      if (seite not in daten):
         break;
      #
      oedo = daten[seite];
      try:
         zeitwerte = oedo['Zeitwerte'];
         setzung = oedo['Setzung [mm]'];
         laststufen = oedo['Laststufen [kN/m^2]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens ein erforderlicher Wert aus ' + seite + ' nicht vorhanden - ' \
             + str(errormessage));
         break;
      #
      zeitpunkte = None;
      for idx_zeit in range(1):
         try:
            zeitpunkte = [startdate + datetime.timedelta(days=float(tempzeit)) for tempzeit in zeitwerte];
            break;
         except:
            pass;
         #
         try:
            # tempzeit.split('.')[0] um Mikrosekunden zu ignorieren
            zeitpunkte = [datetime.datetime.strptime(tempzeit.split('.')[0], '%d.%m.%Y %H:%M:%S') for tempzeit in zeitwerte];
            break;
         except:
            pass;
         #
         try:
            # tempzeit.split('.')[0] um Mikrosekunden zu ignorieren
            zeitpunkte = [datetime.datetime.strptime(tempzeit.split('.')[0], '%Y-%m-%d %H:%M:%S') for tempzeit in zeitwerte];
            break;
         except:
            pass;
      #
      if (zeitpunkte is None):
         print('# Warnung: Konnte Zeitstempel nicht konvertieren');
         continue;
      #
      stunden = [(tempzeitpunkt - zeitpunkte[0]).total_seconds()/3600.0 for tempzeitpunkt in zeitpunkte];
      zeitstempel = [tempzeit.strftime('%d.%m.%Y %H:%M:%S') for tempzeit in zeitpunkte];
      #
      hoehe = [anfangshoehe - setz for setz in setzung];
      porenzahl = [einzelhoehe/hs - 1.0 for einzelhoehe in hoehe];
      if (abs(max(setzung) - setzung[0]) < tol):
         print('# Warnung: Setzung fuer ' + seite + ' ungueltig');
         break;
      #
      spez_setzung = [100.0*(setz - setzung[0])/(max(setzung) - setzung[0]) for setz in setzung];
      #
      oedo.update([('Zeitstempel', zeitstempel)]);
      oedo.update([('Zeit [h]', stunden)]);
      oedo.update([('Hoehe [mm]', hoehe)]);
      oedo.update([('Setzung-spez [%]', spez_setzung)]);
      oedo.update([('Porenzahl [-]', porenzahl)]);
      #
      parameter = Datenstruktur();
      einstellungen = Datenstruktur();
      #
      # FIXME: Einstellbare Parameter am besten an anderer STelle definieren
      log_zu_sqrt = [1, 2];
      zwischenpunkte = 5;
      glaettungswert = 10;
      linearbereich = 0.1;
      #
      einstellungen.update([('Verhaeltnis Log/sqrt', log_zu_sqrt)]);
      einstellungen.update([('Zwischenpunkte', zwischenpunkte)]);
      einstellungen.update([('Glaettungswert', glaettungswert)]);
      einstellungen.update([('Linearer Bereich', linearbereich)]);
      oedo.update([('Einstellungen', einstellungen)]);
      #
      if (abs(a) > tol):
         E_s = (sum(laststufen)/len(laststufen) + b)/a;
         parameter.update([('Steifemodul [kN/m^2]', E_s)]);
      else:
         E_s = None;
      #
      try:
         c_alpha, I_v = _ViskohypoplastischCalphaUndIv(zeit=stunden, porenzahl=porenzahl,
            zwischenpunkte=zwischenpunkte);
         parameter.update([('c_alpha [-]', c_alpha)]);
      except:
         print('# Warnung: c_alpha konnte nicht bestimmt werden (ungueltige Werte fuer Stunden oder Porenzahlen)');
      #
      try:
         [logschnittpunkt, logwendepunkt, sqrt100punkt, sqrt90punkt, m100, m90] = \
            _ViskohypoplastischTangentenpunkte(zeit=stunden, spez_setzung=spez_setzung,
            log_zu_sqrt=log_zu_sqrt, zwischenpunkte=zwischenpunkte, glaettungswert=glaettungswert,
            linearbereich=linearbereich);
      except:
         print('# Warnung: Tangentenpunkte konnten nicht bestimmt werden (ungueltige Werte fuer Stunden oder Setzungen');
         logschnittpunkt = None;
      #
      if (logschnittpunkt is not None):
         # Bestimmung von c_v nach DIN EN ISO 17892-5 Gleichung B.10
         if (abs(m90[0]) < tol):
            print('# Warnung: m90 annaehernd Null');
            break;
         #
         T90_zu_t90 = 0.848/(3600.0*m90[0]);
         c_v = T90_zu_t90 * ((hoehe[0]+hoehe[-1])/1000.0/4.0)**2;
         parameter.update([('Setzung-primaer-100% [h]', m100[0])]);
         parameter.update([('c_v [m^2/s]', c_v)]);
         #
         if (E_s is not None):
            if (abs(E_s) > tol):
               k = 10.0*c_v/E_s;
               parameter.update([('Durchlaessigkeitsbeiwert [m/s]', k)]);
      #
      oedo.update([('Parameter', parameter)]);
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteOedoCrs(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo-CRS und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   
   Achtung: Gewicht der Kopfplatte wird nicht beruecksichtigt. Einige Dateien haben das Gewicht gar
            nicht, die anderen an unterschiedlichen Positionen
   """
   import datetime
   from .konstanten import pi, korndichte
   #
   try:
      zeitwert = daten['Zeitwert'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   startdate = datetime.datetime(year=1899, month=12, day=30);
   #
   for idx_zeit in range(1):
      try:
         delta = datetime.timedelta(days=float(zeitwert));
         aktuell = startdate + delta;
         daten.update([('Datum', aktuell.strftime('%B %Y'))]);
         break;
      except:
         pass;
      #
      try:
         tempzeit = datetime.datetime.strptime(zeitwert, '%B %Y');
         daten.update([('Datum', tempzeit.strftime('%B %Y'))]);
         break;
      except:
         pass;
      #
      print('# Warnung: Zeitwert >' + zeitwert + '< konnte nicht interpretiert werden');
   #
   for oedo_variante in ['Oedo-locker', 'Oedo-dicht']:
      try:
         oedo = daten[oedo_variante];
         kraft = oedo['Kraft [kN]'];
         weg = oedo['Weg [mm]'];
         hoehe = oedo['Hoehe [mm]'];
         durchmesser = oedo['Durchmesser [mm]'];
         masse = oedo['Masse [g]'];
         vscher = oedo['Schergeschwindigkeit [mm/min]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
         continue;
      #
      flaeche = pi*(durchmesser/2.0/1000.0)**2;# [m^2]
      volumen = 1000.0*flaeche*hoehe;# [cm^3]
      if (abs(masse) < tol):
         print('# Warnung: Masse in ' + oedo_variante + ' annaehernd Null');
         continue;
      #
      if (abs(flaeche) < tol):
         print('# Warnung: Flaeche in ' + oedo_variante + ' annaehernd Null');
         continue;
      #
      if (abs(volumen) < tol):
         print('# Warnung: Volumen in ' + oedo_variante + ' annaehernd Null');
         continue;
      #
      rho_0 = masse/volumen;
      e_0 = korndichte/rho_0 - 1.0;
      oedo.update([('Porenzahl-e0 [-]', e_0)]);
      #
      spannung = [einzelkraft/flaeche for einzelkraft in oedo['Kraft [kN]']];
      oedo.update([('Spannung [kN/m^2]', spannung)]);
      weg_korrigiert = [tempweg-weg[0] for tempweg in weg];
      stauchung = [100.0*tempweg/hoehe for tempweg in weg_korrigiert];
      oedo.update([('Stauchung [%]', stauchung)]);
      porenzahlen = [oedo['Porenzahl-e0 [-]'] - tempweg/hoehe*(1.0+oedo['Porenzahl-e0 [-]']) for tempweg in weg_korrigiert];
      oedo.update([('Porenzahl [-]', porenzahlen)]);
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteOedoCrsvisko(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo-CRS-Visko
   und speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   import datetime
   from .datenstruktur import Datenstruktur
   from .konstanten import pi
   from .parameterbestimmung import _ViskohypoplastischCRSPunkte
   #
   try:
      if ('Kraft [N]' in daten):
         kraft = [x/1000.0 for x in daten['Kraft [N]']];
      else:
         kraft = daten['Kraft [kN]'];
      #
      stauchung = daten['Stauchung [mm]'];
      hoehe = daten['Hoehe [mm]'];
      durchmesser = daten['Durchmesser [mm]'];
      #
      gesamttrockenmasse = daten['Trockenmasse mit Behaelter [g]'];
      behaeltermasse = daten['Behaeltermasse [g]'];
      parameter = daten['Parameter'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   startdate = datetime.datetime(year=1899, month=12, day=30);
   #
   if ('Zeit [s]' in daten):
      zeit = daten['Zeit [s]'];
      # Ziehe Offset ab und speichere die bereinigte Zeit wieder
      zeit = [einzelzeit - zeit[0] for einzelzeit in zeit];
      daten.update([('Zeit [s]', zeit)]);
   else:
      try:
         datum = daten['Datum'];
         uhrzeit = daten['Uhrzeit'];
      except:
         print('# Warnung: Keine Zeitwerte gefunden - ' + str(errormessage));
         return False;
      #
      try:
         f_datum = [float(x) for x in datum];
         f_uhrzeit = [float(x) for x in uhrzeit];
      except:
         print('# Warnung: Ungueltige Zeit/Datum');
         return False;
      #
      zeitpunkt = [startdate + datetime.timedelta(f_datum[idx]+f_uhrzeit[idx]) for idx in range(len(datum))];
      zeitdelta = [einzelzeitpunkt - zeitpunkt[0] for einzelzeitpunkt in zeitpunkt];
      zeit = [einzeldelta.total_seconds() for einzeldelta in zeitdelta];
      daten.update([('Zeit [s]', zeit)]);
   #
   if ('Korndichte [g/cm^3]' in daten):
      korndichte = daten['Korndichte [g/cm^3]'];
   elif ('Korndichte' in daten):
      try:
         korndichte = float(daten['Korndichte']);
      except:
         try:
            korndichte = float(daten['Korndichte'].split('=')[1]);
         except:
            print('# Warnung: Probleme eim Konvertieren der Korndichte');
            return False;
   else:
      print('# Warnung: Keine Korndichte uebergeben');
      return False;
   #
   flaeche = pi*(durchmesser/2.0/1000.0)**2;# [m^2]
   volumen = 1000.0*flaeche*hoehe;# [cm^3]
   if (abs(flaeche) < tol):
      print('# Warnung: Flaeche annaehernd Null');
      return False;
   #
   if (abs(volumen) < tol):
      print('# Warnung: Volumen annaehernd Null');
      return False;
   # Zeit ueberpruefen sollte reichen, da Zeit-Kraft-Stauchung als Gruppe eingelesen wird
   if (len(zeit) < 10):
      print('# Warnung: Zu wenig Werte');
      return False;
   #
   if (abs(zeit[9]) < tol):
      print('# Warnung: Zeit annaehernd Null');
      return False;
   #
   pos_maxwert = kraft.index(max(kraft));
   if (pos_maxwert != len(kraft)-1):
      print('# Hinweis: Verwerfe Werte nach Maximalkraft (ab Index ' + str(pos_maxwert) +')');
      zeit = zeit[:pos_maxwert+1];
      kraft = kraft[:pos_maxwert+1];
      stauchung = stauchung[:pos_maxwert+1];
   #
   stauchungsrate = stauchung[9]*60.0/zeit[9];# [mm/min]
   spannungen = [einzelkraft/flaeche for einzelkraft in kraft];
   #
   daten.update([('Stauchungsrate [mm/min]', stauchungsrate)]);
   daten.update([('Spannung [kN/m^2]', spannungen)]);
   #
   trockendichte = (gesamttrockenmasse - behaeltermasse)/volumen;
   if (abs(trockendichte) < tol):
      print('# Warnung: Trockendichte annaehernd Null');
      return False;
   #
   porenzahl_e = korndichte/trockendichte - 1.0;
   porenzahl = [porenzahl_e - (1.0 + porenzahl_e)*einzelstauchung/hoehe for einzelstauchung in stauchung];
   daten.update([('Porenzahl [-]', porenzahl)]);
   #
   einstellungen = Datenstruktur();
   # FIXME: Einstellbare Parameter am besten an anderer Stelle definieren
   intervallgroesse = 25;
   p1logverhaeltnis = 0.5;
   p5logverhaeltnis = 0.5;
   einstellungen.update([('Intervallgroesse', intervallgroesse)]);
   einstellungen.update([('P1 Logverhaeltnis', p1logverhaeltnis)]);
   einstellungen.update([('P5 Logverhaeltnis', p5logverhaeltnis)]);
   daten.update([('Einstellungen', einstellungen)]);
   #
   idxliste = _ViskohypoplastischCRSPunkte(spannungen=spannungen, intervallgroesse=intervallgroesse,
      p1logverhaeltnis=p1logverhaeltnis, p5logverhaeltnis=p5logverhaeltnis);
   if (idxliste != []):
      punkte = Datenstruktur();
      punktspannungen = [spannungen[idx] for idx in idxliste];
      punktporenzahl = [porenzahl[idx] for idx in idxliste];
      punkte.update([('Indizes', idxliste)]);
      punkte.update([('Spannungen [kN/m^2]', punktspannungen)]);
      punkte.update([('Porenzahl [-]', punktporenzahl)]);
      daten.update([('Punkte', punkte)]);
   #
   parameter.update([('Parameter-Hilfen', ['e100 [-]', 'lambda [-]', 'kappa [-]', 'beta_x [-]', 'I_v [-]', 'D_r [-]', 'OCR [-]'])]);
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteTriaxVersuchstabelle(daten):
   """Bestimme die Kennwerte der Versuchstabelle zu einer eingelesenen Dateistruktur nach der
   Vorlage Triax-D, Triax-CU oder Triax-p-q und speichere sie in der uebergebenen Struktur daten,
   sofern diese den Vorgaben entspricht.
   """
   from .datenstruktur import Datenstruktur
   from .konstanten import pi
   #
   try:
      herstellung = daten['1-Probenherstellung'];
      saettigung = daten['2-Saettigung'];
      if ('3-Konsolidation' in daten):
         konsolidation = daten['3-Konsolidation'];
      else:
         konsolidation = dict();
      #
      if ('Hoehe [cm]' in herstellung):
         hoehe_e = [10.0*x for x in herstellung['Hoehe [cm]']];
         herstellung.update([('Hoehe [mm]', hoehe_e)]);
         del herstellung['Hoehe [cm]'];
      #
      hoehe_e = herstellung['Hoehe [mm]'];
      #
      if ('Durchmesser [cm]' in herstellung):
         durchmesser_e = [10.0*x for x in herstellung['Durchmesser [cm]']];
         herstellung.update([('Durchmesser [mm]', durchmesser_e)]);
         del herstellung['Durchmesser [cm]'];
      #
      durchmesser_e = herstellung['Durchmesser [mm]'];
      trockenmasse_e = herstellung['Trockenmasse [g]'];
      #
      zelldruck = saettigung['Zelldruck [kN/m^2]'];
      saettigungsdruck = saettigung['Saettigungsdruck [kN/m^2]'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   #
   mit_korndichte = False;
   try:
      korndichte = daten['Korndichte [g/cm^3]'];
      if (abs(korndichte) < tol):
         print('# Warnung: Korndichte annaehernd Null');
      else:
         mit_korndichte = True;
   except:
      pass;
   #
   variante = None;
   if (('Backvolume-Ende [mm^3]' in saettigung) and ('Backvolume-Ende [mm^3]' in konsolidation) and mit_korndichte):
      variante = 'drainiert';
      backvolume_ende_s = saettigung['Backvolume-Ende [mm^3]'];
      backvolume_ende_k = konsolidation['Backvolume-Ende [mm^3]'];
   #
   elif ('Feuchtmasse [g]' in herstellung):
      feuchtmasse_e = herstellung['Feuchtmasse [g]'];
      variante = 'undrainiert';
   #
   if (variante is None):
      print('# Warnung: Triax-Tabelle konnte keiner (implementierten) Variante zugeordnet werden');
      return False;
   #
   # --------------------- Probenherstellung --------------------
   #
   # Normalerweise sollten immer drei Versuche durchgefuehrt werden, aber im Allgemeinen wird die
   # Versuchsanzahl aus den eingetragenen/gueltigen Anfangshoehen hoehe_e abgeleitet
   anzahl_versuche = len(hoehe_e);
   volumen_e = [pi*(durchmesser_e[idx]/10.0/2.0)**2 * hoehe_e[idx]/10.0 for idx in range(anzahl_versuche)];
   herstellung.update([('Volumen [cm^3]', volumen_e)]);
   #
   nulltests = [('Trockenmasse', trockenmasse_e), ('Volumen', volumen_e)];
   for bezeichnung, wert in nulltests:
      if (any([(abs(einzelvar) < tol) for einzelvar in wert])):
         print('# Warnung: Mindestens ein(e) ' + bezeichnung + ' annaehernd Null');
         return False;
   #
   if (variante == 'drainiert'):
      wassergehalt_e = [(volumen_e[idx] - trockenmasse_e[idx]/korndichte - backvolume_ende_s[idx]/1000.0)/trockenmasse_e[idx] for idx in range(anzahl_versuche)];
   else:
      wassergehalt_e = [(feuchtmasse_e[idx]-trockenmasse_e[idx])/trockenmasse_e[idx] for idx in range(anzahl_versuche)];
   #
   herstellung.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_e])]);
   if (mit_korndichte):
      wassergehalt100 = [(volumen_e[idx] - trockenmasse_e[idx]/korndichte)/trockenmasse_e[idx] for idx in range(anzahl_versuche)];
      herstellung.update([('Wassergehalt-100%-Saettigung [-]', wassergehalt100)]);
      #
      if (any([(abs(einzelvar + 1.0) < tol) for einzelvar in wassergehalt100])):
         print('# Warnung: Mindestens ein Wassergehalt 100%-Saettigung annaehernd -1');
         return False;
   #
   wassermasse = [wassergehalt_e[idx]*trockenmasse_e[idx] for idx in range(anzahl_versuche)];
   herstellung.update([('Wassermasse [g]', wassermasse)]);
   #
   if (variante == 'drainiert'):
      feuchtmasse_e = [trockenmasse_e[idx]+wassermasse[idx] for idx in range(anzahl_versuche)];
      herstellung.update([('Feuchtmasse [g]', feuchtmasse_e)]);
   #
   einbaudichte = [feuchtmasse_e[idx]/volumen_e[idx] for idx in range(anzahl_versuche)];
   herstellung.update([('Dichte [g/cm^3]', einbaudichte)]);
   trockendichte_e = [trockenmasse_e[idx]/volumen_e[idx] for idx in range(anzahl_versuche)];
   herstellung.update([('Dichte-trocken [g/cm^3]', trockendichte_e)]);
   #
   if (mit_korndichte):
      porenanteil_e = [1.0 - trockendichte_e[idx]/korndichte for idx in range(anzahl_versuche)];
      herstellung.update([('Porenanteil [-]', porenanteil_e)]);
      #
      nulltests = [('Trockendichte', trockendichte_e), ('Porenanteil', porenanteil_e)];
      for bezeichnung, variable in nulltests:
         if (any([(abs(einzelvar) < tol) for einzelvar in variable])):
            print('# Warnung: Mindestens ein(e) ' + bezeichnung + ' (Herstellung) annaehernd Null');
            return False;
      #
      porenzahl_e = [korndichte/trockendichte_e[idx] - 1.0 for idx in range(anzahl_versuche)];
      herstellung.update([('Porenzahl [-]', porenzahl_e)]);
      saettigung_e = [wassergehalt_e[idx]*trockendichte_e[idx]/porenanteil_e[idx] for idx in range(anzahl_versuche)];
      herstellung.update([('Saettigungsgrad [-]', saettigung_e)]);
   #
   mit_dichten = True;
   try:
      dichte_dicht = daten['Dichte-dichteste-Lagerung [g/cm^3]'];
      dichte_locker = daten['Dichte-lockerste-Lagerung [g/cm^3]'];
      #
      if (abs(dichte_dicht - dichte_locker) < tol):
         print('# Warnung: Differenz (Dichte) lockerste/dichteste Lagerung annaehernd Null');
         return False;
   except:
      mit_dichten = False;
   #
   if ((variante == 'drainiert') and mit_dichten):
      lagerungsdichte_e = [(trockendichte_e[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)];
      herstellung.update([('Lagerungsdichte [-]', lagerungsdichte_e)]);
      lagerungsdichte_e_bez = [lagerungsdichte_e[idx]*dichte_dicht/trockendichte_e[idx] for idx in range(anzahl_versuche)];
      herstellung.update([('Lagerungsdichte-bez [-]', lagerungsdichte_e_bez)]);
   #
   mit_konsistenzen = True;
   try:
      fliessgrenze = daten['Fliessgrenze [%]'];
      ausrollgrenze = daten['Ausrollgrenze [%]'];
      ueberkorn = daten['Ueberkorn > 0,4mm [%]'];
      #
      if (fliessgrenze == ausrollgrenze):
         print('# Warnung: Fliessgrenze entspricht Ausrollgrenze - kann keine Konsistenzzahl ermitteln');
         mit_konsistenzen = False;
   except:
      mit_konsistenzen = False;
   #
   if ((variante == 'undrainiert') and mit_konsistenzen):
      konsistenzzahl_e = [(fliessgrenze-100.0*wassergehalt_e[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)];
      herstellung.update([('Konsistenzzahl [-]', konsistenzzahl_e)]);
      liquiditaetszahl_e = [1.0-temp_kons for temp_kons in konsistenzzahl_e];
      herstellung.update([('Liquiditaetszahl [-]', liquiditaetszahl_e)]);
   #
   # ------------------------ Saettigung ------------------------
   mit_backvolume = True;
   try:
      backvolume_start = saettigung['Backvolume-Start [mm^3]'];
   except:
      mit_backvolume = False;
   #
   if ((variante == 'drainiert') and mit_backvolume):
      wassermasse_s = [(backvolume_ende_s[idx] - backvolume_start[idx])/1000.0 + wassermasse[idx] for idx in range(anzahl_versuche)];
      wassergehalt_s = [wassermasse_s[idx]/trockenmasse_e[idx] for idx in range(anzahl_versuche)];
   elif (mit_korndichte):
      wassergehalt_s = wassergehalt100;
      wassermasse_s = [trockenmasse_e[idx]*wassergehalt100[idx] for idx in range(anzahl_versuche)];
      #
      saettigung.update([('Wassermasse [g]', wassermasse_s)]);
      saettigung.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_s])]);
      dichte_s = [(wassermasse_s[idx] + trockenmasse_e[idx])/volumen_e[idx] for idx in range(anzahl_versuche)];
      saettigung.update([('Dichte [g/cm^3]', dichte_s)]);
      trockendichte_s = [dichte_s[idx]/(1.0 + wassergehalt_s[idx]) for idx in range(anzahl_versuche)];
      saettigung.update([('Dichte-trocken [g/cm^3]', trockendichte_s)]);
      porenanteil_s = [1.0 - trockendichte_s[idx]/korndichte for idx in range(anzahl_versuche)];
      saettigung.update([('Porenanteil [-]', porenanteil_s)]);
      #
      if (any([(abs(einzelvar) < tol) for einzelvar in trockendichte_s])):
         print('# Warnung: Mindestens eine Trockendichte (Saettigung) annaehernd Null');
         return False;
      #
      porenzahl_s = [korndichte/trockendichte_s[idx] - 1.0 for idx in range(anzahl_versuche)];
      saettigung.update([('Porenzahl [-]', porenzahl_s)]);
      saettigung_s = [wassergehalt_s[idx]*trockendichte_s[idx]/porenanteil_s[idx] for idx in range(anzahl_versuche)];
      saettigung.update([('Saettigungsgrad [-]', saettigung_s)]);
      #
      if ((variante == 'drainiert') and mit_dichten):
         lagerungsdichte_s = [(trockendichte_s[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)];
         saettigung.update([('Lagerungsdichte [-]', lagerungsdichte_s)]);
         lagerungsdichte_s_bez = [lagerungsdichte_s[idx]*dichte_dicht/trockendichte_s[idx] for idx in range(anzahl_versuche)];
         saettigung.update([('Lagerungsdichte-bez [-]', lagerungsdichte_s_bez)]);
      elif ((variante == 'undrainiert') and mit_konsistenzen):
         konsistenzzahl_s = [(fliessgrenze-100.0*wassergehalt_s[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)];
         saettigung.update([('Konsistenzzahl [-]', konsistenzzahl_s)]);
         liquiditaetszahl_s = [1.0-temp_kons for temp_kons in konsistenzzahl_s];
         saettigung.update([('Liquiditaetszahl [-]', liquiditaetszahl_s)]);
   #
   # ----------------------- Konsolidation ----------------------
   if (variante == 'drainiert'):
      konsolidation.update([('Backvolume-Start [mm^3]', backvolume_ende_s)]);
   else:
      try:
         delta_hoehe_k = konsolidation['Delta Hoehe [mm]'];
         durchmesser_k = [durchmesser_e[idx]*(hoehe_e[idx]-delta_hoehe_k[idx])/hoehe_e[idx] for idx in range(anzahl_versuche)];
         konsolidation.update([('Durchmesser [mm]', durchmesser_k)]);
      except:
         pass;
   #
   # --------------------- Nach Konsolidation -------------------
   nachkon_vorgaben = False;
   try:
      nachkon = daten['4-Nach Konsolidation'];
      hoehe_n = nachkon['Hoehe [mm]'];
      durchmesser_n = nachkon['Durchmesser [mm]'];
      nachkon_vorgaben = True;
   except:
      pass;
   #
   if (nachkon_vorgaben):
      volumen_n = [(hoehe_n[idx])/10.0*pi*(durchmesser_n[idx]/2.0/10.0)**2 for idx in range(anzahl_versuche)];
      delta_volumen_n = [volumen_e[idx] - volumen_n[idx] for idx in range(anzahl_versuche)];
   else:
      nachkon = Datenstruktur();
      if (variante == 'drainiert'):
         delta_volumen_n = [(backvolume_ende_s[idx] - backvolume_ende_k[idx])/1000.0 for idx in range(anzahl_versuche)];
         volumen_n = [volumen_e[idx] - delta_volumen_n[idx] for idx in range(anzahl_versuche)];
         hoehe_n = [hoehe_e[idx]*(1.0 - delta_volumen_n[idx]/volumen_e[idx]/3.0) for idx in range(anzahl_versuche)];
      elif ('Delta Hoehe [mm]' in konsolidation):
         volumen_n = [(hoehe_e[idx]-delta_hoehe_k[idx])/10.0*pi*(durchmesser_k[idx]/2.0/10.0)**2 for idx in range(anzahl_versuche)];
         delta_volumen_n = [volumen_e[idx] - volumen_n[idx] for idx in range(anzahl_versuche)];
         hoehe_n = [hoehe_e[idx]-delta_hoehe_k[idx] for idx in range(anzahl_versuche)];
      else:
         print('# Warnung: Werte fuer den Zustand nach der Konsolidation fehlen (Hoehe/Durchmesser/Volumen)');
         return False;
      #
      nachkon.update([('Hoehe [mm]', hoehe_n)]);
      durchmesser_n = [durchmesser_e[idx]*(1.0 - delta_volumen_n[idx]/volumen_e[idx]/3.0) for idx in range(anzahl_versuche)];
      nachkon.update([('Durchmesser [mm]', durchmesser_n)]);
   #
   nachkon.update([('Volumenaenderung [cm^3]', delta_volumen_n)]);
   nachkon.update([('Volumen [cm^3]', volumen_n)]);
   #
   if (any([(abs(einzelvar) < tol) for einzelvar in volumen_n])):
      print('# Warnung: Mindestens ein Volumen (Nach Konsolidation) annaehernd Null');
      return False;
   #
   if (not mit_korndichte):
      daten.update([('4-Nach Konsolidation', nachkon)]);
      print('# Hinweis: Berechnen der Tabellenwerte aufgrund fehlender Korndichte vorzeitig beendet');
      return False;
   #
   feuchtmasse_n = [trockenmasse_e[idx] + wassermasse_s[idx] - delta_volumen_n[idx] for idx in range(anzahl_versuche)];
   nachkon.update([('Feuchtmasse [g]', feuchtmasse_n)]);
   wassergehalt_n = [(feuchtmasse_n[idx]-trockenmasse_e[idx])/trockenmasse_e[idx] for idx in range(anzahl_versuche)];
   nachkon.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_n])]);
   dichte_n = [feuchtmasse_n[idx]/volumen_n[idx] for idx in range(anzahl_versuche)];
   nachkon.update([('Dichte [g/cm^3]', dichte_n)]);
   trockendichte_n = [trockenmasse_e[idx]/volumen_n[idx] for idx in range(anzahl_versuche)];
   nachkon.update([('Dichte-trocken [g/cm^3]', trockendichte_n)]);
   #
   if (any([(abs(einzelvar) < tol) for einzelvar in trockendichte_n])):
      print('# Warnung: Mindestens eine Trockendichte (Nach Konsolidation) annaehernd Null');
      return False;
   #
   porenanteil_n = [1.0 - trockendichte_n[idx]/korndichte for idx in range(anzahl_versuche)];
   nachkon.update([('Porenanteil [-]', porenanteil_n)]);
   porenzahl_n = [korndichte/trockendichte_n[idx] - 1.0 for idx in range(anzahl_versuche)];
   nachkon.update([('Porenzahl [-]', porenzahl_n)]);
   saettigung_n = [wassergehalt_n[idx]*trockendichte_n[idx]/porenanteil_n[idx] for idx in range(anzahl_versuche)];
   nachkon.update([('Saettigungsgrad [-]', saettigung_n)]);
   #
   if ((variante == 'drainiert') and mit_dichten):
      lagerungsdichte_n = [(trockendichte_n[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)];
      nachkon.update([('Lagerungsdichte [-]', lagerungsdichte_n)]);
      lagerungsdichte_n_bez = [lagerungsdichte_n[idx]*dichte_dicht/trockendichte_n[idx] for idx in range(anzahl_versuche)];
      nachkon.update([('Lagerungsdichte-bez [-]', lagerungsdichte_n_bez)]);
   elif ((variante == 'undrainiert') and mit_konsistenzen):
      konsistenzzahl_n = [(fliessgrenze-100.0*wassergehalt_n[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)];
      nachkon.update([('Konsistenzzahl [-]', konsistenzzahl_n)]);
      liquiditaetszahl_n = [1.0-temp_kons for temp_kons in konsistenzzahl_n];
      nachkon.update([('Liquiditaetszahl [-]', liquiditaetszahl_n)]);
   #
   if ('4-Nach Konsolidation' not in daten):
      daten.update([('4-Nach Konsolidation', nachkon)]);
   #
   # ---------------- p-q-Pfad (falls vorhanden) ----------------
   if ('5-p-q-Pfad' in daten):
      for segmentname in ['Segment 2', 'Segment 4']:
         try:
            segment = daten['5-p-q-Pfad'][segmentname];
            porenwasserdruck_p = segment['Porenwasserdruck [kN/m^2]'];
            eff_iso_druck_p = segment['Druck-isotrop-eff [kN/m^2]'];
            hauptspannungsdiff_p = segment['Hauptspannungsdifferenz [kN/m^2]'];
         except KeyError as errormessage:
            print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
            continue;
         #
         druck_total_iso_p = [porenwasserdruck_p[idx] + eff_iso_druck_p[idx] for idx in range(anzahl_versuche)];
         segment.update([('Druck-isotrop [kN/m^2]', druck_total_iso_p)]);
         zelldruck_p = [(3.0*druck_total_iso_p[idx] - hauptspannungsdiff_p[idx])/3.0 for idx in range(anzahl_versuche)];
         segment.update([('Zelldruck [kN/m^2]', zelldruck_p)]);
         normalspannung_p = [zelldruck_p[idx] + hauptspannungsdiff_p[idx] for idx in range(anzahl_versuche)];
         segment.update([('Normalspannung [kN/m^2]', normalspannung_p)]);
      #
      # Falls ein p-q-Pfad vorhanden ist, existiert kein abscheren-Eintrag -> beenden
      return True;
   #
   # ------------------------- Abscheren ------------------------
   if (variante == 'drainiert'):
      try:
         abscheren = daten['5-Abscheren'];
         backvolume_ende_a = abscheren['Backvolume-Ende [mm^3]'];
      except:
         print('# Warnung: Backvolume (Abscheren) fuer Triax-D nicht gefunden');
         return False;
      #
      delta_volumen_a = [(backvolume_ende_k[idx] - backvolume_ende_a[idx])/1000.0 for idx in range(anzahl_versuche)];
   else:
      abscheren = Datenstruktur();
      delta_volumen_a = [0.0, 0.0, 0.0];
   #
   abscheren.update([('Volumenaenderung [cm^3]', delta_volumen_a)]);
   volumen_a = [volumen_n[idx] - delta_volumen_a[idx] for idx in range(anzahl_versuche)];
   abscheren.update([('Volumen [cm^3]', volumen_a)]);
   #
   if (any([(abs(einzelvar) < tol) for einzelvar in volumen_a])):
      print('# Warnung: Mindestens ein Volumen (Abscheren) annaehernd Null');
      return False;
   #
   feuchtmasse_a = [feuchtmasse_n[idx] - delta_volumen_a[idx] for idx in range(anzahl_versuche)];
   abscheren.update([('Feuchtmasse [g]', feuchtmasse_a)]);
   wassergehalt_a = [(feuchtmasse_a[idx]-trockenmasse_e[idx])/trockenmasse_e[idx] for idx in range(anzahl_versuche)];
   abscheren.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_a])]);
   dichte_a = [feuchtmasse_a[idx]/volumen_a[idx] for idx in range(anzahl_versuche)];
   abscheren.update([('Dichte [g/cm^3]', dichte_a)]);
   trockendichte_a = [trockenmasse_e[idx]/volumen_a[idx] for idx in range(anzahl_versuche)];
   abscheren.update([('Dichte-trocken [g/cm^3]', trockendichte_a)]);
   #
   if (any([(abs(einzelvar) < tol) for einzelvar in trockendichte_n])):
      print('# Warnung: Mindestens eine Trockendichte (Abscheren) annaehernd Null');
      return False;
   #
   porenanteil_a = [1.0 - trockendichte_a[idx]/korndichte for idx in range(anzahl_versuche)];
   abscheren.update([('Porenanteil [-]', porenanteil_a)]);
   porenzahl_a = [korndichte/trockendichte_a[idx] - 1.0 for idx in range(anzahl_versuche)];
   abscheren.update([('Porenzahl [-]', porenzahl_a)]);
   saettigung_a = [wassergehalt_a[idx]*trockendichte_a[idx]/porenanteil_a[idx] for idx in range(anzahl_versuche)];
   abscheren.update([('Saettigungsgrad [-]', saettigung_a)]);
   #
   if ((variante == 'drainiert') and mit_dichten):
      lagerungsdichte_a = [(trockendichte_a[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)];
      abscheren.update([('Lagerungsdichte [-]', lagerungsdichte_a)]);
      lagerungsdichte_a_bez = [lagerungsdichte_a[idx]*dichte_dicht/trockendichte_a[idx] for idx in range(anzahl_versuche)];
      abscheren.update([('Lagerungsdichte-bez [-]', lagerungsdichte_a_bez)]);
   elif ((variante == 'undrainiert') and mit_konsistenzen):
      konsistenzzahl_a = [(fliessgrenze-100.0*wassergehalt_a[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)];
      abscheren.update([('Konsistenzzahl [-]', konsistenzzahl_a)]);
      liquiditaetszahl_a = [1.0-temp_kons for temp_kons in konsistenzzahl_a];
      abscheren.update([('Liquiditaetszahl [-]', liquiditaetszahl_a)]);
   #
   if ('5-Abscheren' not in daten):
      daten.update([('5-Abscheren', abscheren)]);
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteTriax(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Triax-D oder
   Triax-CU und speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben
   entspricht.
   """
   import datetime
   from math import asin, atan
   from .konstanten import grad2rad
   from .datenstruktur import Datenstruktur
   from .gleichungsloeser import LinearesAusgleichsproblem, LinearInterpoliertenIndexUndFaktor
   from .gleichungsloeser import WinkelTangenteAnKreisboegen
   #
   try:
      versuch1 = daten['Versuch 1'];
      herstellung = daten['1-Probenherstellung'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   variante = 'drainiert';
   if (('Trockenmasse mit Behaelter [g]' in daten) and ('Behaeltermasse [g]' in daten)):
      variante = 'undrainiert';
      trockenmasse_z = daten['Trockenmasse mit Behaelter [g]'];
      behaeltermasse_z = daten['Behaeltermasse [g]'];
      trockenmasse_e = [trockenmasse_z[idx] - behaeltermasse_z[idx] for idx in range(len(trockenmasse_z))];
      herstellung.update([('Trockenmasse [g]', trockenmasse_e)]);
   #
   versuche = [versuch1];
   if ('Versuch 2' in daten):
      versuche += [daten['Versuch 2']];
   #
   if ('Versuch 3' in daten):
      versuche += [daten['Versuch 3']];
   #
   if ('1-Probenherstellung' in versuch1):
      try:
         durchmesser_e = [x['1-Probenherstellung']['Durchmesser [mm]'] for x in versuche];
         hoehe_e = [x['1-Probenherstellung']['Hoehe [mm]'] for x in versuche];
         durchmesser_n = [x['4-Nach Konsolidation']['Durchmesser [mm]'] for x in versuche];
         hoehe_n = [x['4-Nach Konsolidation']['Hoehe [mm]'] for x in versuche];
         daten['1-Probenherstellung'].update([('Durchmesser [mm]', durchmesser_e)]);
         daten['1-Probenherstellung'].update([('Hoehe [mm]', hoehe_e)]);
         nachkon = Datenstruktur();
         nachkon.update([('Durchmesser [mm]', durchmesser_n)]);
         nachkon.update([('Hoehe [mm]', hoehe_n)]);
         daten.update([('4-Nach Konsolidation', nachkon)]);
         #
         del versuch1['1-Probenherstellung'];
         del versuch2['1-Probenherstellung'];
         del versuch3['1-Probenherstellung'];
         del versuch1['4-Nach Konsolidation'];
         del versuch2['4-Nach Konsolidation'];
         del versuch3['4-Nach Konsolidation'];
      except:
         pass;
   #
   _KennwerteTriaxVersuchstabelle(daten=daten);
   #
   try:
      trockenmasse_e = herstellung['Trockenmasse [g]'];
      nachkon = daten['4-Nach Konsolidation'];
      hoehe_n = nachkon['Hoehe [mm]'];
      volumen_n = nachkon['Volumen [cm^3]'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   #
   if (any([(abs(einzelvar) < tol) for einzelvar in hoehe_n])):
      print('# Warnung: Mindestens eine Hoehe (Nach Konsolidation) annaehernd Null');
      return False;
   #
   startdate = datetime.datetime(year=1899, month=12, day=30);
   sigma_1 = [None, None, None];
   sigma_3 = [None, None, None];
   #
   for idx_triax, triax_versuch in enumerate(['Versuch 1', 'Versuch 2', 'Versuch 3']):
      try:
         triax = daten[triax_versuch];
         radialdruck = triax['Radialdruck [kN/m^2]'];
         porenwasserdruck = triax['Porenwasserdruck [kN/m^2]'];
         #
         if ('Axialkraft [N]' in triax):
            axialkraft = [x/1000.0 for x in triax['Axialkraft [N]']];
         else:
            axialkraft = triax['Axialkraft [kN]'];
         #
         stauchung = triax['Stauchung [mm]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
         continue;
      #
      if ('Zeit [s]' in triax):
         zeit = triax['Zeit [s]'];
      else:
         try:
            datum = triax['Datum'];
            uhrzeit = triax['Uhrzeit'];
         except:
            print('# Warnung: Keine Zeitwerte gefunden - ' + str(errormessage));
            continue;
         #
         zeitpunkt = None;
         for idx in range(1):
            try:
               zeitpunkt = [startdate + datetime.timedelta(float(datum[idx])+float(uhrzeit[idx])) for idx in range(len(datum))];
               break;
            except:
               pass;
            #
            try:
               zeitpunkt = [datetime.datetime.strptime(datum[idx], '%Y-%m-%d %H:%M:%S') +
                  (datetime.datetime.strptime(uhrzeit[idx], '%H:%M:%S')
                  - datetime.datetime(1900, 1, 1, 0, 0, 0)) for idx in range(len(datum))];
               break;
            except:
               pass;
         #
         if (zeitpunkt is None):
            print('# Warnung: Konnte Zeitweite nicht interpretieren');
            zeitpunkt = [0.0 for x in datum];
         #
         zeitdelta = [einzelzeitpunkt - zeitpunkt[0] for einzelzeitpunkt in zeitpunkt];
         zeit = [einzeldelta.total_seconds() for einzeldelta in zeitdelta];
         triax.update([('Zeit [s]', zeit)]);
      #
      numdaten = len(zeit);
      kraft = [einzel_axialkraft-axialkraft[0] for einzel_axialkraft in axialkraft];
      dehnung = [100.0*(einzel_stauchung-stauchung[0])/hoehe_n[idx_triax] for einzel_stauchung in stauchung];
      #
      if (any([(abs(hoehe_n[idx_triax] - tempstauchung) < tol) for tempstauchung in stauchung])):
         print('# Warnung: Stauchung entspricht annaehernd der Hoehe der konsolidierten Probe');
         continue;
      #
      mit_porenwasservol = False;
      try:
         porenwasservolumen = triax['Porenwasservolumen [mm^3]'];
         mit_porenwasservol = True;
      except:
         pass;
      #
      if (mit_porenwasservol):
         delta_volumen = [(vol-porenwasservolumen[0])/1000.0 for vol in porenwasservolumen];
         flaeche = [1000.0*(volumen_n[idx_triax]+delta_volumen[idx])/(hoehe_n[idx_triax]-stauchung[idx]) for idx in range(numdaten)];
         delta_v_v0 = [100.0*delta_volumen[idx]/(volumen_n[idx_triax]) for idx in range(numdaten)];
         triax.update([('delta V/V_0 [%]', delta_v_v0)]);
      else:
         flaeche = [1000.0*(volumen_n[idx_triax])/(hoehe_n[idx_triax]-stauchung[idx]) for idx in range(numdaten)];
      #
      if (any([(abs(tempflaeche) < tol) for tempflaeche in flaeche])):
         print('# Warnung: Mindestens eine Flaeche annaehernd Null');
         continue;
      #
      sig1sig3diff = [1e6*kraft[idx]/flaeche[idx]/2.0 for idx in range(numdaten)];
      sigma1prime = [(2.0*sig1sig3diff[idx] + radialdruck[idx]) - porenwasserdruck[idx] for idx in range(numdaten)];
      sigma3prime = [radialdruck[idx] - porenwasserdruck[idx] for idx in range(numdaten)];
      sig1sig3primesum = [(sigma1prime[idx] + sigma3prime[idx])/2.0 for idx in range(numdaten)];
      #
      if (variante == 'undrainiert'):
         if (any([(abs(tempsig3) < tol) for tempsig3 in sigma3prime])):
            print('# Warnung: Mindestens ein sigma3\' annaehernd Null');
            continue;
         #
         sig1psig3p = [sigma1prime[idx]/sigma3prime[idx] for idx in range(numdaten)];
         triax.update([('sig1_prime/sig3_prime [-]', sig1psig3p)]);
         triax.update([('Porenwasserdruck-Delta [kN/m^2]', [porendruck - porenwasserdruck[0] for porendruck in porenwasserdruck])]);
      #
      try:
         phi_prime = [asin((sigma1prime[idx]-sigma3prime[idx])/(sigma1prime[idx]+sigma3prime[idx]))/grad2rad for idx in range(numdaten)];
      except:
         print('# Warnung: phi\' konnte nicht bestimmt werden');
         continue;
      #
      mit_korndichte = False;
      try:
         korndichte = daten['Korndichte [g/cm^3]'];
         mit_korndichte = True;
      except:
         pass;
      #
      if (mit_korndichte):
         # Es wird bereits in _KennwerteTriaxVersuchstabelle sichergestellt, dass trockenmasse_e ungleich Null ist
         if (mit_porenwasservol):
            if (any([(abs(volumen_n[idx_triax]+temp_vol) < tol) for temp_vol in delta_volumen])):
               print('# Warnung: Differenz von mindestens einem Volumen zu Delta Volumen annaehernd Null');
               continue;
            #
            triax_porenzahlen = [korndichte/(trockenmasse_e[idx_triax]/(volumen_n[idx_triax]+delta_volumen[idx]))-1.0 for idx in range(numdaten)];
         else:
            # FIXME: Keine Porenzahlentwicklung ohne Aenderungsinformationen (idx nicht verwendet)
            triax_porenzahlen = [korndichte*volumen_n[idx_triax]/trockenmasse_e[idx_triax]-1.0 for idx in range(numdaten)];
         #
         triax.update([('Porenzahl [-]', triax_porenzahlen)]);
      #
      triax.update([('(sig_1 - sig_3)/2.0 [kN/m^2]', sig1sig3diff)]);
      triax.update([('(sig_1prime + sig_3prime)/2.0 [kN/m^2]', sig1sig3primesum)]);
      triax.update([('Reibungswinkel [Grad]', phi_prime)]);
      triax.update([('Dehnung [%]', dehnung)]);
      #
      peak = Datenstruktur();
      if (variante == 'drainiert'):
         idx_peak = sig1sig3diff.index(max(sig1sig3diff));
      else:
         idx_peak = sig1psig3p.index(max(sig1psig3p));
         peak.update([('Porenwasserdruck [kN/m^2]', porenwasserdruck[idx_peak])]);
      #
      peak.update([('Index', idx_peak)]);
      peak.update([('Sigma_1_prime [kN/m^2]', sigma1prime[idx_peak])]);
      peak.update([('Sigma_3_prime [kN/m^2]', sigma3prime[idx_peak])]);
      peak.update([('Dehnung [%]', dehnung[idx_peak])]);
      #
      if (mit_korndichte):
         peak.update([('Porenzahl [-]', triax_porenzahlen[idx_peak])]);
      #
      sigma_1[idx_triax] = sigma1prime[idx_peak];
      sigma_3[idx_triax] = sigma3prime[idx_peak];
      #
      if (variante == 'drainiert'):
         einstellungen = Datenstruktur();
         spanne = 1.2;
         maxspanne = max(min(dehnung), dehnung[idx_peak]-spanne);
         minspanne = min(max(dehnung), dehnung[idx_peak]+spanne);
         idx_dehnstart, faks = LinearInterpoliertenIndexUndFaktor(vergleichswert=maxspanne,
            vergleichswertliste=dehnung);
         idx_dehnende, faks = LinearInterpoliertenIndexUndFaktor(vergleichswert=minspanne,
            vergleichswertliste=dehnung);
         #
         einstellungen.update([('Spanne', spanne)]);
         einstellungen.update([('Dehnungsspanne (min/max)', [minspanne, maxspanne])]);
         triax.update([('Einstellungen', einstellungen)]);
         #
         if ((idx_dehnstart is None) or (idx_dehnende is None)):
            continue;
         #
         if (mit_porenwasservol):
            steigung, offset = LinearesAusgleichsproblem(x=dehnung[idx_dehnstart:idx_dehnende],
               y=delta_v_v0[idx_dehnstart:idx_dehnende]);
            #
            if (steigung < -1.0):
               print('# Warnung: Steigung sollte positiv (und muss groesser als -1) sein');
               continue;
            #
            geradenwinkel = atan(steigung)/grad2rad;
            dilatanzwinkel = asin(steigung/(2.0+steigung))/grad2rad;
            peak.update([('Geradenwinkel [Grad]', geradenwinkel)]);
            peak.update([('Dilatanzwinkel [Grad]', dilatanzwinkel)]);
      #
      triax.update([('Peakzustand', peak)]);
   #
   if (any([(tempsig is None) for tempsig in sigma_1]) or any([(tempsig is None) for tempsig in sigma_3])):
      print('# Warnung: Es konnten nicht alle drei Spannungen von sigma1/sigma3 erkannt werden');
      return False;
   #
   # --------------------- Mohr-Coulomb-Daten -------------------
   mc = Datenstruktur();
   mc.update([('Sigma_1 [kN/m^2]', sigma_1)]);
   mc.update([('Sigma_3 [kN/m^2]', sigma_3)]);
   #
   if (variante == 'drainiert'):
      # Finde die dazugehoerigen Reibungswinkel
      ohneKohaesion = WinkelTangenteAnKreisboegen(x_min=sigma_3, x_max=sigma_1, y_0=0);
      #
      ohne_c = Datenstruktur();
      ohne_c.update([('Reibungswinkel-eff [Grad]', ohneKohaesion[1])]);
      mc.update([('Ohne Kohaesion', ohne_c)]);
   else:
      mitKohaesion = [None, None, None];
      # Es gibt wahrscheinlich bessere Abschaetzungen, aber die Kohaesion
      # ist zumindest kleiner als der minimale radius
      # FIXME: Am besten das Intervall erst grob und dann in immer feineren Schritten unterteilen.
      radien = [(sigma_1[idx] - sigma_3[idx])/2.0 for idx in range(3)];
      max_kohaesion = min(radien);
      c_delta = 0.1;
      c_schritte = int(max_kohaesion/c_delta + 1.0);
      #
      if ((max_kohaesion > 80.0) or (c_schritte > 800)):
         print('# Warnung: max. Kohaesionswert zu gross - Berechnung von wuerde zuviele Iterationen benoetigen');
         return False;
      #
      for idx_kohaesion in range(c_schritte):
         c = idx_kohaesion*c_delta;
         temp_abstand, temp_winkel = WinkelTangenteAnKreisboegen(x_min=sigma_3, x_max=sigma_1, y_0=c);
         #
         if ((mitKohaesion[0] is None) or ((mitKohaesion[0] is not None) and (temp_abstand < mitKohaesion[0]))):
            mitKohaesion = [temp_abstand, temp_winkel, c];
      #
      mit_c = Datenstruktur();
      mit_c.update([('Reibungswinkel-eff [Grad]', mitKohaesion[1])]);
      mit_c.update([('Kohaesion [kN/m^2]', mitKohaesion[2])]);
      mc.update([('Mit Kohaesion', mit_c)]);
   #
   daten.update([('Mohr-Coulomb', mc)]);
   return True;
#


# -------------------------------------------------------------------------------------------------
def _KennwerteTriaxpq(daten):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Triax-p-q und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   from .datenstruktur import Datenstruktur
   from .parameterbestimmung import _ErweiterteHypoParamHilfsfunktion, _ErweiterteHypoParamHilfsfunktionEpssom
   #
   _KennwerteTriaxVersuchstabelle(daten=daten);
   #
   try:
      versuch1 = daten['Versuch 1'];
      versuch2 = daten['Versuch 2'];
      versuch3 = daten['Versuch 3'];
      #herstellung = daten['1-Probenherstellung'];
      nachkon = daten['4-Nach Konsolidation'];
      hoehe_n = nachkon['Hoehe [mm]'];
      volumen_n = nachkon['Volumen [cm^3]'];
      parameter = daten['Parameter'];
   except KeyError as errormessage:
      print('# Warnung: Mindestens ein erforderlicher Wert nicht vorhanden - ' + str(errormessage));
      return False;
   #
   tol = 1e-6;
   #
   epsliste = [None, None, None];
   emodulliste = [None, None, None];
   for idx_triax, triax_versuch in enumerate(['Versuch 1', 'Versuch 2', 'Versuch 3']):
      try:
         triax = daten[triax_versuch];
         stage = triax['Stage'];
         porenwasservolumen = triax['Porenwasservolumen [mm^3]'];
         radialdruck = triax['Radialdruck [kN/m^2]'];
         porenwasserdruck = triax['Porenwasserdruck [kN/m^2]'];
         # Bei p-q-Pfaden sind bei Axialkraft und Stauchung auch negative Bereiche erlaubt
         axialkraft = triax['Axialkraft [kN]'];
         stauchung = triax['Stauchung [mm]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
         continue;
      #
      numdaten = len(stage);
      kraft = [einzel_axialkraft-axialkraft[0] for einzel_axialkraft in axialkraft];
      dehnung = [(einzel_stauchung-stauchung[0])/hoehe_n[idx_triax] for einzel_stauchung in stauchung];
      delta_volumen = [(vol-porenwasservolumen[0])/1000.0 for vol in porenwasservolumen];
      #
      if (any([(abs(hoehe_n[idx_triax] - tempstauchung) < tol) for tempstauchung in stauchung])):
         print('# Warnung: Stauchung entspricht annaehernd der Hoehe der konsolidierten Probe');
         continue;
      #
      flaeche = [1000.0*(volumen_n[idx_triax]+delta_volumen[idx])/(hoehe_n[idx_triax]-stauchung[idx]) for idx in range(numdaten)];
      #
      if (any([(abs(tempflaeche) < tol) for tempflaeche in flaeche])):
         print('# Warnung: Mindestens eine Flaeche annaehernd Null');
         continue;
      #
      sig1sig3diff = [1e6*kraft[idx]/flaeche[idx]/2.0 for idx in range(numdaten)];
      sigma1 = [2.0*sig1sig3diff[idx] + radialdruck[idx] for idx in range(numdaten)];
      sigma1prime = [sigma1[idx] - porenwasserdruck[idx] for idx in range(numdaten)];
      sigma3prime = [radialdruck[idx] - porenwasserdruck[idx] for idx in range(numdaten)];
      #
      triax.update([('Dehnung [-]', dehnung)]);
      q = [sigma1[idx] - radialdruck[idx] for idx in range(numdaten)];
      triax.update([('Hauptspannungsdifferenz [kN/m^2]', q)]);
      p_prime = [(sigma1prime[idx] + 2.0*sigma3prime[idx])/3.0 for idx in range(numdaten)];
      triax.update([('Druck-isotrop-eff [kN/m^2]', p_prime)]);
      #
      # Statt den Stagenamen nur den Index einer Aenderung speichern
      stage_idxlist = [];
      letzte_stage = 0;
      for idx_stage, stagenum in enumerate(stage):
         if (stagenum > letzte_stage):
            stage_idxlist += [idx_stage];
            letzte_stage = stagenum;
      #
      if (len(stage_idxlist) < 2):
         print('# Warnung: Mindestens zwei Stages erforderlich');
         continue;
      #
      triax.update([('Schritte', stage_idxlist)]);
      #
      geglaettet = Datenstruktur();
      einstellungen = Datenstruktur();
      #
      # FIXME: Einstellbare Parameter am besten an anderer Stelle definieren
      offset = 0;# Standardmaessig wird kein Offset verwendet
      glaettungswert = 10;
      refspanne = 3;
      #
      einstellungen.update([('Glaettungspunkte', glaettungswert)]);
      einstellungen.update([('Startoffset', offset)]);
      einstellungen.update([('Referenzspanne', refspanne)]);
      geglaettet.update([('Einstellungen', einstellungen)]);
      #
      startidx = stage_idxlist[-1]+offset;
      if (startidx > len(stauchung)-1):
         print('# Warnung: Index fuer Stage und Offset liegt hinter der Grenze des Vektors');
         continue;
      #
      eps = [(einzelstauchung-stauchung[startidx])/(hoehe_n[idx_triax]-stauchung[startidx]) for einzelstauchung in stauchung[startidx:]];
      # T bzw. tau entspricht q/2
      q2 = [x/2.0 for x in q[startidx:]];
      eps_glatt, q_glatt, e_modul_glatt, R_max, E_max, fitoffset = _ErweiterteHypoParamHilfsfunktion(eps=eps,
         q=q2, glaettungswert=glaettungswert, refspanne=refspanne);
      # FIXME: Gueltigkeit der Rueckgabewerte pruefen
      #
      geglaettet.update([('Dehnung [-]', eps_glatt)]);
      geglaettet.update([('E-Modul [kN/m^2]', e_modul_glatt)]);
      geglaettet.update([('q/2 [kN/m^2]', q_glatt)]);
      geglaettet.update([('R [-]', R_max)]);
      geglaettet.update([('E-Modul-max [kN/m^2]', E_max)]);
      geglaettet.update([('Versatz', fitoffset)]);
      triax.update([('Glaettung', geglaettet)]);
      #
      mittelq = sum(q[stage_idxlist[-2]:stage_idxlist[-1]])/(stage_idxlist[-1]-stage_idxlist[-2]);
      mittelqtendenz = int(round(mittelq/10.0));
      if (mittelqtendenz == 0):
         pfadname = '90 Grad';
         epsliste[1] = eps_glatt;
         emodulliste[1] = e_modul_glatt;
      elif (mittelqtendenz > 0):
         pfadname = '180 Grad';
         epsliste[2] = eps_glatt;
         emodulliste[2] = e_modul_glatt;
      else:
         pfadname = '0 Grad';
         epsliste[0] = eps_glatt;
         emodulliste[0] = e_modul_glatt;
      #
      triax.update([('Spannungspfad', pfadname)]);
      daten.update([('Versuch ' + str(idx_triax+1), triax)]);
   #
   if (any([(tempeps is None) for tempeps in epsliste])):
      print('# Warnung: Es konnten nicht alle drei Spannungspfade erkannt werden');
      return False;
   #
   eps_som = _ErweiterteHypoParamHilfsfunktionEpssom(eps0=epsliste[0], eps180=epsliste[2],
      emodul0=emodulliste[0], emodul180=emodulliste[2]);
   # FIXME: Gueltigkeit des Rueckgabewerts pruefen
   #
   daten['Parameter'].update([('Parameter-Hilfen', ['m_T [-]', 'm_R [-]', 'R_max [-]', 'beta_r [-]', 'chi [-]'])]);
   daten['Parameter'].update([('eps_som [-]', eps_som)]);
   return True;
#
