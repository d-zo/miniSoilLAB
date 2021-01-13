# -*- coding: utf-8 -*-
"""
vorlagen.py   v0.2 (2020-09)
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
class VorlagenMuster(object):
   def __init__(self):
      self.vorlagen = dict();
   #
   def AusOrdnerEinlesen(self, ordner):
      from os import walk as os_walk
      from os import path as os_path
      from .konstanten import debugmodus
      from .dateneinlesen import _JSONDateiEinlesen
      #
      json_dateien = [];
      for pfad, _, dateiliste in os_walk(ordner):
         for dateiname in dateiliste:
            if (dateiname.endswith('.json')):
               json_dateien += [os_path.abspath(os_path.join(pfad, dateiname))];
      #
      if (json_dateien == []):
         print('# Warnung: Keine Vorlagen gefunden in ' + os_path.abspath(ordner));
      else:
         for dateiname in json_dateien:
            if (debugmodus):
               print('# Debug: Lese Vorlage(n) aus ' + os_path.basename(dateiname));
            #
            vorlage = _JSONDateiEinlesen(dateiname=dateiname, bezeichnung='Vorlage');
            if (vorlage is not None):
               for schluessel in vorlage.keys():
                  if (schluessel in self.vorlagen.keys()):
                     print('# Warnung: Vorlage ' + schluessel + ' ist mehr als einmal definiert - wird ueberschrieben');
               #
               self.vorlagen.update(vorlage);
   #
   def Schluessel(self):
      return sorted(self.vorlagen.keys());
   #
   def _TeilVorlage(self, schluessel, checks=True):
      erforderliche_seiten = dict();
      refvorlage = self.vorlagen[schluessel];
      for tabellenseite in refvorlage.keys():
         teildaten = {};
         if (checks):
            if ('[Checks]' in refvorlage[tabellenseite]):
               teildaten = refvorlage[tabellenseite]['[Checks]'];
         else:
            for feld in refvorlage[tabellenseite]:
               if (feld != '[Checks]'):
                  teildaten.update([(feld, refvorlage[tabellenseite][feld])]);
         #
         erforderliche_seiten.update([(tabellenseite, teildaten)]);
      #
      return erforderliche_seiten;
   #
   def Checks(self, schluessel):
      return self._TeilVorlage(schluessel, checks=True);
   #
   def Datenfelder(self, schluessel):
      return self._TeilVorlage(schluessel, checks=False);
   #
   def NameReferenzvorlage(self, name):
      """Der uebergebene name muss zu den intern verwendeten Referenznamen passen (bspw. Atterberg,
      Oedo-CRS, Triax-D, usw). Er endet immer auf einem Buchstaben [a-z], optional gefolgt von einem
      Binde- oder Unterstrich und eine oder mehrere Zahlen, um auf die Variante der Vorlage
      hinzuweisen. Diese Funktion entfernt die Variantenendung und gibt den restlichen Namen zurueck.
      Bei ungueltigem name wird eine Warnung ausgegeben und der unveraenderte name zurueckgegeben.
      """
      from .konstanten import gueltige_vorlagen
      #
      if (name is None):
         return None;
      #
      refname = name;
      while (True):
         if (len(refname) == 0):
            print('# Warnung: Ungueltige Bezeichnung fuer Vorlage');
            return name;
         #
         if ((refname[-1].isdigit()) or (refname[-1] == '-') or (refname[-1] == '_')):
            refname = refname[:-1];
         else:
            break;
      #
      if (refname in gueltige_vorlagen):
         return refname;
      else:
         print('# Warnung: Vorlage ' + refname + ' entspricht keiner gueltigen Vorlage');
         return name;
   #
   def Pruefen(self, workbook, tabellentyp):
      from .konstanten import debugmodus
      from .xlshilfen import VorhandeneTabellenseiten, EinzelEintragEinlesen
      from .xlshilfen import ZeileUndSpalteAusZellenbezeichnung
      #
      zielvorlage = None;
      verworfeneVorlagen = '';
      tabellenseiten = VorhandeneTabellenseiten(workbook=workbook, tabellentyp=tabellentyp);
      for schluessel in self.Schluessel():
         naechste_vorlage = False;
         ueberpruefungen = self.Checks(schluessel=schluessel);
         for seite in ueberpruefungen.keys():
            if (seite not in tabellenseiten):
               verworfeneVorlagen += '\n   ' + schluessel + ' verworfen, da Tabellenseite \'' \
                  + seite + '\' nicht vorhanden';
               # Wenn eine erforderliche Tabellenseite nicht vorhanden ist -> naechste Vorlage
               naechste_vorlage = True;
               break;
            #
            aktuelleseite = ueberpruefungen[seite];
            for pruefzelle in aktuelleseite.keys():
               zeile, spalte = ZeileUndSpalteAusZellenbezeichnung(zellenname=pruefzelle);
               eintrag = EinzelEintragEinlesen(workbook=workbook, tabellenname=seite, zeile=zeile,
                  spalte=spalte, name='_temp-' + seite + '-' + pruefzelle, tabellentyp=tabellentyp,
                  inhalt='text', warnen=False);
               if (eintrag is None):
                  # Leere Zellen nur akzeptieren, wenn explizit kein Inhalt gefordert ist
                  if (aktuelleseite[pruefzelle] == ''):
                     continue;
                  #
                  verworfeneVorlagen += '\n   ' + schluessel + ' verworfen, da Eintrag None != \'' \
                     + aktuelleseite[pruefzelle] + '\'';
                  # Wenn ein Wert nicht dem Pruefwert entspricht -> naechste Vorlage
                  naechste_vorlage = True;
                  break;
               #
               if (eintrag != aktuelleseite[pruefzelle]):
                  verworfeneVorlagen += '\n   ' + schluessel + ' verworfen, da Eintrag \'' \
                     + eintrag + '\' != \'' + aktuelleseite[pruefzelle] + '\'';
                  # Wenn ein Wert nicht dem Pruefwert entspricht -> naechste Vorlage
                  naechste_vorlage = True;
                  break;
            #
            if (naechste_vorlage):
               break;
         #
         if (naechste_vorlage):
            continue;
         #
         zielvorlage = schluessel;
         break;
      #
      if (debugmodus and (zielvorlage is None)):
         print('# Debug: [Checks] von keiner Vorlage erfuellt:' + verworfeneVorlagen);
      #
      return [zielvorlage, self.NameReferenzvorlage(name=zielvorlage)];
#


# -------------------------------------------------------------------------------------------------
def VorlagenstrukturZuDatenstruktur(vorlage, ebene=0):
   """Geht eine vorhandene Vorlagenstruktur durch, um daraus das Geruest fuer einen passenden
   Datensatz zu ermitteln. Dabei werden die Inhalte der Tabellenseiten (Hauptebene der Vorlage) in
   die Hauptebene der neuen Struktur eingefuegt. Alle [Checks] und deren Unterstrukturen werden
   ignoriert. Die Inhalte aller Datengruppen (d.h. alle anderen Eintraege, die mit [ beginnen)
   werden direkt in die Elterngruppe geschrieben.
   """
   from .datenstruktur import Datenstruktur
   #
   strukturebene = Datenstruktur();
   for schluessel in vorlage.keys():
      eintrag = vorlage[schluessel];
      if ((isinstance(eintrag, Datenstruktur)) or (isinstance(eintrag, dict))):
         if (schluessel == '[Checks]'):
            continue;
         elif ((schluessel.startswith('[')) or (ebene == 0)):
            strukturebene.update(VorlagenstrukturZuDatenstruktur(vorlage=eintrag, ebene=ebene+1));
         else:
            strukturebene.update([(schluessel, VorlagenstrukturZuDatenstruktur(vorlage=eintrag,
               ebene=ebene+1))]);
      #
      elif isinstance(eintrag, list):
         if (len(eintrag) == 1):
            strukturebene.update([(schluessel, '')]);
         else:
            strukturebene.update([(schluessel, [])]);
   #
   return strukturebene;
#
