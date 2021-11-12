# -*- coding: utf-8 -*-
"""
konstanten.py   v0.4 (2019-11)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with miniSoilLAB. If not, see <http://www.gnu.org/licenses/>.


pi = 3.1415926535897932;
grad2rad = pi/180.0;
g = 9.81; # [m/s^2]
korndichte = 2.65; # [g/cm^3]
oedo_gewichtsplatten = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]; # [kg]
oedo_gewichte_kopfplatte = [0.36324, 0.4649, 1.1]; # [kg]
oedo_hebel = 10.0;
gueltige_vorlagen = ['Atterberg', 'Auswertung-Hypoplastisch', 'LoDi', 'Oedo', 'Oedo-CRL', 'Oedo-CRS',
   'Oedo-CRS-Visko', 'Triax-CU', 'Triax-D', 'Triax-p-q'];
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
def Standardpfad(pfad='./Vorlagen'):
   """Setze den Pfad zum Hauptverzeichnis von miniSoilLAB, um bspw. Vorlagen korrekt einladen zu
   koennen.
   """
   import os
   #
   global basispfad;
   basispfad = pfad;
   #
   if ((not pfad.endswith(os.sep)) and (not pfad.endswith('/'))):
      basispfad += os.sep;
#
