# -*- coding: utf-8 -*-
"""
verarbeitung_oedocrl.py   v0.2 (2021-11)
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
def OedoCRLStruktur():
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
      }),
      'Laststufe 1': Datenstruktur({
         'Zeitwerte': [],
         'Setzung [mm]': [],
         'Laststufen [kN/m^2]': []
      }),
      'Laststufe 2': Datenstruktur({
         'Zeitwerte': [],
         'Setzung [mm]': [],
         'Laststufen [kN/m^2]': []
      })
   });
   return copy.deepcopy(struktur);
#


# -------------------------------------------------------------------------------------------------
def _KennwerteOedoCRL(daten, refwerte):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Oedo-CRL und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   from .datenstruktur import Datenstruktur
   from .verarbeitung_oedo import _KennwerteOedo
   from .verarbeitung_hilfen import ImportiertesDatumFormatieren, SekundenAusDatumsangabenExtrahieren
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
   from .parameterbestimmung import _ViskohypoplastischTangentenpunkte, _ViskohypoplastischCalphaUndIv
   #
   # Einstellbare Parameter fuer Oedometerversuche, falls keine Vorgaben existieren
   param_log_zu_sqrt = [1, 2];
   param_zwischenpunkte = 5;
   param_glaettungswert = 10;
   param_linearbereich = 0.1;
   #
   if (not _KennwerteOedo(daten=daten, refwerte=refwerte)):
      print('# Warnung: Berechnung der Oedo-Kennwerte zu Oedo-CRL fehlgeschlagen');
      return False;
   #
   anfangshoehe = daten['Hoehe [mm]'];
   durchmesser = daten['Durchmesser [mm]'];
   trockendichte = daten['Trockendichte [g/cm^3]'];
   erstbelastung = daten['Erstbelastung'];
   versuch1 = daten['Laststufe 1'];
   versuch2 = daten['Laststufe 2'];
   a, b, c = erstbelastung['Ausgleichs-Koeffizienten'];
   #
   # Extrahiere Uebergabewerte
   korndichte = refwerte['Korndichte [g/cm^3]'];
   #
   tol = 1e-6;
   # ----------------- Dat-Seiten mit CRL-Daten -----------------
   hs = anfangshoehe * trockendichte/korndichte;
   erfolgreich = [False for idx in range(1, 9)];
   for idx_last in range(8):
      seite = 'Laststufe ' + str(idx_last+1);
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
      mod_zeitwerte = [ImportiertesDatumFormatieren(datum=wert, ausgabeformat='%d.%m.%Y %H:%M:%S') for wert in zeitwerte];
      if (all([wert is not None for wert in mod_zeitwerte])):
         oedo.update([('Zeitwerte', mod_zeitwerte)]);
      #
      zeitpunkte = SekundenAusDatumsangabenExtrahieren(daten=zeitwerte,
         formatliste=['%d.%m.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']);
      if (zeitpunkte is None):
         continue;
      #
      stunden = [tempzeit/3600.0 for tempzeit in zeitpunkte];
      oedo.update([('Zeit [h]', stunden)]);
      #zeitstempel = [tempzeit.strftime('%d.%m.%Y %H:%M:%S') for tempzeit in stunden];
      #oedo.update([('Zeitstempel', zeitstempel)]);
      #
      hoehe = [anfangshoehe - setz for setz in setzung];
      oedo.update([('Hoehe [mm]', hoehe)]);
      porenzahl = [einzelhoehe/hs - 1.0 for einzelhoehe in hoehe];
      oedo.update([('Porenzahl [-]', porenzahl)]);
      #
      if (max(setzung) - setzung[0] < tol):
         print('# Warnung: Setzung fuer ' + seite + ' ungueltig');
         break;
      #
      spez_setzung = [100.0*(setz - setzung[0])/(max(setzung) - setzung[0]) for setz in setzung];
      oedo.update([('Setzung-spez [%]', spez_setzung)]);
      #
      einstellungen = GespeicherterWertOderUebergabe(daten=daten,
         bezeichnung='Einstellungen', uebergabe=Datenstruktur());
      #
      log_zu_sqrt = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Verhaeltnis Log/sqrt', uebergabe=param_log_zu_sqrt);
      zwischenpunkte = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Zwischenpunkte', uebergabe=param_zwischenpunkte);
      glaettungswert = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Glaettungswert', uebergabe=param_glaettungswert);
      linearbereich = GespeicherterWertOderUebergabe(daten=einstellungen,
         bezeichnung='Linearer Bereich', uebergabe=param_linearbereich);
      #
      parameter = GespeicherterWertOderUebergabe(daten=oedo,
         bezeichnung='Parameter', uebergabe=Datenstruktur());
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
         logschnittpunkt = None;
      #
      if (logschnittpunkt is None):
         print('# Warnung: Tangentenpunkte konnten nicht bestimmt werden bei ' + seite);
      else:
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
      erfolgreich[idx_last] = True;
   #
   # Mindestens die ersten beiden Seiten muessen erfolgreich bearbeitet worden sein
   if (erfolgreich[0] and erfolgreich[1]):
      return True;
   else:
      return False;
#


# -------------------------------------------------------------------------------------------------
def AlleLaststufen(daten):
   """Alle vorhandenen Laststufen der ausgewaehlten Referenzstruktur pruefen und in der
   Hauptstruktur von daten uebernehmen.
   """
   from .datenstruktur import Datenstruktur, DatenstrukturExtrahieren
   #
   for idx_last in range(2, 8):
      laststufe = 'Laststufe ' + str(idx_last+1);
      if (laststufe in daten[daten['_Refwahl']]):
         OedoCRLStruktur_mod = Datenstruktur({laststufe: OedoCRLStruktur()['Laststufe 1']});
         extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=OedoCRLStruktur_mod, refwahl=daten['_Refwahl']);
         if (extrahierte_daten):
            daten.update(extrahierte_daten);
      else:
         break;
#


# -------------------------------------------------------------------------------------------------
def KennwerteOedoCRL(daten, refwerte):
   """Erwartet eine JSON-Struktur daten, in der die Daten zu Oedo-CRL-Versuchen gespeichert sind
   und aktualisiert/berechnet die entsprechenden Kennwerte.
   """
   from .konstanten import debugmodus
   from .datenstruktur import DatenstrukturExtrahieren
   from .verarbeitung_hilfen import ZusatzdatenKopieren
   from .verarbeitung_oedo import AlleOedoBelastungsschritte
   #
   erfolgreich = False;
   #
   if ('_Refwahl' not in daten):
      if (debugmodus):
         print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001');
      #
      daten.update([('_Refwahl', '_Ref_001')]);
   #
   extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=OedoCRLStruktur(), refwahl=daten['_Refwahl']);
   if (extrahierte_daten):
      daten.update(extrahierte_daten);
      ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten);
      # Alle vorhandenen Belastungsschritte und Laststufen der ausgewaehlten Referenzstruktur beruecksichtigen
      AlleOedoBelastungsschritte(daten=daten, refwahl=daten['_Refwahl'], ziel=daten);
      AlleLaststufen(daten=daten);
      #
      _KennwerteOedoCRL(daten=daten, refwerte=refwerte);
      erfolgreich = True;
   #
   return erfolgreich;
#


# -------------------------------------------------------------------------------------------------
def VorbereitungOedoCRL(daten):
   """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Oedo-CRL-Versuchen
   gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
   eine spaetere Weiterverarbeitung zu haben.
   """
   import copy
   from math import pi
   from .datenstruktur import DictStrukturPruefenUndAngleichen, DictStrukturGleichOderTeilmenge
   from .datenstruktur import ZielgroesseFindenUndAktualisieren
   #
   testdaten = copy.deepcopy(daten);
   if (not DictStrukturPruefenUndAngleichen(ref_dict=OedoCRLStruktur(), test_dict=testdaten, warnung=False)):
      # Pruefe die folgenden Alternativgroessen und passe ggfs. die Einheiten an
      ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Trockenmasse mit Behaelter', einheit='g');
      ZielgroesseFindenUndAktualisieren(daten=testdaten, bezeichnung='Behaeltermasse', einheit='g');
      # Zielgroessen aus Alternativgroessen berechnen (falls erforderlich)
      try:
         durchmesser = testdaten['Durchmesser [mm]'];
      except KeyError as errormessage:
         print('# Warnung: Mindestens ein erforderlicher Wert in Oedo-CRL nicht vorhanden - ' + str(errormessage));
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
   # Die zusaetzlichen Laststufen pruefen
   for idx_last in range(6):
      seite = 'Laststufe ' + str(idx_last+3);
      if (seite not in testdaten):
         break;
      #
      laststufe = testdaten[seite];
      ZielgroesseFindenUndAktualisieren(daten=laststufe, bezeichnung='Setzung', einheit='mm');
      ZielgroesseFindenUndAktualisieren(daten=laststufe, bezeichnung='Laststufen', einheit='kN/m^2');
   #
   if (DictStrukturGleichOderTeilmenge(ref_dict=OedoCRLStruktur(), test_dict=testdaten, warnung=True)):
      # Referenz an daten zu den modifizierten Daten aendern
      daten.clear();
      daten.update(testdaten);
   else:
      print('# Warnung: Struktur der Oedo-CRL-Daten ist ungueltig');
#
