# -*- coding: utf-8 -*-
"""
konstanten.py   v0.5 (2021-06)
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


from math import pi

g = 9.81; # [m/s^2]
grad2rad = pi/180.0;
# Die Liste der gueltigen Vorlagen ist sortiert, so dass keine Abhaengigkeiten einer Vorlage
# selbst aufgelistet sind. Umgekehrt werden aber nicht alle Eintraege vor einer Vorlage fuer
# die Berechnung von Kennwerten der Vorlage benoetigt
gueltige_vorlagen = ['KVS', 'Korndichte', 'Atterberg', 'Auswertung-Hypoplastisch', 'LoDi',
   'Oedo', 'Oedo-CRL', 'Oedo-CRS', 'Oedo-CRS-Visko', 'Triax-CU', 'Triax-D', 'Triax-p-q'];
debugmodus = False;
basispfad = './Vorlagen';


# -------------------------------------------------------------------------------------------------
def DebugAnAus():
   """Hilfsfunktion, um global den Zustand des Debug-Modus zu wechseln. Standardmaessig ist der
   Debug-Modus deaktivert und durch Aktivierung werden zahlreiche Debugausgaben erzeugt.
   """
   global debugmodus;
   debugmodus = not debugmodus;
#


# -------------------------------------------------------------------------------------------------
def Standardpfad(pfad='.'):
   """Setze den Pfad zum Hauptverzeichnis von miniSoilLAB, in dem ein Ordner namens Vorlagen
   erwartet wird (in dem die Vorlagen aller relevanten Strukturen gespeichert sind).
   """
   import os
   #
   global basispfad;
   #
   if (pfad.endswith(os.sep)):
      pfad = pfad[:-1];
   #
   basispfad = pfad + os.sep + 'Vorlagen' + os.sep;
#
