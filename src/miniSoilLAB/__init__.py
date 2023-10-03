# -*- coding: utf-8 -*-
"""
                                                    v0.6.0
        _      _    __      _  _  .--.       ..    .----.
       (_)    (_).´ __|    (_)| | |  |      /  `   |     `
 _ _ _  _ _ _  _ . (    __  _ | | |  |     '    '  |  ()  |
| ' ` `| | ' `| |`. `. ´  `| || | |  |    /  /`  ` |     <
| .. . | | .. | |  `  ' () | || | |  |    ' '--' ' |  ()  |
| || | | | || | |_.´  .    | |. '.|   --./  .--.  `|      /
|_||_|_|_|_||_|_|___.´ \__,|_| \_,`_____'__/    `__.___.-'

                                          D.Zobel 2019-2021

Programm zur Aufbereitung von geotechnischen Laborversuchen
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


from .rohdatenverarbeitung import *
from .vorlagen import *
from .xlshilfen import *
from .plotausgabe import *
from .kennwerte import *
from .parameterbestimmung import *
from .rohdaten import *
from .dateneinlesen import *
from .datenstruktur import *
from .gleichungsloeser import *
from .konstanten import *

__author__ = 'Dominik Zobel';
__version__ = '0.6.0';
__package__ = 'miniSoilLAB';
