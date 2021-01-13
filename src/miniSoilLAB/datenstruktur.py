# -*- coding: utf-8 -*-
"""
datenstruktur.py   v0.1 (2019-09)
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
class Datenstruktur(dict):
   """Mini-Klasse zur Verwaltung von dict-Datenstrukturen mit angepasster Darstellung bei der
   Ausgabe (sortierte Schluessel, Unterstrukturen nicht automatisch aufklappen, Zeilenumbruch bei
   print-Befehlen).
   """
   def __init__(self, daten=None):
      if (daten is not None):
         self.update(daten);
   #
   def __repr__(self):
      return self.show(newline=False);
   #
   def __str__(self):
      return self.show(newline=True);
   #
   def show(self, newline=True):
      eintraege = [];
      max_eintraege = 6;
      for item in sorted(self.keys()):
         if isinstance(item, str):
            schluessel = '\'' + str(item) + '\'';
         else:
            schluessel = str(item);
         #
         aktueller_wert = self[item];
         if (isinstance(aktueller_wert, dict) or isinstance(aktueller_wert, Datenstruktur)):
            eintraege += [schluessel + ': {...}'];
         else:
            if isinstance(aktueller_wert, str):
               wert = '\'' + str(aktueller_wert) + '\'';
            elif (isinstance(aktueller_wert, list) or isinstance(aktueller_wert, tuple)):
               if (len(aktueller_wert) > max_eintraege):
                  wert = '[' + ', '.join([str(aktueller_wert[idx]) for idx in range(max_eintraege)]) + ', ...]';
               else:
                  wert = str(aktueller_wert);
            else:
               wert = str(aktueller_wert);
            #
            eintraege += [schluessel + ': ' + wert];
      #
      if (newline):
         return '{' + ',\n '.join(eintraege) + '}';
      else:
         return '{' + ', '.join(eintraege) + '}';
   #
   def keys(self):
      return sorted(super().keys());
   #
#
