# -*- coding: utf-8 -*-
"""
dateneinlesen.py   v0.5 (2020-12)
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
def ExistiertDatei(dateiname):
   """Pruefe die Existenz einer Datei. Gibt True zurueck, falls die Datei vorhanden ist.
   """
   from pathlib import Path
   #
   testdatei = Path(dateiname);
   if (testdatei.is_file()):
      return True;
   else:
      return False;
#


# -------------------------------------------------------------------------------------------------
def BodenmusterdateiEinlesen(dateiname):
   """Liest den Inhalt einer Bodenmuster-Datei (dateiname) ein, die in jeder Zeile durch Semikolons
   getrennt die drei Eintraege Bodenname, Dateimuster und Zielordner enthaelt.
   Gibt ein dict mit den Bodennamen als Schluessel zurueck, das fuer jeden Bodennamen die
   Eintraege Dateimuster und Zielordner enthaelt.
   """
   eintraege = dict();
   zeile = 0;
   idx_leseversuch = 0;
   max_leseversuche = 5;
   try:
      with open(dateiname, 'r', encoding='utf-8') as eingabe:
         zeile += 1;
         for zeile in eingabe:
            if (len(zeile) == 0):
               continue;
            #
            if ((zeile == '\n') or (zeile == '\r\n')):
               continue;
            #
            if (zeile[0] == '#'):
               continue;
            #
            einzelteile = zeile.split(';');
            if (len(einzelteile) != 3):
               idx_leseversuch += 1;
               print('# Warnung: Die folgende Zeile hat nicht genau 2 Semikolons und wird ignoriert:');
               print(zeile);
               #
               if (idx_leseversuch == max_leseversuche):
                  print('# Fehler: Zuviele ungueltige Zeilen - Breche Lesevorgang ab');
                  break;
               #
               continue;
            #
            schluessel = einzelteile[0].strip();
            if (schluessel in eintraege.keys()):
               print('# Warnung: Eintrag in Zeile ' + str(zeile) + ' wird ignoriert (Bodenname ' + schluessel + ' bereits eingelesen)');
               continue;
            #
            eintraege.update([(schluessel, [einzelteile[1].strip(), einzelteile[2].strip()])]);
   except FileNotFoundError:
      print('# Fehler: Bodenmuster-Datei konnte nicht gefunden/geoeffnet werden');
   except:
      print('# Fehler: Bodenmuster-Datei konnte nicht eingelesen werden');
   #
   return eintraege;
#


# -------------------------------------------------------------------------------------------------
def BodendatenMitSchluesselAusMusterEinlesen(muster, schluessel=None, ignoriere=['rohdaten', '.dta',
   '.eax', '.gds', '.tvc']):
   """Lese alle Dateien der Boeden ein, die in muster hinterlegt sind (falls schluessel=None),
   oder nur diejenigen, die als Liste an schluessel uebergeben worden sind. Die Werte der Schluessel
   in muster entsprechen dem dateimuster und dem zielordner fuer den jeweiligen Bodennamen. Es
   werden alle Dateien ignoriert, in deren Namen sich ein in ignoriere definierter Begriff befindet.
   """
   from .datenstruktur import Datenstruktur
   #
   if (schluessel is None):
      schluessel = muster.keys();
   #
   bodendaten = Datenstruktur();
   for bodenname in schluessel:
      try:
         dateimuster, zielordner = muster[bodenname];
      except:
         print('# Warnung: ' + bodenname + ' ist kein gueltiger Schluessel fuer die uebergebenen Muster');
         continue;
      #
      tempboden = BodendatenEinlesen(bodenname=bodenname, dateimuster=dateimuster,
         zielordner=zielordner, ignoriere=ignoriere);
      if (tempboden is None):
         print('# Warnung: Boden ' + bodenname + ' ungueltig (Pfad/Muster korrekt?)');
         continue;
      #
      bodendaten.update(tempboden);
   #
   return bodendaten;
#


# -------------------------------------------------------------------------------------------------
def BodendatenEinlesen(bodenname, dateimuster, zielordner, ignoriere=['rohdaten', '.dta', '.eax',
   '.gds', '.tvc']):
   """Lese alle Dateien aus dem zielordner ein, die dateimuster enthalten. Speichere die
   eingelesenen Datein in einer Struktur mit dem Schluessel bodenname und gib diese zurueck.
   Es werden alle Dateien ignoriert, in deren Namen sich ein in ignoriere definierter Begriff
   befindet.
   """
   import os
   from .datenstruktur import Datenstruktur
   #
   if (zielordner[-1] == os.sep):
      zielordner = zielordner[:-1];
   #
   zieldateiliste = ZieldateienFinden(zielordner=zielordner, dateimuster=dateimuster);
   if (zieldateiliste == []):
      return None;
   #
   print('# --- Lese Dateien zu: ' + bodenname);
   bodendaten = Datenstruktur();
   for dateiname in zieldateiliste:
      for bezeichnung in ignoriere:
         if (bezeichnung in dateiname.lower()):
            continue;
      #
      eingelesen = DateiEinlesen(dateiname=dateiname)
      if (eingelesen is not None):
         if (len(eingelesen.keys()) == 0):
            print('# Hinweis: Keine Daten aus aktueller Datei eingelesen');
            continue;
         #
         if (len(eingelesen.keys()) > 1):
            print('# Hinweis: Mehrere Schluessel in einer Datei nicht unterstuetzt - ignoriere Eintraege');
            continue;
         #
         bezugsname = eingelesen.keys()[0];
         if (bezugsname in bodendaten.keys()):
            print('# Warnung: ' + bezugsname + ' existiert bereits und wird ueberschrieben');
            del bodendaten[bezugsname];
         #
         bodendaten.update(eingelesen);
   #
   if (len(bodendaten.keys()) == 0):
      return None;
   #
   bodendaten.update([('Basisordner', zielordner)]);
   #
   boden = Datenstruktur();
   boden.update([(bodenname, bodendaten)]);
   print('# Hinweis: ' + bodenname + ' aus Dateien eingelesen');
   print('# ---');
   return boden;
#


# -------------------------------------------------------------------------------------------------
def DateiEinlesen(dateiname):
   """Lese die Datei namens dateiname ein, sofern es sich um einen unterstuetzten Dateityp/-namen
   handelt.
   """
   from .xlshilfen import LeseXLSDaten
   from .rohdaten import LeseDTADaten, LeseEAXDaten, LeseGDSDaten, LeseTVCDaten, LeseKVSDaten
   #
   if ((dateiname[-3:].lower() == 'xls') or (dateiname[-4:].lower() == 'xlsx')):
      # Wird in Funktion ausgegeben
      #print('#  - LeseXLS: ' + dateiname);
      return LeseXLSDaten(dateiname=dateiname);
   elif (dateiname[-3:].lower() == 'dta'):
      print('# - LeseDTA: ' + dateiname);
      return LeseDTADaten(dateiname=dateiname);
   elif (dateiname[-3:].lower() == 'eax'):
      print('# - LeseEAX: ' + dateiname);
      return LeseEAXDaten(dateiname=dateiname);
   elif (dateiname[-3:].lower() == 'gds'):
      print('# - LeseGDS: ' + dateiname);
      return LeseGDSDaten(dateiname=dateiname);
   elif (dateiname[-3:].lower() == 'tvc'):
      print('# - LeseTVC: ' + dateiname);
      return LeseTVCDaten(dateiname=dateiname);
   elif (dateiname[-3:].lower() == 'kvs'):
      print('# - LeseKVS: ' + dateiname);
      return LeseKVSDaten(dateiname=dateiname);
   else:
      #print('# Hinweis: Ignoriere ' + dateiname);
      return None;
#


# -------------------------------------------------------------------------------------------------
def ZieldateienFinden(zielordner, dateimuster, ignoriereOrdnernamen=['alt']):
   """Ermittle im zielordner und allen Unterordnern alle Dateien, deren Namen dateimuster enthaelt.
   Falls ignoriereOrdnernamen keine leere Liste ist, werden alle Unterordner in der Liste ignoriert
   (deren Name einem der Eintraege entspricht).
   Gibt eine Liste aller Dateinamen der so ausgewaehlten Dateien zurueck.
   
   Kann auch zum Testen von Bodenmusterdatei-Eintraegen verwendet werden. Wenn Pfad und regulaerer
   Ausdruck richtig gewaehlt sind, sollten exakt die gewuenschten Dateien aufgelistet/eingelesen
   werden. Fuer die Wahl von sinnvollen regulaeren Ausdrucken sei auf das Python-Modul re und
   die offizielle Dokumentation verwiesen (Standard Library Reference unter https://docs.python.org)
   """
   from os import walk as os_walk
   from os import sep as os_sep
   from os.path import join as os_join
   from re import compile as re_compile
   from re import search as re_search
   #
   if ((dateimuster == '*') or (dateimuster == '*.*')):
      dateimuster = '';
   #
   if (zielordner == ''):
      zielordner = '.';
   #
   if (zielordner[-1] != os_sep):
      zielordner += os_sep;
   #
   remuster = re_compile(dateimuster);
   zieldateiliste = [];
   for (pfad, _, dateiliste) in os_walk(zielordner):
      # Ignoriere alle Dateien aus (Unter-)ordner eines Eintrags aus ignoriereOrdnernamen
      unterpfad = pfad[len(zielordner):].split(os_sep);
      if (any([pfadteil in ignoriereOrdnernamen for pfadteil in unterpfad])):
         continue;
      #
      for datei in dateiliste:
         if (re_search(remuster, datei)):
            zieldateiliste += [os_join(pfad, datei)];
   #
   if (len(zieldateiliste) > 0):
      zieldateiliste.sort();
   #
   return zieldateiliste;
#


# -------------------------------------------------------------------------------------------------
def DatensatzEinlesen(dateiname):
   """Lade eine JSON-formatierte Datei, die mit Datensatz_Speichern erstellt worden ist. Gib die
   eingelesene Struktur zurueck.
   """
   return _JSONDateiEinlesen(dateiname, bezeichnung='Datensatz');
#


# -------------------------------------------------------------------------------------------------
def _JSONDateiEinlesen(dateiname, bezeichnung='Datei'):
   """Lade eine JSON-formatierte Datei und gib die eingelesene Struktur zurueck.
   """
   import json
   #
   def Eingabedaten_json(json_objekt):
      """Hilfsfunktion zur Umwandlung von unterstuetzten Strukturen beim Einlesen von
      JSON-formatierten Dateien.
      """
      from .datenstruktur import Datenstruktur
      #
      if (isinstance(json_objekt, dict)):
         return Datenstruktur(json_objekt);
      else:
         return json_objekt;
   #
   eingelesen = None;
   try:
      with open(dateiname, 'r', encoding='utf-8') as eingabe:
         eingelesen = json.load(eingabe, object_hook=Eingabedaten_json);
   except FileNotFoundError:
      print('# Fehler: Datei konnte nicht gefunden/geoeffnet werden');
   except:
      print('# Fehler: ' + bezeichnung + ' konnte nicht eingelesen werden');
   #
   return eingelesen;
#


# -------------------------------------------------------------------------------------------------
def DatensatzSpeichern(datensatz, dateiname):
   """Speichere die Stuktur datensatz als JSON-formatierte Datei namens dateiname.
   """
   import json
   #
   class DatenstrukturEncoder(json.JSONEncoder):
      """Einfacher Encoder fuer Objekte der Datenstruktur-Klasse. Kovertiert Datenstruktur-Elemente
      in dicts und schreibt alle Listeneintraege in eine Zeile.
      """
      def default(self, o):
         return o.__dict__;
      #
      def iterencode(self, eintrag, _one_shot=False):
         listenstufe = 0;
         for dumpstring in super().iterencode(eintrag, _one_shot=_one_shot):
            if (dumpstring[0] =='['):
               listenstufe += 1;
               dumpstring = ''.join([teil.strip() for teil in dumpstring.split('\n')]);
            #
            elif (listenstufe > 0):
               dumpstring = ' '.join([teil.strip() for teil in dumpstring.split('\n')]);
               if (dumpstring == ' '):
                  continue;
               #
               if (dumpstring[-1] == ','):
                  dumpstring = dumpstring[:-1] + self.item_separator;
               elif (dumpstring[-1] == ':'):
                  dumpstring = dumpstring[:-1] + self.key_separator;
            #
            if (dumpstring[-1] == ']'):
               listenstufe -= 1;
            #
            yield dumpstring;
   #
   with open(dateiname, 'w') as ausgabe:
      json.dump(datensatz, ausgabe, cls=DatenstrukturEncoder, indent=1);
#
