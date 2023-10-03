# -*- coding: utf-8 -*-
"""
guihilfen.py   v0.4 (2021-06)
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
def FensterZentrieren(hauptfenster, fenster):
   """Bestimme die Groessen von hauptfenster und fenster und zentriere das fenster mittig in
   Relation zum hauptfenster.
   """
   hauptfenster.update_idletasks();
   haupt_x = hauptfenster.winfo_x();
   haupt_y = hauptfenster.winfo_y();
   haupt_breite = hauptfenster.winfo_width();
   haupt_hoehe = hauptfenster.winfo_height();
   fenster_breite = fenster.winfo_reqwidth();
   fenster_hoehe = fenster.winfo_reqheight();
   posx = int(haupt_x + (haupt_breite - fenster_breite)/2.0);
   posy = int(haupt_y + (haupt_hoehe - fenster_hoehe)/2.0);
   fenster.geometry('+{}+{}'.format(posx, posy));
# 


# -------------------------------------------------------------------------------------------------
def _Autoscrollfunktion(event):
   event.widget.master.configure(scrollregion=event.widget.master.bbox('all'),
      width=event.widget.breite, height=event.widget.hoehe);
#


# -------------------------------------------------------------------------------------------------
def _Radscrollfunktion(event, canvas, scrollbar):
   # Windows/Linux Scroll events
   delta = 0;
   if ((event.num == 4) or (event.delta == 120)):
      delta = -1;
   #
   if ((event.num == 5) or (event.delta == -120)):
      delta = 1;
   if (len(scrollbar.state()) == 0):
      # oder Zustand mit != 'disabled' pruefen
      canvas.yview_scroll(delta, 'units');
#
