# -*- coding: utf-8 -*-
"""
verarbeitung_oedo.py   v0.2 (2021-11)
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
def OedoStruktur():
   #
   import copy
   from .datenstruktur import Datenstruktur
   #
   struktur = Datenstruktur({
      'Hoehe [mm]': [],
      'Durchmesser [mm]': [],
      'Trockenmasse [g]': [],
      'Erstbelastung': Datenstruktur({
         'Setzung [mm]': [],
         'Spannung [kN/m^2]': []
      })
   });
   return copy.deepcopy(struktur);
#


# -------------------------------------------------------------------------------------------------
def _KennwerteOedo(daten, refwerte):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   from math import pi, log
   from .konstanten import g
   from .datenstruktur import Datenstruktur
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
   from .gleichungsloeser import LoeseGleichung, LetzterIndexMitWertKleinerAls
   #
   # Einstellbare Parameter fuer Oedometerversuche, falls keine Vorgaben existieren
   param_max_it = 500;
   param_puffergroesse = 0.95;
   param_spannungsgrenzen = [10, 1000];
   param_intervallgrenzen = [5, 16];
   #
   oedo_gewichtsplatten = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]; # [kg]
   oedo_gewichte_kopfplatte = [0.36324, 0.4649, 1.1]; # [kg]
   oedo_hebel = 10.0;
   #
   anfangshoehe = daten['Hoehe [mm]'];
   durchmesser = daten['Durchmesser [mm]'];
   trockenmasse = daten['Trockenmasse [g]'];
   #
   # Extrahiere Uebergabewerte
   korndichte = refwerte['Korndichte [g/cm^3]'];
   #
   tol = 1e-6;
   # --------------------------- Tab1 ---------------------------
   volumen_e = anfangshoehe * pi*(durchmesser/2.0)**2 / 1000.0; # [cm^3]
   daten.update([('Volumen [cm^3]', volumen_e)]);
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
   #
   porenzahl_anfang = korndichte/trockendichte - 1.0;
   druckflaeche = pi*(durchmesser/2000.0)**2; # [m^2]
   #
   hatKopfplattendaten = False;
   try:
      kopfplatte = daten['Kopfplatte'];
      refgewicht = kopfplatte['Last-ref [kg]'];
      refspannung = kopfplatte['Spannung-ref [kN/m^2]'];
      hatKopfplattendaten = True;
   except:
      pass;
   #
   if (hatKopfplattendaten):
      abgeleitetes_gewicht_kopfplatte = 1000.0*refspannung*druckflaeche/g - oedo_hebel*refgewicht;
      gewicht_kopfplatte = None;
      for ref_gewicht in oedo_gewichte_kopfplatte:
         if (abs(abgeleitetes_gewicht_kopfplatte - ref_gewicht) < 1e-3):
            gewicht_kopfplatte = ref_gewicht;
            break;
      #
      if (gewicht_kopfplatte is None):
         print('# Hinweis: Gewicht der Oedometer-Kopfplatte unterscheidet sich von den Referenzgewichten');
         gewicht_kopfplatte = abgeleitetes_gewicht_kopfplatte;
      #
      kopfplatte.update([('Gewicht [kg]', gewicht_kopfplatte)]);
      #
      oedo_sumgewicht = [sum(oedo_gewichtsplatten[0:idx_aktuell]) for idx_aktuell in range(len(oedo_gewichtsplatten))];
      oedo_spannungen = [(gewicht*oedo_hebel + gewicht_kopfplatte)*g/1000.0/druckflaeche for gewicht in oedo_sumgewicht]; # [kN/m^2]
      daten.update([('Spannung-neuberechnet [kN/m^2]', oedo_spannungen)]);
   #
   for belastungsart in ['Erstbelastung', 'Entlastung', 'Wiederbelastung']:
      if (belastungsart in daten):
         belastung = daten[belastungsart];
      else:
         break;
      #
      try:
         setzung = belastung['Setzung [mm]'];
         spannung = belastung['Spannung [kN/m^2]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens ein erforderlicher Wert aus ' + belastungsart + \
            ' fuer Oedo nicht vorhanden - ' + str(errormessage));
         return False;
      #
      if (any([(abs(tempsetzung - anfangshoehe) < tol) for tempsetzung in setzung])):
         print('# Warnung: Setzung erreicht Probenhoehe bei ' + belastungsart);
         continue;
      #
      # FIXME: Richtig? (siehe auch oedo-crs)
      #porenzahl = [porenzahl_anfang - tempsetzung/100.0 * (1.0 + porenzahl_anfang) for tempsetzung in setzung];
      porenzahl = [(anfangshoehe - (tempsetzung-setzung[0]))/anfangshoehe * (porenzahl_anfang + 1.0) - 1.0 for tempsetzung in setzung];
      dehnung = [log(anfangshoehe/(anfangshoehe - tempsetzung)) for tempsetzung in setzung];
      #
      belastung.update([('Porenzahl [-]', porenzahl)]);
      belastung.update([('Dehnung-axial [-]', dehnung)]);
      #
      einstellungen = GespeicherterWertOderUebergabe(daten=daten,
         bezeichnung='Einstellungen', uebergabe=Datenstruktur());
      #
      max_it = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Iterationen-max', uebergabe=param_max_it);
      puffergroesse = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Puffergroesse', uebergabe=param_puffergroesse);
      spannungsgrenzen = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Spannungsgrenzen', uebergabe=param_spannungsgrenzen);
      intervallgrenzen = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Intervallgrenzen', uebergabe=param_intervallgrenzen);
      custom_tol = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Toleranz', uebergabe=tol);
      #
      spannungsgrenzen = [max(min(spannung), spannungsgrenzen[0]), min(max(spannung), spannungsgrenzen[1])];
      einstellungen.update([('Spannungsgrenzen', spannungsgrenzen)]);
      xmin = LetzterIndexMitWertKleinerAls(liste=spannung, grenzwert=spannungsgrenzen[0]);
      if (xmin is None):
         xmin = 0;
      #
      xmax = LetzterIndexMitWertKleinerAls(liste=spannung, grenzwert=spannungsgrenzen[1]);
      if (xmax-xmin == 0):
         print('# Warnung: Zu wenig Werte zur Bestimmung der Ausgleichs-Koeffizienten bei ' + belastungsart);
         continue;
      #
      intervall = [2.0**idx for idx in range(*intervallgrenzen)];
      a, b, c = LoeseGleichung(gleichung='y = a*ln(x+b)+c', x=spannung[xmin:xmax], y=dehnung[xmin:xmax],
         intervall=intervall, max_it=max_it, puffergroesse=puffergroesse, tol=custom_tol);
      if (a is None):
         continue;
      #
      belastung.update([('Ausgleichs-Koeffizienten', [a, b, c])]);
      if (abs(a) < custom_tol):
         print('# Warnung: Erster Ausgleichs-Koeffizient bei ' + belastungsart + ' annaehernd Null');
         continue;
      #
      steifemodul = [(tempspannung + b) / a/1000.0 for tempspannung in spannung];
      belastung.update([('Steifemodul [kN/m^2]', steifemodul)]);
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def AlleOedoBelastungsschritte(daten, refwahl, ziel):
   """Fuege alle vorhandenen Belastungsschritte der ausgewaehlten Referenzdaten zum tatsaechlichen
   Datensatz hinzu.
   """
   from .datenstruktur import Datenstruktur, DatenstrukturExtrahieren
   #
   for belastungsart in ['Entlastung', 'Wiederbelastung']:
      if (belastungsart in daten[refwahl]):
         OedoStruktur_mod = Datenstruktur({belastungsart: OedoStruktur()['Erstbelastung']});
         extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=OedoStruktur_mod, refwahl=refwahl);
         if (extrahierte_daten):
            ziel.update(extrahierte_daten);
      else:
         break;
#


# -------------------------------------------------------------------------------------------------
def LagerungsdichtenOedoBestimmen(daten, refwerte, grenzen_min=[-0.1, 0.55], grenzen_max=[0.7, 1.2]):
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
   oedo_locker = [];
   oedo_dicht = [];
   #
   # Fuer Oedometerversuche sind die Angaben zur Trockendichte optional
   try:
      refdichten = [refwerte[x] for x in ['Trockendichte-min [g/cm^3]', 'Trockendichte-max [g/cm^3]']];
   except:
      print('# Hinweis: Keine Einstufung der Oedometerversuche aufgrund fehlender Angaben zur Trockendichte (typischerweise aus LoDi)');
      return [[], []];
   #
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
         hoehe = daten[schluessel]['Hoehe [mm]'];
         durchmesser = daten[schluessel]['Durchmesser [mm]'];
         trockenmasse = daten[schluessel]['Trockenmasse [g]'];
         #
         volumen = pi*(durchmesser/10.0/2.0)**2 * hoehe/10.0;
         trockendichte = trockenmasse/volumen;
      except:
         print('# Debug: Abbruch wegen fehlender Werte');
         continue;
      #
      if ((trockendichte > bereich_locker[0]) and (trockendichte < bereich_locker[1])):
         oedo_locker += [schluessel];
      elif ((trockendichte > bereich_dicht[0]) and (trockendichte < bereich_dicht[1])):
         oedo_dicht += [schluessel];
      elif (debugmodus):
         print('# Debug: Oedometerversuch ' + schluessel + ' nicht erfolgreich als locker/dicht eingestuft');
         print(str((trockendichte-refdichten[0])/dichte_bereich));
   #
   return [oedo_locker, oedo_dicht];
#


# -------------------------------------------------------------------------------------------------
def KennwerteOedo(daten, refwerte):
   """Erwartet eine JSON-Struktur daten, in der die Daten zu Oedometerversuchen gespeichert sind
   und aktualisiert/berechnet die entsprechenden Kennwerte.
   """
   from .konstanten import debugmodus
   from .datenstruktur import Datenstruktur, DatenstrukturExtrahieren
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe, ZusatzdatenKopieren
   #
   oedo_locker, oedo_dicht = LagerungsdichtenOedoBestimmen(daten=daten, refwerte=refwerte);
   for variante, kandidaten in [('locker', oedo_locker), ('dicht', oedo_dicht)]:
      erfolgreich = False;
      if (kandidaten == []):
         if (debugmodus):
            print('# Hinweis: Keine kandidaten fuer Oedo-' + variante);
         #
         continue;
      #
      oedo_variante = GespeicherterWertOderUebergabe(daten=daten,
         bezeichnung='Oedo-' + variante, uebergabe=Datenstruktur());
      #
      auswahl = kandidaten[0];
      if ('_Refwahl' not in oedo_variante):
         if (debugmodus):
            print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme ' + kandidaten[0]);
         #
      else:
         if (oedo_variante['_Refwahl'] not in kandidaten):
            print('# Warnung: Angegebene Referenzdaten ' + auswahl + ' ungueltig, nehme ' + kandidaten[0]);
         else:
            auswahl = oedo_variante['_Refwahl'];
      #
      oedo_variante.update([('_Refwahl', auswahl)]);
      #
      extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=OedoStruktur(),
         refwahl=oedo_variante['_Refwahl']);
      if (extrahierte_daten):
         oedo_variante.update(extrahierte_daten);
         ZusatzdatenKopieren(quelle=daten[oedo_variante['_Refwahl']], ziel=oedo_variante);
         # Alle vorhandenen Belastungsschritte der ausgewaehlten Referenzstruktur beruecksichtigen
         AlleOedoBelastungsschritte(daten=daten, refwahl=oedo_variante['_Refwahl'], ziel=oedo_variante);
         erfolgreich = _KennwerteOedo(daten=oedo_variante, refwerte=refwerte);
      #
      if (not erfolgreich):
         return False;
   #
   return erfolgreich;
#


# -------------------------------------------------------------------------------------------------
def VorbereitungOedo(daten):
   """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Oedometerversuchen
   gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
   eine spaetere Weiterverarbeitung zu haben.
   """
   import copy
   from math import pi
   from .datenstruktur import DictStrukturPruefenUndAngleichen, DictStrukturGleichOderTeilmenge
   from .datenstruktur import ZielgroesseFindenUndAktualisieren
   #
   testdaten = copy.deepcopy(daten);
   if (not DictStrukturPruefenUndAngleichen(ref_dict=OedoStruktur(), test_dict=testdaten, warnung=False)):
      # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
      ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Trockenmasse mit Behaelter', einheit='g');
      ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Behaeltermasse', einheit='g');
      # Zielgroessen aus Alternativgroessen berechnen (falls erforderlich)
      try:
         durchmesser = testdaten['Durchmesser [mm]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens ein erforderlicher Wert in Oedo nicht vorhanden - ' + str(errormessage));
         return;
      #
      try:
         gesamttrockenmasse = testdaten['Trockenmasse mit Behaelter [g]'];
         behaeltermasse = testdaten['Behaeltermasse [g]'];
         testdaten.update([('Trockenmasse [g]', gesamttrockenmasse - behaeltermasse)]);
      except:
         pass;
      #
      for belastungsart in ['Erstbelastung', 'Entlastung', 'Wiederbelastung']:
         try:
            belastung = testdaten[belastungsart];
         except:
            break;
         #
         # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
         ZielgroesseFindenUndAktualisieren(daten=belastung, bezeichnung='Kraft', einheit='kN');
         ZielgroesseFindenUndAktualisieren(daten=belastung, bezeichnung='Weg', einheit='mm');
         try:
            setzung = belastung['Weg [mm]'];
            kraft = belastung['Kraft [kN]'];
            druckflaeche = pi*(durchmesser/2000.0)**2; # [m^2]
            belastung.update([('Setzung [mm]', setzung)]);
            belastung.update([('Spannung [kN/m^2]', [einzelkraft/druckflaeche for einzelkraft in kraft])]);
            del belastung['Weg [mm]'];
            del belastung['Kraft [kN]'];
         except:
            pass;
   #
   if (DictStrukturGleichOderTeilmenge(ref_dict=OedoStruktur(), test_dict=testdaten, warnung=True)):
      # Referenz an daten zu den modifizierten Daten aendern
      daten.clear();
      daten.update(testdaten);
   else:
      print('# Warnung: Struktur der Oedo-Daten ist ungueltig');
#
