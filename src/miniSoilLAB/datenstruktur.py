# -*- coding: utf-8 -*-
"""
datenstruktur.py   v0.2 (2021-11)
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
class Datenstruktur(dict):
   """Mini-Klasse zur Verwaltung von dict-Datenstrukturen mit angepasster Darstellung bei der
   Ausgabe (sortierte Schluessel, Unterstrukturen nicht automatisch aufklappen, Zeilenumbruch bei
   print-Befehlen).
   """
   def __init__(self, daten=None):
      if (daten is not None):
         self.update(daten);
      #
      self.komplettausgabe = False;
      self.max_eintraege = 6;
   #
   def __repr__(self):
      return self.show(newline=False);
   #
   def __str__(self):
      return self.show(newline=True);
   #
   def show(self, newline=True, subdict=None):
      if (subdict is None):
         subdict = self;
      #
      eintraege = [];
      for item in subdict.keys():
         if isinstance(item, str):
            schluessel = '\'' + str(item) + '\'';
         else:
            schluessel = str(item);
         #
         aktueller_wert = subdict[item];
         if (isinstance(aktueller_wert, dict) or isinstance(aktueller_wert, Datenstruktur)):
            if (self.komplettausgabe):
               eintraege += [schluessel + ': ' + self.show(newline=newline, subdict=subdict[item])];
            else:
               eintraege += [schluessel + ': {...}'];
         else:
            if isinstance(aktueller_wert, str):
               wert = '\'' + str(aktueller_wert) + '\'';
            elif ((not self.komplettausgabe) and \
                  ((isinstance(aktueller_wert, list) or isinstance(aktueller_wert, tuple)))):
               if (len(aktueller_wert) > self.max_eintraege):
                  wert = '[' + ', '.join([str(aktueller_wert[idx]) for idx in range(self.max_eintraege)]) + ', ...]';
               else:
                  wert = str(aktueller_wert);
            else:
               wert = str(aktueller_wert);
            #
            eintraege += [schluessel + ': ' + wert];
      #
      if ((not self.komplettausgabe) and (newline)):
         return '{' + ',\n '.join(eintraege) + '}';
      else:
         return '{' + ', '.join(eintraege) + '}';
   #
   def keys(self):
      return sorted(super().keys());
   #
   def togglefull(self):
      self.komplettausgabe = not self.komplettausgabe;
#


# -------------------------------------------------------------------------------------------------
def DictStrukturGleichOderTeilmenge(ref_dict, test_dict, warnung=True):
   """Erwartet ein ref_dict (Referenz) und test_dict und vergleicht diese. Gibt True zurueck,
   falls jedes Element von ref_dict in test_dict vorkommt (ggfs. hat test_dict weitere
   Elemente), sonst False.
   """
   rueckgabe = True;
   for schluessel in ref_dict.keys():
      if (schluessel not in test_dict.keys()):
         if (warnung):
            print('# Warnung: Fehlender Eintrag in dict (' + schluessel + ')');
         #
         return False;
      else:
         if (isinstance(ref_dict[schluessel], dict)):
            rueckgabe = DictStrukturGleichOderTeilmenge(ref_dict=ref_dict[schluessel],
               test_dict=test_dict[schluessel], warnung=warnung);
      #
      if (rueckgabe == False):
         return False;
   #
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def DictStrukturPruefenUndAngleichen(ref_dict, test_dict, warnung=True):
   """Erwartet ein ref_dict (Referenz) und test_dict und vergleicht diese. Gibt True zurueck,
   falls jedes Element von ref_dict in test_dict vorkommt (ggfs. hat test_dict weitere
   Elemente), sonst False. Zusaetzlich wird test_dict modifiziert und die Werte entsprechend
   skaliert, falls sich gleiche Strukturen nur durch eine bekannte Einheit unterscheiden.
   """
   from .verarbeitung_hilfen import PraefixUmrechnungsfaktor
   #
   rueckgabe = True;
   for schluessel in ref_dict.keys():
      if (schluessel not in test_dict.keys()):
         if ('[' in schluessel):
            # Pruefen, ob der schluessel "Bezeichnung [Einheit]" entspricht
            gefunden = False;
            refbezeichnung = schluessel.split('[')[0];
            for testschluessel in list(test_dict.keys()):
               if (refbezeichnung in testschluessel):
                  gefunden = True;
                  break;
            #
            if (gefunden):
               faktor = PraefixUmrechnungsfaktor(von=testschluessel, zu=schluessel);
               if (faktor is not None):
                  zielwert = test_dict[testschluessel];
                  if (isinstance(zielwert, list)):
                     test_dict.update([(schluessel, [faktor*wert for wert in zielwert])]);
                  else:
                     test_dict.update([(schluessel, faktor*zielwert)]);
                  #
                  del test_dict[testschluessel];
                  continue;
         #
         if (warnung):
            print('# Warnung: Fehlender Eintrag in dict (' + schluessel + ')');
         #
         rueckgabe = False;
      else:
         if (isinstance(ref_dict[schluessel], dict)):
            temp_rueckgabe = DictStrukturPruefenUndAngleichen(ref_dict=ref_dict[schluessel],
               test_dict=test_dict[schluessel], warnung=warnung);
            # Falls die Rueckgabe noch True ist, uebernehme die Rueckgabe aus der Pruefung
            # der Unterstruktur. Falls sie bereits False ist, aendere nichts daran
            if (rueckgabe):
               rueckgabe = temp_rueckgabe;
   #
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def GleichartigesDictListenErgaenzen(altes_dict, neues_dict, skalar_zu_liste=True, listenlaenge=[]):
   """Erwartet ein altes_dict und neues_dict, das die gleiche Struktur (oder Untermenge davon)
   von altes_dict hat. Jeder (verschachtelte) Schluessel von neues_dict wird ueberprueft und um
   den dazugehoerigen Wert aus altes_dict ergaenzt. Skalare Werte werden ebenfalls nur einfach
   hinzugefuegt, falls listenlaenge leer ist oder in der gleichen Ebene kein gleichnamiger Eintrag
   existiert. Andernfalls wird die Laenge der groessten Liste der Eintraege von listenlaenge in
   der aktuellen Ebene fuer die Laenge (Wiederholungen) des aktuellen Werts verwendet. Gibt False
   zurueck und bricht ab, falls in neues_dict mindestens ein Schluessel nicht in altes_dict
   vorkommt, ansonsten True.
   
   Da beim Durchlauf neues_dict geaendert wird, sollte neues_dict nicht im Original an diese
   Funktion uebergeben werden! neues_dict sollte nur weiterverwendet werden, wenn diese Funktion
   True zurueck gibt.
   """
   rueckgabe = True;
   for schluessel in neues_dict.keys():
      if (schluessel not in altes_dict.keys()):
         print('# Warnung: Fehlender Eintrag in Referenz-dict (' + schluessel + ')');
         return False;
      else:
         if (isinstance(neues_dict[schluessel], dict)):
            rueckgabe = GleichartigesDictListenErgaenzen(altes_dict=altes_dict[schluessel],
               neues_dict=neues_dict[schluessel], skalar_zu_liste=skalar_zu_liste, listenlaenge=listenlaenge);
         else:
            if (not isinstance(neues_dict[schluessel], list)):
               ergaenzung = '';
               if (not skalar_zu_liste):
                  ergaenzung = ' (skalar_zu_liste ist False)';
               #
               print('# Warnung: Unterstruktur (' + schluessel + ') ist keine Liste' + ergaenzung);
               return False;
            #
            alter_eintrag = altes_dict[schluessel];
            if ((len(neues_dict[schluessel]) == 0) and (not skalar_zu_liste)):
               neues_dict.update([(schluessel, alter_eintrag)]);
            else:
               if (not isinstance(alter_eintrag, list)):
                  if (listenlaenge == []):
                     alter_eintrag = [alter_eintrag];
                  else:
                     max_laenge = 1;
                     for laengeneintrag in listenlaenge:
                        try:
                           temp_laenge = len(altes_dict[laengeneintrag]);
                           max_laenge = max(max_laenge, temp_laenge);
                        except:
                           pass;
                     #
                     alter_eintrag = [alter_eintrag for x in range(max_laenge)];
               #
               neues_dict.update([(schluessel, neues_dict[schluessel]+alter_eintrag)]);
      #
      if (rueckgabe == False):
         return False;
   #
   return rueckgabe;
#


# -------------------------------------------------------------------------------------------------
def DatenstrukturExtrahieren(daten, refstruktur, listenlaenge=[], refwahl=''):
   """Erwarte eine eingelesene Datenstruktur daten, die u.a. verschiedene _Ref_###-Eintraege mit
   Unterstrukturen und Listen enthaelt (bspw. Rohdaten). Anhand einer refstruktur werden
   namensgleiche Elemente aller _Ref_###-Strukturen in der Hauptebene von daten erstellt.
   Bei fehlerfreier Ausfuehrung wird die modifizierte Datenstruktur zurueckgegeben, anderenfalls
   False (daten bleibt unveraendert). Falls Eintraege in listenlaenge uebergeben werden, so wird 
   die Laenge von Listen an die Laenge der laengsten Liste in listenlaenge angepasst.
   """
   import datetime
   import copy
   #
   struktur_neu = copy.deepcopy(refstruktur);
   schluesselliste = list(daten.keys());
   fehlerfrei = True;
   for schluessel in schluesselliste:
      if (not schluessel.startswith('_Ref_')):
         continue;
      #
      if (schluessel == refwahl):
         if (not GleichartigesDictListenErgaenzen(altes_dict=daten[schluessel], neues_dict=struktur_neu,
            skalar_zu_liste=False, listenlaenge=listenlaenge)):
            fehlerfrei = False;
            break;
      elif (refwahl == ''):
         if (not GleichartigesDictListenErgaenzen(altes_dict=daten[schluessel], neues_dict=struktur_neu,
            skalar_zu_liste=True, listenlaenge=listenlaenge)):
            fehlerfrei = False;
            break;
   #
   if (not fehlerfrei):
      print('# Warnung: Datenstruktur aufgrund von Warnungen nicht aktualisiert');
      return False;
   else:
      struktur_neu.update([('Letzte Anpassung', datetime.date.today().strftime('%Y-%m-%d'))]);
      return struktur_neu;
#


# -------------------------------------------------------------------------------------------------
def ZielgroesseFindenUndAktualisieren(daten, bezeichnung, einheit):
   """Ueberpruefe die Eintraege in der ersten Ebene des dicts daten, ob sie den Eintrag
   "bezeichnung [einheit]" enthalten oder einen Eintrag mit der gleichen bezeichnung aber einer
   anderen Einheit. In diesem Fall werden die Werte des Eintrags in die uebergebene Einheit
   umgerechnet und daten aktualisiert. Gibt True zurueck, falls ein Eintrag mit der angegebenen
   bezeichnung existiert (ggfs. mit bekannter, umgerechneter Einheit) und False sonst.
   """
   startschluessel = None;
   zielschluessel = bezeichnung + ' [' + einheit + ']';
   faktor = None;
   identisch = False;
   for schluessel in list(daten.keys()):
      if (schluessel == zielschluessel):
         identisch = True;
         break;
      #
      elif (bezeichnung in schluessel):
         startschluessel = schluessel;
         faktor = PraefixUmrechnungsfaktor(von=startschluessel, zu=zielschluessel);
         break;
   #
   if (identisch):
      return True;
   elif (faktor is None):
      return False;
   else:
      startwert = daten[startschluessel];
      if (isinstance(startwert, list)):
         daten.update([(zielschluessel, [faktor*wert for wert in startwert])]);
      else:
         daten.update([(zielschluessel, faktor*startwert)]);
      #
      del daten[startschluessel];
      return True;
#


# -------------------------------------------------------------------------------------------------
def DatenGleicherSchluesselAllerUnterstrukturenEntfernen(daten, unterstrukturen, eintraege):
   """Erwartet eine Struktur daten, die die uebergebenen unterstrukturen enthalten koennen.
   In jeder Unterstruktur wird ueberprueft, ob einer der eintraege existiert und ggfs. entfernt.
   Alle so entfernten Teilstrukturen werden als neue Struktur zurueckgegeben.
   """
   entfernt = Datenstruktur();
   for eintrag in eintraege:
      if (all(eintrag in daten[struktur] for struktur in unterstrukturen)):
         # Eine beliebige Unterstruktur auswaehlen, da nur gemeinsame Schluessel verarbeitet werden
         schluesselliste = list(daten[unterstrukturen[0]][eintrag].keys());
         for schluessel in schluesselliste:
            if (all(schluessel in daten[struktur][eintrag] for struktur in unterstrukturen)):
               if (eintrag not in entfernt):
                  entfernt.update([(eintrag, Datenstruktur())]);
               #
               entfernt[eintrag].update([(schluessel, [daten[struktur][eintrag][schluessel] for struktur in unterstrukturen])]);
               for struktur in unterstrukturen:
                  # Eintrag aus allen Unterstrukturen loeschen
                  del daten[struktur][eintrag][schluessel];
         #
         for struktur in unterstrukturen:
            # Alle leeren Strukturen entfernen
            if (not daten[struktur][eintrag]):
               del daten[struktur][eintrag];
   #
   return entfernt;
#


# -------------------------------------------------------------------------------------------------
def EintraegeAusUnterstrukturenInHauptstruktur(daten, unterstrukturen, eintraege):
   """Erwartet eine Struktur daten, die die uebergebenen unterstrukturen enthalten koennen.
   In jeder Unterstruktur wird ueberprueft, ob einer der eintraege existiert und ggfs. zur
   Hauptstruktur verschoben, bspw. wird daten[unterstruktur][eintrag] zu daten[eintrag]
   veraendert. Veraendert die uebergebene Struktur daten.
   """
   extrahierte_strukturen = DatenGleicherSchluesselAllerUnterstrukturenEntfernen(daten=daten,
      unterstrukturen=unterstrukturen, eintraege=eintraege);
   for struktur in extrahierte_strukturen:
      if (struktur not in daten):
         daten.update([(struktur, extrahierte_strukturen[struktur])]);
      else:
         for schluessel in list(extrahierte_strukturen[struktur].keys()):
            daten[struktur].update([(schluessel, extrahierte_strukturen[struktur][schluessel])]);
#


# -------------------------------------------------------------------------------------------------
def EintraegeEntfernen(mod_struktur, entfernen_start=[]):
   """Erwartet eine Datenstruktur mod_struktur, die durch diese Funktion veraendert werden kann.
   Alle Schluessel in der Struktur (und Unterstrukturen) werden geprueft und entfernt, ob deren
   Name mit einem Ausdruck aus entfernen_start beginnt. In diesem Fall werden der Schluessel und
   Wert aus mod_struktur geloescht. Gibt nichts zurueck, da mod_struktur bereits alle Aenderungen
   enthaelt.
   """
   entfernen = [];
   for schluessel, wert in mod_struktur.items():
      if any([schluessel.startswith(x) for x in entfernen_start]):
         entfernen += [schluessel];
      #
      if (isinstance(wert, dict)):
         EintraegeEntfernen(mod_struktur=wert, entfernen_start=entfernen_start);
   #
   for schluessel in entfernen:
      del mod_struktur[schluessel];
#
