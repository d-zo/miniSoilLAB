# -*- coding: utf-8 -*-
"""
__main__.py   v0.5 (2023-09)
"""

# Copyright 2020-2023 Dominik Zobel.
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


# Paketname muss explizit angegeben werden, wenn mit relativen Abhaengigkeiten gearbeitet wird.
# Diese sind wiederum fuer ein Laden der Bibliotheken aus einem zip-Archiv (.pyz) erforderlich
__package__ = 'miniSoilLAB'


# -------------------------------------------------------------------------------------------------
def main(argument):
    """Hauptfunktion zum Starten von miniSoilLAB.
    """
    import os
    from .konstanten import Standardpfad
    from .gui import GUIbasis

    print('Starte miniSoilLAB')

    if (len(argument) > 1):
        print('# Abbruch: Aufruf ohne Argument oder mit Pfad als Argument erwartet')
        return

    pfad = '.' + os.sep
    if (len(argument) == 1):
        pfad = argument[0] + os.sep

    print('# Vorlagenordner: ' + os.path.abspath(pfad))
    Standardpfad(pfad=pfad)
    gui = GUIbasis()
    gui.Vorbereiten()
    gui.Ausfuehren()



# -------------------------------------------------------------------------------------------------
import sys


if (sys.version_info[0] < 3):
    print('miniSoilLAB benötigt mindestens Python3')
else:
    if (__name__ == '__main__'):
        main(sys.argv[1:])
    else:
        main(sys.argv[1:])

