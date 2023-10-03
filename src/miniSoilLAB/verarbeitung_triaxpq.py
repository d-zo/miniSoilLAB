# -*- coding: utf-8 -*-
"""
verarbeitung_triaxpq.py   v0.2 (2021-11)
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
def TriaxpqStruktur():
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
      '5-p-q-Pfad': Datenstruktur({
         'Segment 2': Datenstruktur({
            'Porenwasserdruck [kN/m^2]': [],
            'Druck-isotrop-eff [kN/m^2]': [],
            'Hauptspannungsdifferenz [kN/m^2]': []
         }),
         'Segment 4': Datenstruktur({
            'Porenwasserdruck [kN/m^2]': [],
            'Druck-isotrop-eff [kN/m^2]': [],
            'Hauptspannungsdifferenz [kN/m^2]': []
         })
      }),
      'Versuch 1': Datenstruktur({
         'Stage': [],
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Porenwasservolumen [mm^3]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': []
      }),
      'Versuch 2': Datenstruktur({
         'Stage': [],
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Porenwasservolumen [mm^3]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': []
      }),
      'Versuch 3': Datenstruktur({
         'Stage': [],
         'Radialdruck [kN/m^2]': [],
         'Porenwasserdruck [kN/m^2]': [],
         'Porenwasservolumen [mm^3]': [],
         'Axialkraft [kN]': [],
         'Stauchung [mm]': []
      })
   });
   return copy.deepcopy(struktur);
#


# -------------------------------------------------------------------------------------------------
def _KennwerteTriaxpq(daten, refwerte, typ):
   """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Triax-p-q und
   speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben entspricht.
   """
   from .datenstruktur import Datenstruktur
   from .verarbeitung_hilfen import GespeicherterWertOderUebergabe
   from .verarbeitung_triax import _KennwerteTriaxVersuchstabelle
   from .parameterbestimmung import _ErweiterteHypoParamHilfsfunktion, _ErweiterteHypoParamHilfsfunktionEpssom
   #
   if (not _KennwerteTriaxVersuchstabelle(daten=daten, refwerte=refwerte, typ=typ)):
      print('# Warnung: Bestimmung der Kennwerte fehlgeschlagen');
      return False;
   #
   # Einstellbare Parameter fuer Triax-p-q-Versuche, falls keine Vorgaben existieren
   param_offset = 0;# Standardmaessig wird kein Offset verwendet
   param_glaettungswert = 10;
   param_refspanne = 3;
   #
   konsolidation = daten['3-Konsolidation'];
   hoehe_k = konsolidation['Hoehe [mm]'];
   volumen_k = konsolidation['Volumen [cm^3]'];
   #
   tol = 1e-6;
   #
   epsliste = [None, None, None];
   emodulliste = [None, None, None];
   for idx_triax, triax_versuch in enumerate(['Versuch 1', 'Versuch 2', 'Versuch 3']):
      try:
         triax = daten[triax_versuch];
      except KeyError as errormessage:
         print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage));
         continue;
      #
      stage = triax['Stage'];
      porenwasservolumen = triax['Porenwasservolumen [mm^3]'];
      radialdruck = triax['Radialdruck [kN/m^2]'];
      porenwasserdruck = triax['Porenwasserdruck [kN/m^2]'];
      # Bei p-q-Pfaden sind bei Axialkraft und Stauchung auch negative Bereiche erlaubt
      axialkraft = triax['Axialkraft [kN]'];
      stauchung = triax['Stauchung [mm]'];
      #
      numdaten = len(stage);
      kraft = [einzel_axialkraft-axialkraft[0] for einzel_axialkraft in axialkraft];
      dehnung = [(einzel_stauchung-stauchung[0])/hoehe_k[idx_triax] for einzel_stauchung in stauchung];
      delta_volumen = [(vol-porenwasservolumen[0])/1000.0 for vol in porenwasservolumen];
      #
      if (any([(abs(hoehe_k[idx_triax] - tempstauchung) < tol) for tempstauchung in stauchung])):
         print('# Warnung: Stauchung entspricht annaehernd der Hoehe der konsolidierten Probe');
         continue;
      #
      flaeche = [1000.0*(volumen_k[idx_triax]+delta_volumen[idx])/(hoehe_k[idx_triax]-stauchung[idx]) for idx in range(numdaten)];
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
      geglaettet = GespeicherterWertOderUebergabe(daten=triax, bezeichnung='Glaettung',
         uebergabe=Datenstruktur());
      einstellungen = GespeicherterWertOderUebergabe(daten=geglaettet, bezeichnung='Einstellungen',
         uebergabe=Datenstruktur());
      #      
      offset = GespeicherterWertOderUebergabe(daten=einstellungen, bezeichnung='Startoffset',
         uebergabe=param_offset);
      glaettungswert = GespeicherterWertOderUebergabe(daten=einstellungen, bezeichnung='Glaettungspunkte',
         uebergabe=param_glaettungswert);
      refspanne = GespeicherterWertOderUebergabe(daten=einstellungen, bezeichnung='Referenzspanne',
         uebergabe=param_refspanne);
      #
      startidx = stage_idxlist[-1]+offset;
      if (startidx > len(stauchung)-1):
         print('# Warnung: Index fuer Stage und Offset liegt hinter der Grenze des Vektors');
         continue;
      #
      eps = [(einzelstauchung-stauchung[startidx])/(hoehe_k[idx_triax]-stauchung[startidx]) for einzelstauchung in stauchung[startidx:]];
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
   parameter = GespeicherterWertOderUebergabe(daten=daten, bezeichnung='Parameter',
         uebergabe=Datenstruktur());
   parameter.update([('eps_som [-]', eps_som)]);
   return True;
#


# -------------------------------------------------------------------------------------------------
def KennwerteTriaxpq(daten, refwerte):
   """Erwartet eine JSON-Struktur daten, in der die Daten zu Triax-p-q-Versuchen gespeichert sind
   und aktualisiert/berechnet die entsprechenden Kennwerte.
   """
   from .konstanten import debugmodus
   from .datenstruktur import DatenstrukturExtrahieren
   from .verarbeitung_hilfen import ZusatzdatenKopieren
   #
   erfolgreich = False;
   #
   if ('_Refwahl' not in daten):
      if (debugmodus):
         print('# Hinweis: Keine Referenzdaten mit _Refwahl ausgewaehlt, nehme _Ref_001');
      #
      daten.update([('_Refwahl', '_Ref_001')]);
   #
   extrahierte_daten = DatenstrukturExtrahieren(daten=daten, refstruktur=TriaxpqStruktur(), refwahl=daten['_Refwahl']);
   if (extrahierte_daten):
      daten.update(extrahierte_daten);
      ZusatzdatenKopieren(quelle=daten[daten['_Refwahl']], ziel=daten);
      _KennwerteTriaxpq(daten=daten, refwerte=refwerte, typ='Triax-p-q');
      erfolgreich = True;
   #
   return erfolgreich;
#


# -------------------------------------------------------------------------------------------------
def VorbereitungTriaxpq(daten):
   """Erwartet eine eingelesene JSON-Struktur daten, in der die Daten zu Triax-p-q-Versuchen
   gespeichert sind. Die uebergebene Struktur wird modifiziert, um eine einheitliche Struktur fuer
   eine spaetere Weiterverarbeitung zu haben.
   """
   import copy
   from math import pi
   from .datenstruktur import DictStrukturPruefenUndAngleichen, ZielgroesseFindenUndAktualisieren
   #
   testdaten = copy.deepcopy(daten);
   if (DictStrukturPruefenUndAngleichen(ref_dict=TriaxpqStruktur(), test_dict=testdaten, warnung=True)):
      # Referenz an daten zu den modifizierten Daten aendern
      daten.clear();
      daten.update(testdaten);
   else:
      print('# Warnung: Struktur der Triax-p-q-Daten ist ungueltig');
#
