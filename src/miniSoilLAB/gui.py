# -*- coding: utf-8 -*-
"""
gui.py   v0.9 (2020-12)
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


import tkinter
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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


# -------------------------------------------------------------------------------------------------
class GUIbasis(object):
   def __init__(self):
      from .guistil import GUIFarben
      #
      self.tkroot = tkinter.Tk();
      self.tkroot.title('miniSoilLAB');
      #
      self.icondata = 'R0lGODlhIAAgAMZ0ALQAALQBAbMGBrYICDAwMLcKCjExMTIyMrIODrgODrIQELgPD7ISErETE7EUFLoVFboWFrsXF7sYGLEcHLwaGrAeHrwcHL0dHb4hIb4jI78lJb8mJr8nJ68tLcAqKsErK8IwMMIxMa05OcMzM8M0NK07O6w8PMU6OqtFRcY+PshDQ8lHR6pRUcpLS6lbW8xSUs1UVM1VVc5YWM5ZWc9cXNBeXqdqatJmZqV1daV3d9Nra9RtbaR/f9VxcaSCgth5eaSIiNh6eth8fKKOjtqCgtuEhNuGhqCYmNyHh6GZmaGcnN2Li6Cfn6CgoN+RkeCWluGamuKcnOKenuOfn+OgoOOhoeSiouWlpeiwsOixsemzs+q4uOy9vezAwO7Fxe/IyPDMzPHPz/LU1PPV1fPW1vPX1/TZ2fXc3PXd3fbf3/jn5/jo6Pns7Prt7frv7/vy8vz09P34+P35+f/+/v///////////////////////////////////////////////yH5BAEKAH8ALAAAAAAgACAAAAf+gH+Cg4SFhoeIiYqLjI2Oj4sEB5OTBpSVlweWlwaHBmx0oaKjpKWhngsYM1BpTaSuo7CiTZ5zZVM0EhNFZ7Ovr56jc147ES1cpqbBsXRxUR4pPr+xnq5N1tZMUAoocdd03+HLyXRuMSRo5MtyVjUdNEhgc+B0ThRj9NSGBnRwJypScFTpwcHDkyOhrlAgIysUrX10zBQI8iWOqC4wHiyRQ4eKhjellon5AUJAiBlCpmyxMSJDFjo3RADbh42OEh5XWJRYUYHBAAAOLAQYAs7aOHKh2uhIgCUkRGZQQ2lBEEVfIX5RHZICsoHIrKNIR635gEQU2Ib5fKm5sAVctaI4cMPV/JajAZyHV8MilWGEztlpvkKRgZDkb9a0dF64AKuXVJgLhgNLDmXirdy4c+dC2sy5s2dFgQAAOw==';
      self.tkroot.tk.call('wm', 'iconphoto', self.tkroot._w, tkinter.PhotoImage(data=self.icondata));
      #
      self.menubreite = 400;
      self.plotbreite = 800;
      self.plotextrabreite = 700;
      self.hoehe = 800;
      self.tkroot.geometry('{}x{}'.format(self.menubreite+self.plotbreite, self.hoehe));
      self.tkroot.resizable(False, False);
      #
      self.menucanvas = None;
      self.font_param = ('Helvetica', '-12');
      #
      self.tabs = None;
      self.auswahlliste = ();
      self.boden = None;
      self.bodenname = ''; # als StringVar mit get() auf den Inhalt zugreifen
      self.plotcmd = ''; # als StringVar mit get() auf den Inhalt zugreifen
      self.plotcmdidx = 0;
      self.plotcmdliste = [''];
      #
      self.figure = None;
      self.zeichnung = None;
      self.plotname = '';
      self.zeitstempel = None;
      #
      self.zwischenspeicher_dateieinlesen = ['Material', '', '.'];
      self.zwischenspeicher_bodenmustereinlesen = ['.'];
      self.zwischenspeicher_datensatz = ['.', '.'];
      #
      self.hypoparam = [];
      self.erwhypoparam = [];
      self.viskohypoparam = [];
      #
      self.ignoriertedaten = ['rohdaten', '.dta', '.eax', '.gds', '.tvc'];
      #
      self.farben = GUIFarben();
   #
   def _Beenden(self, event=None):
      """GUI-Hauptprogramm beenden
      """
      self.tkroot.destroy();
   #
   def _Debugmodus(self):
      from .konstanten import DebugAnAus
      #
      DebugAnAus();
   #
   def _Rohdaten(self):
      if (len(self.ignoriertedaten) == 0):
         self.ignoriertedaten = ['rohdaten', '.dta', '.eax', '.gds', '.tvc'];
      else:
         self.ignoriertedaten = [];
   #
   def _PlotBefehlEintragen(self, event):
      self.plotcmdidx = len(self.plotcmdliste)-1;
      if (self.plotcmd.get() == ''):
         return;
      #
      self.plotcmdliste[-1] = self.plotcmd.get();
      self.plotcmdliste += [''];
      self.plotcmdidx += 1;
      self.plotcmd.set('');
   #
   def _LetzterPlotBefehl(self, event):
      if (self.plotcmdidx > 0):
         self.plotcmdidx -= 1;
         self.plotcmd.set(str(self.plotcmdliste[self.plotcmdidx]));
   #
   def _NaechsterPlotBefehl(self, event):
      if (self.plotcmdidx < len(self.plotcmdliste)-1):
         self.plotcmdidx += 1;
         self.plotcmd.set(str(self.plotcmdliste[self.plotcmdidx]));
   #
   def _PlotbefehlWeiterleiten(self, event):
      if ((self.plotcmd.get() == '') or (self.bodenname.get() == '')):
         # Keine Nachrichten ausgeben
         return;
      #
      self._PlotbefehlInterpretieren(plotbefehl=self.plotcmd.get());
      self._PlotBefehlEintragen(event);
      self.plotcmd.set('');
   #
   def _PlotbefehlInterpretieren(self, plotbefehl):
      from .plotausgabe import VordefiniertePlots, VordefinierteMultiPlots
      #
      self.figure.clear();
      plotbefehl_klein = plotbefehl.lower();
      if (('sieblinie' in plotbefehl_klein) or ('kvs' in plotbefehl_klein) or ('kornverteilung' in plotbefehl_klein)):
         self.tkroot.geometry('{}x{}'.format(self.menubreite+self.plotbreite+self.plotextrabreite, self.hoehe));
      else:
         self.tkroot.geometry('{}x{}'.format(self.menubreite+self.plotbreite, self.hoehe));
      #
      self.plotname = 'plot';
      # FIXME: Doppelt implementiert (hier und in VordefiniertePlots)
      for kurzform in ['oedo-crs-visko', 'oedo-crs', 'oedo-crl', 'oedo', 'triax-d', 'triax-cu',
         'triax-p-q', 'kvs', 'kornverteilung', 'sieblinie']:
         if (kurzform in plotbefehl_klein):
            self.plotname = kurzform;
            break;
      #
      if (plotbefehl_klein[:5] == 'alle:'):
         VordefinierteMultiPlots(boden=self.boden, plotname=plotbefehl[5:], figure=self.figure);
      else:
         VordefiniertePlots(boden=self.boden[self.bodenname.get()], plotname=plotbefehl, figure=self.figure);
      #
      # FIXME: Keine schoene Loesung, um die Auswahl temporaer aufzuheben
      if (self.tabs['KVS'].master.currenthighlight is not None):
         self.tabs['KVS'].master.currenthighlight.master.master.Unhighlight();
         self.tabs['KVS'].master.currenthighlight = None;
      #
      self.figure.canvas.draw();
   #
   def _PlotAlsPdfSpeichern(self, event=None):
      if ((self.figure is None) or (self.bodenname.get() == '')):
         messagebox.showwarning(title='pdf speichern', message='Kein Boden/Figure zum Speichern aktiv');
         return;
      #
      dateiname = self.zeitstempel + '-' + self.plotname + '.pdf';
      zieldatei = filedialog.asksaveasfilename(title='Plot als pdf speichern', initialfile=dateiname,
         defaultextension='.pdf');
      if (zieldatei != ''):
         self.figure.savefig(zieldatei);
   #
   def _PlotAlsPngSpeichern(self, event=None):
      if ((self.figure is None) or (self.bodenname.get() == '')):
         messagebox.showwarning(title='png speichern', message='Kein Boden/Figure zum Speichern aktiv');
         return;
      #
      dateiname = self.zeitstempel + '-' + self.plotname + '.png';
      zieldatei = filedialog.asksaveasfilename(title='Plot als png speichern', initialfile=dateiname,
         defaultextension='.pdf');
      if (zieldatei != ''):
         self.figure.savefig(zieldatei);
   #
   def _BodenlisteAktualisieren(self):
      """Aktualisiere das OptionMenu.
      """
      self.auswahlliste['menu'].delete(0, 'end');
      if (self.boden is None):
         self.auswahlliste['menu'].add_command(label='');
         if (self.figure is not None):
            self.figure.clear();
            self.zeichnung.draw();
      else:
         for eintrag in self.boden.keys():
            self.auswahlliste['menu'].add_command(label=eintrag,
               command=lambda name=eintrag: self._TabsAktualisieren(name));
         #
         if (len(self.boden.keys()) > 0):
            tempbodenname = self.bodenname.get();
            if ((tempbodenname != '') and (tempbodenname in self.boden.keys())):
               pass;
            else:
               # Waehle den ersten Schluessel (alphabetisch) aus
               schluessel = list(self.boden.keys());
               schluessel.sort();
               self._TabsAktualisieren(schluessel[0]);
               if (self.figure is not None):
                  self.figure.clear();
                  self.zeichnung.draw();
            #
            return;
      #
      self._TabsAktualisieren();
   #
   def _HypoplastischeParameterBerechnen(self, refelem, refunten, refoben):
      from .konstanten import grad2rad
      from .parameterbestimmung import HypoplastischeParameterFuerBoden
      #
      for kindelem in refelem.winfo_children():
         kindelem.destroy();
      #
      try:
         spannung_unten = float(refunten);
         spannung_oben = float(refoben);
      except:
         tkinter.Label(refelem, text='Referenzspannungen ungültig', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         return;
      #
      # Pruefe, ob alle relevanten Dateien eingelesen worden sind
      boden = self.boden[self.bodenname.get()];
      # Erst in HypoplastischeParameterFuerBoden bewerten, ob alles vorhanden ist -> Anzeige?
      #if (not (('Auswertung-Hypoplastisch' in boden) and ('LoDi' in boden) and ('Oedo-CRS' in boden)
      #   and ('Triax-D-locker' in boden) and ('Triax-D-dicht' in boden))):
      if ('Auswertung-Hypoplastisch' not in boden):
         tkinter.Label(refelem, text='Notwendige Dateien fehlen', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      self.hypoparam = HypoplastischeParameterFuerBoden(boden=boden,
            referenzspannungen=[spannung_unten, spannung_oben]);
      if (self.hypoparam == []):
         tkinter.Label(refelem, text='Berechnung fehlgeschlagen', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      self.hypoparam[0] = self.hypoparam[0]/grad2rad;
      boden['Auswertung-Hypoplastisch']['Parameter'].update([('Parameter-miniSoilLAB', self.hypoparam)]);
      paramnames = ['phi_c [Grad]', 'h_s [MPa]', 'n [-]', 'e_d [-]', 'e_c [-]', 'e_i [-]', 'alpha [-]', 'beta [-]'];
      runden =     [1e1,            1e0,         1e3,     1e3,       1e3,       1e3,       1e3,         1e3];
      for idx in range(len(self.hypoparam)):
         tkinter.Label(refelem, text=paramnames[idx] + ':', background=self.farben.farbe_bg_subitem,
            font=self.font_param, foreground=self.farben.farbe_fg, width=15,
            anchor='e').grid(row=idx, column=0, padx=(30, 0));
         tkinter.Label(refelem, text=str(round(runden[idx]*self.hypoparam[idx])/runden[idx]),
            background=self.farben.farbe_bg_subitem, foreground=self.farben.farbe_fg,
            font=self.font_param, width=10, anchor='w').grid(row=idx, column=1, padx=5);
      #
      self.tkroot.update_idletasks();
   #
   def _ErwHypoplastischeParameterBerechnen(self, refelem, offset, glaettungswert, refspanne):
      from .parameterbestimmung import ErweiterteHypoplastischeParameterFuerBoden
      #
      for kindelem in refelem.winfo_children():
         kindelem.destroy();
      #
      try:
         offset = int(offset);
         glaettungswert = int(glaettungswert);
         refspanne = int(refspanne);
      except:
         tkinter.Label(refelem, text='Ungültige Eingabewerte', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      # Pruefe, ob alle relevanten Dateien eingelesen worden sind
      boden = self.boden[self.bodenname.get()];
      if ('Triax-p-q' not in boden):
         tkinter.Label(refelem, text='Notwendige Dateien fehlen', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      self.erwhypoparam = ErweiterteHypoplastischeParameterFuerBoden(boden=boden, offset=offset,
         glaettungswert=glaettungswert, refspanne=refspanne);
      if (self.erwhypoparam == []):
         tkinter.Label(refelem, text='Berechnung fehlgeschlagen', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      boden['Triax-p-q']['Parameter'].update([('Parameter-miniSoilLAB', self.erwhypoparam)]);
      paramnames = ['m_T [-]', 'm_R [-]', 'R_max [-]', 'beta_r [-]', 'chi [-]'];
      runden =     [1e2,       1e2,       1e6,         1e2,          1e2];
      for idx in range(len(self.erwhypoparam)):
         tkinter.Label(refelem, text=paramnames[idx] + ':', background=self.farben.farbe_bg_subitem,
            font=self.font_param, foreground=self.farben.farbe_fg, width=15,
            anchor='e').grid(row=idx, column=0, padx=(30, 0));
         tkinter.Label(refelem, text=str(round(runden[idx]*self.erwhypoparam[idx])/runden[idx]),
            background=self.farben.farbe_bg_subitem, foreground=self.farben.farbe_fg,
            font=self.font_param, width=10, anchor='w').grid(row=idx, column=1, padx=5);
      #
      self.tkroot.update_idletasks();
   #
   def _ViskohypoplastischeParameterBerechnen(self, refelem, intervalllokalext, p1logverhaeltnis,
      p5logverhaeltnis, interpzwischenpunkte):
      from .konstanten import grad2rad
      from .parameterbestimmung import ViskohypoplastischeParameterFuerBoden
      #
      for kindelem in refelem.winfo_children():
         kindelem.destroy();
      #
      try:
         intervalllokalext = int(intervalllokalext);
         p1logverhaeltnis = float(p1logverhaeltnis);
         p5logverhaeltnis = float(p5logverhaeltnis);
         interpzwischenpunkte = int(interpzwischenpunkte);
      except:
         tkinter.Label(refelem, text='Ungültige Eingabewerte', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      # Pruefe, ob alle relevanten Dateien eingelesen worden sind
      boden = self.boden[self.bodenname.get()];
      if (('Triax-CU' not in boden) or ('Oedo-CRL' not in boden) or ('Oedo-CRS-Visko' not in boden)):
         tkinter.Label(refelem, text='Notwendige Dateien fehlen', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      self.viskohypoparam = ViskohypoplastischeParameterFuerBoden(boden=boden,
         intervallgroesse=intervalllokalext, p1logverhaeltnis=p1logverhaeltnis,
         p5logverhaeltnis=p5logverhaeltnis, zwischenpunkte=interpzwischenpunkte);
      if (self.viskohypoparam == []):
         tkinter.Label(refelem, text='Berechnung fehlgeschlagen', font=self.font_param,
            foreground='#aa0000', background=self.farben.farbe_bg_subitem).grid(row=0, column=0);
         self.tkroot.update_idletasks();
         return;
      #
      boden['Oedo-CRS-Visko']['Parameter'].update([('Parameter-miniSoilLAB', self.viskohypoparam)]);
      paramnames = ['e100 [-]', 'lambda [-]', 'kappa [-]', 'beta_x [-]', 'I_v [-]', 'D_r [-]', 'OCR [-]'];
      runden =     [1e3,         1e3,         1e3,         1e3,          1e3,       1e8,       1e2];
      for idx in range(len(self.viskohypoparam)):
         tkinter.Label(refelem, text=paramnames[idx] + ':', background=self.farben.farbe_bg_subitem,
            font=self.font_param, foreground=self.farben.farbe_fg, width=15,
            anchor='e').grid(row=idx, column=0, padx=(30, 0));
         tkinter.Label(refelem, text=str(round(runden[idx]*self.viskohypoparam[idx])/runden[idx]),
            background=self.farben.farbe_bg_subitem, foreground=self.farben.farbe_fg,
            font=self.font_param, width=10, anchor='w').grid(row=idx, column=1, padx=5);
      #
      self.tkroot.update_idletasks();
   #
   def _TabsAktualisieren(self, bodenname=''):
      # Alte Unterelemente entfernen
      for schluessel in self.tabs.keys():
         self.tabs[schluessel].AlleEintraegeEntfernen();
      #
      self.menucanvas.yview_moveto(0);
      if (bodenname == ''):
         return;
      #
      # Zaehler fuer unterschiedliche Ergebnisse in einem Tab
      idx_oedo = -1;
      idx_triax = -1;
      idx_auswertung = -1;
      self.bodenname.set(bodenname);
      try:
         refordner = self.boden[bodenname]['Basisordner'];
      except:
         refordner = '';
      #
      num_refzeichen = len(refordner) + 1;
      if (num_refzeichen == 1):
         num_refzeichen = 0;
      #
      if ('Kornverteilung' in self.boden[bodenname]):
         try:
            dateiname = self.boden[bodenname]['Kornverteilung']['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         try:
            self.tabs['KVS'].NeuerEintrag(text=dateiname);
            for idx_sieb in range(8):
               siebname = 'Sieblinie ' + str(idx_sieb);
               if (siebname not in self.boden[bodenname]['Kornverteilung'].keys()):
                  break;
               #
               refsiebung = self.boden[bodenname]['Kornverteilung'][siebname];
               self.tabs['KVS'].NeuerEintrag(text=siebname);
               self.tabs['KVS'].NeuerEintrag(text='Bodenart: ' + refsiebung['Bodenart']);
               self.tabs['KVS'].NeuerEintrag(text='Entnahmestelle: ' + refsiebung['Entnahmestelle']);
            #
            self.tabs['KVS'].NeuerEintrag(text='Plot KVS', command=lambda: self._PlotbefehlInterpretieren('Sieblinie'));
         except:
            self.tabs['KVS'].AlleEintraegeEntfernen();
            self.tabs['KVS'].NeuerEintrag(text=dateiname);
            self.tabs['KVS'].NeuerEintrag(text='Fehlerhafte/Ungueltige Eintraege');
      #
      if ('LoDi' in self.boden[bodenname]):
         lodi = self.boden[bodenname]['LoDi'];
         try:
            dateiname = lodi['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         try:
            self.tabs['LoDi'].NeuerEintrag(text=dateiname);
            if (lodi['Status'] != 'Einlesen erfolgreich'):
               self.tabs['LoDi'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
            #
            self.tabs['LoDi'].NeuerEintrag(text='Bodenart: ' + lodi['Bodenart']);
            self.tabs['LoDi'].NeuerEintrag(text='Entnahmestelle: ' + lodi['Bodenname']);
            self.tabs['LoDi'].NeuerEintrag(text='Trockendichte-min [g/cm^3]: ' + str(round(1e3*lodi['Lockerste-Lagerung']['Trockendichte-min [g/cm^3]'])/1e3));
            self.tabs['LoDi'].NeuerEintrag(text='Trockendichte-max [g/cm^3]: ' + str(round(1e3*lodi['Dichteste-Lagerung']['Trockendichte-max [g/cm^3]'])/1e3));
            self.tabs['LoDi'].NeuerEintrag(text='Porenzahl-min [-]: ' + str(round(1e3*lodi['Dichteste-Lagerung']['Porenzahl-min [-]'])/1e3));
            self.tabs['LoDi'].NeuerEintrag(text='Porenzahl-max [-]: ' + str(round(1e3*lodi['Lockerste-Lagerung']['Porenzahl-max [-]'])/1e3));
         except:
            self.tabs['LoDi'].AlleEintraegeEntfernen();
            self.tabs['LoDi'].NeuerEintrag(text=dateiname);
            self.tabs['LoDi'].NeuerEintrag(text='Fehlerhafte/Ungueltige Eintraege');
      #
      if ('Atterberg' in self.boden[bodenname]):
         atterberg = self.boden[bodenname]['Atterberg'];
         try:
            dateiname = atterberg['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         try:
            self.tabs['LoDi'].NeuerEintrag(text=dateiname);
            if (atterberg['Status'] != 'Einlesen erfolgreich'):
               self.tabs['LoDi'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
            #
            self.tabs['LoDi'].NeuerEintrag(text='Fließgrenze [%]: ' + str(round(1e2*atterberg['Fliessgrenze [%]'])/1e2));
            self.tabs['LoDi'].NeuerEintrag(text='Ausrollgrenze [%]: ' + str(round(1e2*atterberg['Ausrollgrenze [%]'])/1e2));
            self.tabs['LoDi'].NeuerEintrag(text='Plastizitätszahl [%]: ' + str(round(1e2*atterberg['Plastizitaetszahl [%]'])/1e2));
            self.tabs['LoDi'].NeuerEintrag(text='Konsistenzzahl [-]: ' + str(round(1e2*atterberg['Konsistenzzahl [-]'])/1e2));
         except:
            self.tabs['LoDi'].AlleEintraegeEntfernen();
            self.tabs['LoDi'].NeuerEintrag(text=dateiname);
            self.tabs['LoDi'].NeuerEintrag(text='Fehlerhafte/Ungueltige Eintraege');
      #
      if ('Oedo-CRS' in self.boden[bodenname]):
         oedo_crs = self.boden[bodenname]['Oedo-CRS'];
         try:
            dateiname = oedo_crs['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Oedo'].NeuerEintrag(text=dateiname);
         if (oedo_crs['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Oedo'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         for oedo_lagerung in ['locker', 'dicht']:
            if ('Oedo-' + oedo_lagerung in oedo_crs):
               self.tabs['Oedo'].NeuerEintrag(text='Plot Stauchung Oedo-CRS ' + oedo_lagerung,
                  command=lambda name=oedo_lagerung: self._PlotbefehlInterpretieren('Stauchung Oedo-CRS ' + name));
               self.tabs['Oedo'].NeuerEintrag(text='Plot Porenzahl Oedo-CRS ' + oedo_lagerung,
                  command=lambda name=oedo_lagerung: self._PlotbefehlInterpretieren('Porenzahl Oedo-CRS ' + name));
      #
      if ('Oedo-CRS-Visko' in self.boden[bodenname]):
         oedo_crsvisko = self.boden[bodenname]['Oedo-CRS-Visko'];
         try:
            dateiname = oedo_crsvisko['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Oedo'].NeuerEintrag(text=dateiname);
         if (oedo_crsvisko['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Oedo'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Oedo'].NeuerEintrag(text='Plot Porenzahl Oedo-CRS-Visko',
            command=lambda: self._PlotbefehlInterpretieren('Porenzahl Oedo-CRS-Visko'));
      #
      if ('Oedo-CRL' in self.boden[bodenname]):
         oedo_crl = self.boden[bodenname]['Oedo-CRL'];
         try:
            dateiname = oedo_crl['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Oedo'].NeuerEintrag(text=dateiname);
         if (oedo_crl['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Oedo'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Oedo'].NeuerEintrag(text='Plot Oedo-CRL Wurzelmassstab',
            command=lambda: self._PlotbefehlInterpretieren('Oedo-CRL Wurzelmassstab Laststufe 1'));
         self.tabs['Oedo'].NeuerEintrag(text='Plot Oedo-CRL Logarithmisch',
            command=lambda: self._PlotbefehlInterpretieren('Oedo-CRL Logarithmisch Laststufe 1'));
         self.tabs['Oedo'].NeuerEintrag(text='Plot Oedo-CRL Porenzahl',
            command=lambda: self._PlotbefehlInterpretieren('Oedo-CRL Porenzahl Laststufe 1'));
         self.tabs['Oedo'].NeuerEintrag(text='Plot Oedo-CRL Kurvenfit',
            command=lambda: self._PlotbefehlInterpretieren('Oedo-CRL Fit'));
      #
      if ('Oedo-dicht' in self.boden[bodenname]):
         oedo_dicht = self.boden[bodenname]['Oedo-dicht'];
         try:
            dateiname = oedo_dicht['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Oedo'].NeuerEintrag(text=dateiname);
         if (oedo_dicht['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Oedo'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Oedo'].NeuerEintrag(text='Plot Oedo-dicht',
            command=lambda: self._PlotbefehlInterpretieren('dichter Oedometerversuch'));
      #
      if ('Oedo-locker' in self.boden[bodenname]):
         oedo_locker = self.boden[bodenname]['Oedo-locker'];
         try:
            dateiname = oedo_locker['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Oedo'].NeuerEintrag(text=dateiname);
         if (oedo_locker['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Oedo'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Oedo'].NeuerEintrag(text='Plot Oedo-locker',
            command=lambda: self._PlotbefehlInterpretieren('lockerer Oedometerversuch'));
      #
      if ('Triax-D-dicht' in self.boden[bodenname]):
         triaxd_dicht = self.boden[bodenname]['Triax-D-dicht'];
         try:
            dateiname = triaxd_dicht['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Triax'].NeuerEintrag(text=dateiname);
         if (triaxd_dicht['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Triax'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Triax'].NeuerEintrag(text='Plot Volumen Triax-D-dicht',
            command=lambda: self._PlotbefehlInterpretieren('Volumen dichter Triax-D'));
         dilatanzwinkel = 'Dilatanzwinkel: ';
         for idx_triaxversuche in range(3):
            versuchsname = 'Versuch ' + str(idx_triaxversuche + 1);
            try:
               tempwinkel = triaxd_dicht[versuchsname]['Peakzustand']['Dilatanzwinkel [Grad]'];
               dilatanzwinkel += str(round(tempwinkel*10.0)/10.0) + ' Grad; ';
            except:
               dilatanzwinkel += '-?-; ';
         #
         self.tabs['Triax'].NeuerEintrag(text=dilatanzwinkel);
         self.tabs['Triax'].NeuerEintrag(text='Plot Porenzahl Triax-D-dicht',
            command=lambda: self._PlotbefehlInterpretieren('Porenzahl dichter Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Reibungswinkel Triax-D-dicht',
            command=lambda: self._PlotbefehlInterpretieren('Reibungswinkel dichter Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Mittelspannung Triax-D-dicht',
            command=lambda: self._PlotbefehlInterpretieren('Mittelspannung dichter Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Spannungskreise Triax-D-dicht',
            command=lambda: self._PlotbefehlInterpretieren('Spannungskreise dichter Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Bruchgerade Triax-D-dicht',
            command=lambda: self._PlotbefehlInterpretieren('Bruchgerade dichter Triax-D'));
      #
      if ('Triax-D-locker' in self.boden[bodenname]):
         triaxd_locker = self.boden[bodenname]['Triax-D-locker'];
         try:
            dateiname = triaxd_locker['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Triax'].NeuerEintrag(text=dateiname);
         if (triaxd_locker['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Triax'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Triax'].NeuerEintrag(text='Plot Volumen Triax-D-locker',
            command=lambda: self._PlotbefehlInterpretieren('Volumen lockerer Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Porenzahl Triax-D-locker',
            command=lambda: self._PlotbefehlInterpretieren('Porenzahl lockerer Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Reibungswinkel Triax-D-locker',
            command=lambda: self._PlotbefehlInterpretieren('Reibungswinkel lockerer Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Mittelspannung Triax-D-locker',
            command=lambda: self._PlotbefehlInterpretieren('Mittelspannung lockerer Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Spannungskreise Triax-D-locker',
            command=lambda: self._PlotbefehlInterpretieren('Spannungskreise lockerer Triax-D'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Bruchgerade Triax-D-locker',
            command=lambda: self._PlotbefehlInterpretieren('Bruchgerade lockerer Triax-D'));
      #
      if ('Triax-CU' in self.boden[bodenname]):
         triax_cu = self.boden[bodenname]['Triax-CU'];
         try:
            dateiname = triax_cu['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Triax'].NeuerEintrag(text=dateiname);
         if (triax_cu['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Triax'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Triax'].NeuerEintrag(text='Plot Mittelspannung Triax-CU',
            command=lambda: self._PlotbefehlInterpretieren('Mittelspannung Triax-CU'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Hauptspannungsverhaeltnis Triax-CU',
            command=lambda: self._PlotbefehlInterpretieren('Hauptspannungsverhaeltnis Triax-CU'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Porenwasserdruckdelta Triax-CU',
            command=lambda: self._PlotbefehlInterpretieren('Porenwasserdruckdelta Triax-CU'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Spannungskreise Triax-CU',
            command=lambda: self._PlotbefehlInterpretieren('Spannungskreise Triax-CU'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Bruchgerade Triax-CU',
            command=lambda: self._PlotbefehlInterpretieren('Bruchgerade Triax-CU'));
      #
      if ('Auswertung-Hypoplastisch' in self.boden[bodenname]):
         from .parameterbestimmung import HypoplastischeParameterFuerBoden
         #
         auswertung = self.boden[bodenname]['Auswertung-Hypoplastisch'];
         try:
            dateiname = auswertung['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Auswertung'].NeuerEintrag(text=dateiname);
         if (auswertung['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Auswertung'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         refunten = tkinter.StringVar();
         refunten.set('30');
         self.tabs['Auswertung'].NeuerEintrag(text='Ref.-Spannung-min [kN/m^2]', variable=refunten);
         refoben = tkinter.StringVar();
         refoben.set('1500');
         self.tabs['Auswertung'].NeuerEintrag(text='Ref.-Spannung-max [kN/m^2]', variable=refoben);
         #
         hypoparamrahmen = self.tabs['Auswertung'].NeuerFrameEintrag();
         self.tabs['Auswertung'].NeuerBefehl(text='Hypoplastische Parameter berechnen',
            command=lambda: self._HypoplastischeParameterBerechnen(hypoparamrahmen, refunten.get(), refoben.get()));
         self._HypoplastischeParameterBerechnen(hypoparamrahmen, refunten.get(), refoben.get());
      #
      if ('Triax-p-q' in self.boden[bodenname]):
         triax_pq = self.boden[bodenname]['Triax-p-q'];
         try:
            dateiname = triax_pq['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Triax'].NeuerEintrag(text=dateiname);
         if (triax_pq['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Triax'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         self.tabs['Triax'].NeuerEintrag(text='Plot Spannungen Triax-p-q',
            command=lambda: self._PlotbefehlInterpretieren('Spannungen Triax-p-q'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Stauchungen Triax-p-q',
            command=lambda: self._PlotbefehlInterpretieren('Stauchungen Triax-p-q'));
         self.tabs['Triax'].NeuerEintrag(text='Plot E-Modul-Entwicklung Triax-p-q',
            command=lambda: self._PlotbefehlInterpretieren('E-Modul-Entwicklung Triax-p-q'));
         self.tabs['Triax'].NeuerEintrag(text='Plot Dehnungen Triax-p-q',
            command=lambda: self._PlotbefehlInterpretieren('Dehnungen Triax-p-q'));
         #
         from .parameterbestimmung import ErweiterteHypoplastischeParameterFuerBoden
         #
         self.tabs['Auswertung'].NeuerEintrag(text=dateiname);
         if (triax_pq['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Auswertung'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         offset = tkinter.StringVar();
         offset.set('0');
         self.tabs['Auswertung'].NeuerEintrag(text='Startoffset', variable=offset);
         glaettungswert = tkinter.StringVar();
         glaettungswert.set('10');
         self.tabs['Auswertung'].NeuerEintrag(text='Glättungswert', variable=glaettungswert);
         refspanne = tkinter.StringVar();
         refspanne.set('3');
         self.tabs['Auswertung'].NeuerEintrag(text='Ref.Wertspanne', variable=refspanne);
         #
         erwhypoparamrahmen = self.tabs['Auswertung'].NeuerFrameEintrag();
         self.tabs['Auswertung'].NeuerBefehl(text='Erw. Hypopl. Parameter berechnen',
            command=lambda: self._ErwHypoplastischeParameterBerechnen(erwhypoparamrahmen, offset.get(),
            glaettungswert.get(), refspanne.get()));
         self._ErwHypoplastischeParameterBerechnen(erwhypoparamrahmen, offset.get(), glaettungswert.get(),
            refspanne.get());
      #
      if ('Oedo-CRS-Visko' in self.boden[bodenname]):
         from .parameterbestimmung import ViskohypoplastischeParameterFuerBoden
         #
         oedo_crsvisko = self.boden[bodenname]['Oedo-CRS-Visko'];
         try:
            dateiname = oedo_crsvisko['Dateiname'][num_refzeichen:];
         except:
            dateiname = '--Dateiname fehlt/ungueltig--';
         #
         self.tabs['Auswertung'].NeuerEintrag(text=dateiname);
         if (oedo_crsvisko['Status'] != 'Einlesen erfolgreich'):
            self.tabs['Auswertung'].NeuerEintrag(text='! Fehler beim Einlesen (siehe Log) !');
         #
         intervalllokalext = tkinter.StringVar();
         intervalllokalext.set('25');
         self.tabs['Auswertung'].NeuerEintrag(text='Intervall lok. Extremwert', variable=intervalllokalext);
         p1logverhaeltnis = tkinter.StringVar();
         p1logverhaeltnis.set('0.5');
         self.tabs['Auswertung'].NeuerEintrag(text='P1 Logverhältnis', variable=p1logverhaeltnis);
         p5logverhaeltnis = tkinter.StringVar();
         p5logverhaeltnis.set('0.5');
         self.tabs['Auswertung'].NeuerEintrag(text='P5 Logverhältnis', variable=p5logverhaeltnis);
         interpzwischenpunkte = tkinter.StringVar();
         interpzwischenpunkte.set('5');
         self.tabs['Auswertung'].NeuerEintrag(text='Interp. Zwischenpunkte', variable=interpzwischenpunkte);
         #
         viskohypoparamrahmen = self.tabs['Auswertung'].NeuerFrameEintrag();
         self.tabs['Auswertung'].NeuerBefehl(text='Viskohypopl. Parameter berechnen',
            command=lambda: self._ViskohypoplastischeParameterBerechnen(viskohypoparamrahmen,
            intervalllokalext.get(), p1logverhaeltnis.get(), p5logverhaeltnis.get(), interpzwischenpunkte.get()));
         self._ViskohypoplastischeParameterBerechnen(viskohypoparamrahmen, intervalllokalext.get(),
            p1logverhaeltnis.get(), p5logverhaeltnis.get(), interpzwischenpunkte.get());
      #
      self.tkroot.update_idletasks();
   #
   def _DatenEinlesen(self, unterfenster, bodenname, dateimaske, zielordner):
      from .dateneinlesen import BodendatenEinlesen
      #
      if (bodenname == ''):
         messagebox.showwarning(parent=unterfenster, title='Daten Einlesen',
            message='Bodenname darf nicht leer sein');
         return;
      #
      if (zielordner == ''):
         zielordner = './';
      #
      if (self.boden is not None):
         if (bodenname in self.boden.keys()):
            messagebox.showwarning(parent=unterfenster, title='Daten Einlesen',
               message='Bodenname ' + bodenname + ' existiert bereits');
            return;
      #
      daten = BodendatenEinlesen(bodenname=bodenname, dateimuster=dateimaske, zielordner=zielordner,
         ignoriere=self.ignoriertedaten);
      if (daten is None):
         messagebox.showwarning(parent=unterfenster, title='Daten Einlesen',
            message='Dateiname oder Dateimuster ungültig');
         return;
      else:
         # Eingaben als neue Startwerte speichern
         self.zwischenspeicher_dateieinlesen = [bodenname, dateimaske, zielordner];
         if (self.boden is None):
            self.boden = dict();
         #
         self.boden.update(daten);
         self._BodenlisteAktualisieren();
         unterfenster.destroy();
   #
   def _DatensatzSpeichern(self, unterfenster, dateiname, auswahlbox, saveall=False):
      from os import path as os_path
      from .dateneinlesen import ExistiertDatei, DatensatzSpeichern
      #
      if ((dateiname == '') or (self.boden is None)):
         messagebox.showwarning(parent=unterfenster, title='Datensatz speichern',
            message='Dateiname oder Bodendaten fehlen');
         return;
      #
      if (os_path.isdir(dateiname)):
         messagebox.showwarning(parent=unterfenster, title='Datensatz speichern',
            message='Dateiname darf kein Ordner sein');
         return;
      #
      if (ExistiertDatei(dateiname=dateiname)):
         fortfahren = messagebox.askyesno(parent=unterfenster, title='Datensatz speichern',
            message='Datei existiert bereits. Überschreiben?');
         if (not fortfahren):
            return;
      #
      if (saveall == 1):
         DatensatzSpeichern(datensatz=self.boden, dateiname=dateiname);
         self.zwischenspeicher_datensatz[1] = os_path.dirname(dateiname);
      else:
         bodenauswahl = [auswahlbox.get(elem) for elem in auswahlbox.curselection()];
         if (len(bodenauswahl) == 0):
            messagebox.showwarning(parent=unterfenster, title='Datensatz speichern',
               message='Keine Datensätze ausgewählt');
            return;
         #
         self.zwischenspeicher_datensatz[1] = os_path.dirname(dateiname);
         datensaetze = dict();
         for auswahl in bodenauswahl:
            datensaetze.update([(auswahl, self.boden[auswahl])]);
         #
         DatensatzSpeichern(datensatz=datensaetze, dateiname=dateiname);
      #
      unterfenster.destroy();
   #
   def _DatensatzEntfernen(self, unterfenster, auswahlbox, closeall):
      if (self.boden is None):
         return;
      #
      if (closeall):
         if (len(self.boden.keys()) != 0):
            self.boden.clear();
         #
         self.boden = None;
         self.bodenname.set('');
      else:
         bodenauswahl = [auswahlbox.get(elem) for elem in auswahlbox.curselection()];
         if (len(bodenauswahl) == 0):
            messagebox.showwarning(parent=unterfenster, title='Datensatz entfernen',
               message='Keine Datensätze ausgewählt');
            return;
         #
         for datensatz in bodenauswahl:
            del self.boden[datensatz];
            if (datensatz == self.bodenname.get()):
               self.bodenname.set('');
         #
         if (len(self.boden.keys()) == 0):
            self.boden = None;
      #
      self._BodenlisteAktualisieren();
      if (self.bodenname.get() != ''):
         self._TabsAktualisieren(bodenname=self.bodenname.get());
      else:
         self._TabsAktualisieren();
      #
      unterfenster.destroy();
   #
   def _FensterOrdnerDurchsuchen(self, unterfenster, ordnername):
      zielordner = filedialog.askdirectory(parent=unterfenster, title='Ordner auswählen',
         initialdir=ordnername.get());
      ordnername.set(zielordner);
   #
   def _FensterDateiSpeichern(self, unterfenster, dateiname):
      zieldatei = filedialog.asksaveasfilename(parent=unterfenster, title='Speicherort auswählen',
         initialfile=dateiname.get());
      if ((zieldatei == '') or (not zieldatei)):
         return;
      #
      dateiname.set(zieldatei);
   #
   def _FensterDatensaetzeAusBodenmusterdateiEinlesen(self):
      from os import path as os_path
      from .dateneinlesen import BodenmusterdateiEinlesen
      from .guihilfen import FensterZentrieren
      from .guistil import CustomLabel, CustomCheckbutton, CustomAuswahlliste, CustomButton
      #
      dateiname = filedialog.askopenfilename(title='Bodenmusterdatei Einlesen',
         initialdir=self.zwischenspeicher_bodenmustereinlesen[0]);
      if ((dateiname == '') or (not dateiname)):
         return;
      #
      bodenmuster = BodenmusterdateiEinlesen(dateiname=dateiname);
      if (len(bodenmuster.keys()) == 0):
         messagebox.showwarning(title='Bodenmusterdatei Einlesen',
            message='Datei ' + dateiname + ' enthält keine Bodenmuster');
         return;
      #
      self.zwischenspeicher_bodenmustereinlesen[0] = os_path.dirname(dateiname);
      unterfenster = tkinter.Toplevel(self.tkroot, background=self.farben.farbe_bg_highlight);
      unterfenster.tk.call('wm', 'iconphoto', unterfenster._w, tkinter.PhotoImage(data=self.icondata));
      unterfenster.title('Bodenmuster Einlesen');
      #
      text_dateiname = CustomLabel(unterfenster, text='Bodenmuster aus Datei');
      text_dateiname.grid(row=0, column=0, padx=10, pady=10, sticky='e');
      #
      loadall = tkinter.IntVar();
      loadall.set(0);
      eingabe_alleswaehlen = CustomCheckbutton(unterfenster, variable=loadall, text='Alle Laden');
      eingabe_alleswaehlen.grid(row=0, column=1, padx=10, pady=10, sticky='w');
      #
      CustomLabel(unterfenster, text=dateiname, font=('Helvetica', '-12')).grid(row=1, column=0, columnspan=2, padx=5, pady=10);
      #
      schluessel = list(bodenmuster.keys());
      schluessel.sort();
      auswahlframe = CustomAuswahlliste(unterfenster, schluessel=schluessel);
      auswahlframe.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ns');
      #
      button = CustomButton(unterfenster, text="Laden",
         command=lambda: self._BodenmusterLaden(unterfenster, bodenmuster,
         auswahlframe.children['!listbox'], loadall.get()));
      button.grid(row=3, column=0, padx=10, pady=10, sticky='e');
      #
      button = CustomButton(unterfenster, text="Schließen", command=unterfenster.destroy);
      button.grid(row=3, column=1, padx=10, pady=10, sticky='w');
      #
      FensterZentrieren(self.tkroot, unterfenster);
   #
   def _BodenmusterLaden(self, unterfenster, bodenmuster, auswahlbox, loadall):
      from .dateneinlesen import BodendatenMitSchluesselAusMusterEinlesen
      # Eintraege immer gleich aktualisieren, damit bei Abbruechen zumindest alle vorher
      # vollstaendig geladenen Boeden verfuegbar sind
      if (loadall):
         musterdaten = bodenmuster;
      else:
         bodenauswahl = [auswahlbox.get(elem) for elem in auswahlbox.curselection()];
         if (len(bodenauswahl) == 0):
            messagebox.showwarning(parent=unterfenster, title='Datensätze laden',
               message='Keine Datensätze ausgewählt');
            return;
         #
         musterdaten = dict();
         for auswahl in bodenauswahl:
            musterdaten.update([(auswahl, bodenmuster[auswahl])]);
      #
      for einzelboden in musterdaten.keys():
         einzelpaar = dict([(einzelboden, musterdaten[einzelboden])]);
         bodendaten = BodendatenMitSchluesselAusMusterEinlesen(muster=einzelpaar,
            ignoriere=self.ignoriertedaten);
         if (bodendaten is None):
            continue;
         #
         if (self.boden is None):
            self.boden = dict();
         #
         self.boden.update(bodendaten);
         self._BodenlisteAktualisieren();
      #
      unterfenster.destroy();
   #
   def _FensterDateiEinlesen(self):
      from .guihilfen import FensterZentrieren
      from. guistil import CustomLabel, CustomEntry, CustomButton
      #
      unterfenster = tkinter.Toplevel(self.tkroot, background=self.farben.farbe_bg_highlight);
      unterfenster.tk.call('wm', 'iconphoto', unterfenster._w, tkinter.PhotoImage(data=self.icondata));
      unterfenster.title('Daten einlesen');
      #
      text_bodenname = CustomLabel(unterfenster, text='Bodenname');
      text_bodenname.grid(row=0, column=0, padx=10, pady=10, sticky='nsew');
      #
      bodenname = tkinter.StringVar();
      bodenname.set(self.zwischenspeicher_dateieinlesen[0]);
      eingabe_bodenname = CustomEntry(unterfenster, textvariable=bodenname);
      eingabe_bodenname.grid(row=0, column=1, padx=10, pady=10, sticky='nsew');
      eingabe_bodenname.focus_set();
      #
      text_dateimaske = CustomLabel(unterfenster, text='Suchmaske');
      text_dateimaske.grid(row=1, column=0, padx=10, pady=10, sticky='nsew');
      #
      dateimaske = tkinter.StringVar();
      dateimaske.set(self.zwischenspeicher_dateieinlesen[1]);
      eingabe_dateimaske = CustomEntry(unterfenster, textvariable=dateimaske);
      eingabe_dateimaske.grid(row=1, column=1, padx=10, pady=10, sticky='nsew');
      #
      text_zielordner = CustomLabel(unterfenster, text='Suchordner');
      text_zielordner.grid(row=2, column=0, padx=10, pady=10, sticky='nsew');
      #
      button = CustomButton(unterfenster, text="Durchsuchen",
         command=lambda: self._FensterOrdnerDurchsuchen(unterfenster, zielordner));
      button.grid(row=2, column=1, padx=10, pady=10, sticky='w');
      #
      zielordner = tkinter.StringVar();
      zielordner.set(self.zwischenspeicher_dateieinlesen[2]);
      eingabe_zielordner = CustomEntry(unterfenster, textvariable=zielordner);
      eingabe_zielordner.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew');
      #
      button = CustomButton(unterfenster, text="Einlesen",
         command=lambda: self._DatenEinlesen(unterfenster, bodenname.get(), dateimaske.get(), zielordner.get()));
      button.grid(row=4, column=0, padx=10, pady=10, sticky='e');
      #
      button = CustomButton(unterfenster, text="Schließen", command=unterfenster.destroy);
      button.grid(row=4, column=1, padx=10, pady=10, sticky='w');
      #
      FensterZentrieren(self.tkroot, unterfenster);
   #
   def _FensterDatensatzOeffnen(self):
      from os import path as os_path
      from .dateneinlesen import DatensatzEinlesen
      #
      datensatz = filedialog.askopenfilename(title='Datei auswählen',
         initialdir=self.zwischenspeicher_datensatz[0]);
      if ((datensatz == '') or (not datensatz)):
         return;
      #
      eingelesen = DatensatzEinlesen(dateiname=datensatz);
      if (eingelesen is None):
         messagebox.showwarning(parent=self.tkroot, title='Datensatz öffnen',
            message='Fehler beim Einlesen des Datensatzes aus ' + datensatz);
         return;
      #
      self.zwischenspeicher_datensatz[0] = os_path.dirname(datensatz);
      if (self.boden is None):
         self.boden = eingelesen;
      else:
         self.boden.update(eingelesen);
      #
      self._BodenlisteAktualisieren();
   #
   def _FensterDatensatzSpeichern(self):
      from .guihilfen import FensterZentrieren
      from .guistil import CustomLabel, CustomButton, CustomCheckbutton, CustomAuswahlliste
      from .guistil import CustomEntry
      #
      if (self.boden is None):
         messagebox.showwarning(title='Datensatz speichern', message='Kein Datensatz verfügbar');
         return;
      #
      unterfenster = tkinter.Toplevel(self.tkroot, background=self.farben.farbe_bg_highlight);
      unterfenster.tk.call('wm', 'iconphoto', unterfenster._w, tkinter.PhotoImage(data=self.icondata));
      unterfenster.title('Datensatz speichern');
      #
      text_dateiname = CustomLabel(unterfenster, text='Datensatz auswählen');
      text_dateiname.grid(row=0, column=0, padx=10, pady=10, sticky='e');
      #
      saveall = tkinter.IntVar();
      saveall.set(0);
      eingabe_alleswaehlen = CustomCheckbutton(unterfenster, variable=saveall, text='Alles Speichern');
      eingabe_alleswaehlen.grid(row=0, column=1, padx=10, pady=10, sticky='w');
      #
      schluessel = list(self.boden.keys());
      schluessel.sort();
      auswahlframe = CustomAuswahlliste(unterfenster, schluessel=schluessel);
      auswahlframe.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ns');
      #
      text_dateiname = CustomLabel(unterfenster, text='Dateiname');
      text_dateiname.grid(row=2, column=0, padx=10, pady=10);
      #
      button = CustomButton(unterfenster, text="Durchsuchen",
         command=lambda: self._FensterDateiSpeichern(unterfenster, dateiname));
      button.grid(row=2, column=1, padx=20, pady=10);
      #
      dateiname = tkinter.StringVar();
      dateiname.set(self.zwischenspeicher_datensatz[1]);
      eingabe_dateiname = CustomEntry(unterfenster, textvariable=dateiname, width=34);
      eingabe_dateiname.grid(row=3, column=0, columnspan=2, padx=10, pady=10);
      #
      button = CustomButton(unterfenster, text="Speichern",
         command=lambda: self._DatensatzSpeichern(unterfenster, dateiname.get(), auswahlframe.children['!listbox'], saveall.get()));
      button.grid(row=4, column=0, padx=20, pady=10);
      #
      button = CustomButton(unterfenster, text="Schließen", command=unterfenster.destroy);
      button.grid(row=4, column=1, padx=20, pady=10);
      #
      FensterZentrieren(self.tkroot, unterfenster);
   #
   def _FensterDatensatzEntfernen(self):
      from .guihilfen import FensterZentrieren
      from .guistil import CustomLabel, CustomButton, CustomCheckbutton, CustomAuswahlliste
      #
      if (self.boden is None):
         messagebox.showwarning(title='Datensatz entfernen', message='Kein Datensatz verfügbar');
         return;
      #
      unterfenster = tkinter.Toplevel(self.tkroot, background=self.farben.farbe_bg_highlight);
      unterfenster.tk.call('wm', 'iconphoto', unterfenster._w, tkinter.PhotoImage(data=self.icondata));
      unterfenster.title('Datensatz entfernen');
      #
      text_dateiname = CustomLabel(unterfenster, text='Datensatz auswählen');
      text_dateiname.grid(row=0, column=0, padx=10, pady=10, sticky='e');
      #
      closeall = tkinter.IntVar();
      closeall.set(0);
      eingabe_alleswaehlen = CustomCheckbutton(unterfenster, variable=closeall, text='Alles Entfernen');
      eingabe_alleswaehlen.grid(row=0, column=1, padx=10, pady=10, sticky='w');
      #
      schluessel = list(self.boden.keys());
      schluessel.sort();
      auswahlframe = CustomAuswahlliste(unterfenster, schluessel=schluessel);
      auswahlframe.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ns');
      #
      button = CustomButton(unterfenster, text="Datensatz entfernen",
         command=lambda: self._DatensatzEntfernen(unterfenster, auswahlframe.children['!listbox'],
         closeall.get()));
      button.grid(row=2, column=0, padx=20, pady=10);
      #
      button = CustomButton(unterfenster, text="Schließen", command=unterfenster.destroy);
      button.grid(row=2, column=1, padx=20, pady=10);
      #
      FensterZentrieren(self.tkroot, unterfenster);
   #
   def _Infofenster(self):
      from .guihilfen import FensterZentrieren
      from .guistil import CustomLabel, CustomButton
      #
      unterfenster = tkinter.Toplevel(self.tkroot, background=self.farben.farbe_bg_highlight);
      unterfenster.tk.call('wm', 'iconphoto', unterfenster._w, tkinter.PhotoImage(data=self.icondata));
      unterfenster.title('miniSoilLAB Infos');
      #
      infolabel1 = CustomLabel(unterfenster, text='miniSoilLAB v0.5.6', font=('Helvetica', '-18', 'bold'));
      infolabel1.grid(row=0, column=0, padx=30, pady=15);
      #
      infolabel2 = CustomLabel(unterfenster, text='2019-2021 Dominik Zobel');
      infolabel2.grid(row=1, column=0, padx=30, pady=5);
      #
      button = CustomButton(unterfenster, text="Schließen", command=unterfenster.destroy);
      button.grid(row=2, column=0, padx=10, pady=15);
      #
      FensterZentrieren(self.tkroot, unterfenster);
   #
   def Vorbereiten(self):
      import datetime
      from .guistil import CustomLabelMenu, CustomOptionMenu, CustomScrollbar
      #
      menubar = tkinter.Menu(self.tkroot, tearoff=0, borderwidth=0, relief=tkinter.FLAT);
      menu_datei = tkinter.Menu(menubar, tearoff=0);
      #
      menubar.add_cascade(label="Datei", menu=menu_datei);
      menu_datei.add_command(label="Bodenmusterdatei einlesen", command=self._FensterDatensaetzeAusBodenmusterdateiEinlesen);
      menu_datei.add_command(label="Dateien einlesen", command=self._FensterDateiEinlesen);
      menu_datei.add_command(label="Datensatz öffnen", command=self._FensterDatensatzOeffnen);
      menu_datei.add_command(label="Datensatz speichern", command=self._FensterDatensatzSpeichern);
      menu_datei.add_command(label="Datensatz entfernen", command=self._FensterDatensatzEntfernen);
      menu_datei.add_separator();
      menu_datei.add_command(label="Beenden", command=self.tkroot.destroy);

      menu_plot = tkinter.Menu(menubar, tearoff=0);
      menubar.add_cascade(label='Plot', menu=menu_plot);
      menu_plot.add_command(label='Als pdf speichern', command=self._PlotAlsPdfSpeichern);
      menu_plot.add_command(label='Als png speichern', command=self._PlotAlsPngSpeichern);
      #
      menu_hilfe = tkinter.Menu(menubar, tearoff=0);
      menubar.add_cascade(label='Hilfe', menu=menu_hilfe);
      menu_hilfe.add_command(label='Debug An/Aus', command=self._Debugmodus);
      menu_hilfe.add_command(label='Rohdaten An/Aus', command=self._Rohdaten);
      menu_hilfe.add_command(label='Über miniSoilLAB', command=self._Infofenster);
      #
      self.tkroot.config(menu=menubar);
      # ----------------------------------------------------------------
      scrollbreite = 16;
      # FIXME: menubarhoehe am besten direkt aus menubar ableiten
      menubarhoehe = 30;
      #
      farbe_fg_boden = '#aa0000';
      farbe_top_bg = '#202020';
      farbe_top_fg = '#dddddd';
      farbe_bg_active = '#dddddd';
      font_top = ('Helvetica', '14');
      #
      menurahmen = tkinter.Frame(self.tkroot, width=self.menubreite, background=farbe_top_bg);
      menurahmen.grid(row=0, column=0, sticky='nw');
      #
      bodenrahmen = tkinter.Frame(menurahmen, background=farbe_top_bg);
      bodenrahmen.grid(row=0, column=0, columnspan=2, sticky='nsew');
      #
      bodenlabel = ttk.Label(bodenrahmen, text='Boden:', background=farbe_top_bg,
         foreground=farbe_top_fg, font=font_top);
      bodenlabel.grid(row=0, column=0, padx=14, pady=5, sticky='nsew');
      #
      optionList = ('', );
      self.bodenname = tkinter.StringVar();
      self.bodenname.set(optionList[0]);
      #
      self.auswahlliste = CustomOptionMenu(bodenrahmen, self.bodenname, ());
      self.auswahlliste.configure(width=30);
      self.auswahlliste.grid(row=0, column=1, padx=5, pady=5, sticky='w');
      # ---
      scishowline = ttk.Label(menurahmen, text='Manuelle Plotbefehlseingabe', background=farbe_top_bg,
         foreground=farbe_top_fg, font=font_top);
      scishowline.grid(row=2, column=0, padx=14, pady=5, sticky='nsew');
      #
      self.plotcmd = tkinter.StringVar();
      cmdshowline = tkinter.Entry(menurahmen, background='#ffffff', foreground=farbe_top_bg,
         font=font_top, borderwidth=0, highlightthickness=0, relief='flat', width=30,
         textvariable=self.plotcmd);
      self.plotcmd.set('');
      cmdshowline.grid(row=3, column=0, padx=5, pady=5, columnspan=2, sticky='nsew');
      #
      # update() muss aufgerufen werden, um die tatsaechlichen Werte mit winfo_... abfragen zu koennen
      self.tkroot.update();
      menuhoehe = self.hoehe - (scishowline.winfo_height() + cmdshowline.winfo_height() + bodenlabel.winfo_height() + menubarhoehe);
      #
      self.menucanvas = tkinter.Canvas(menurahmen, highlightthickness=0, borderwidth=0);
      mainmenu = CustomLabelMenu(self.farben, self.menubreite-scrollbreite, menuhoehe, self.menucanvas);
      menuscrollbar = CustomScrollbar(menurahmen, orient='vertical', command=self.menucanvas.yview);
      #
      self.menucanvas.configure(yscrollcommand=menuscrollbar.set);
      self.menucanvas.grid(row=1, column=0, sticky='nsew');
      self.menucanvas.create_window((0, 0), window=mainmenu, anchor='nw');
      menuscrollbar.grid(row=1, column=1, sticky='ns');
      #
      mainmenu.bind('<Configure>', _Autoscrollfunktion);
      self.tkroot.bind('<MouseWheel>', lambda event: _Radscrollfunktion(event, self.menucanvas, menuscrollbar));
      self.tkroot.bind('<Button-4>', lambda event: _Radscrollfunktion(event, self.menucanvas, menuscrollbar));
      self.tkroot.bind('<Button-5>', lambda event: _Radscrollfunktion(event, self.menucanvas, menuscrollbar));
      # ---
      kvs_section = mainmenu.NeuerEintrag(text='Kornverteilung');
      lodi_section = mainmenu.NeuerEintrag(text='Lagerung/Zustandsgrenzen');
      oedo_section = mainmenu.NeuerEintrag(text='Oedometerversuche');
      triax_section = mainmenu.NeuerEintrag(text='Triaxialversuche');
      ausw_section = mainmenu.NeuerEintrag(text='Auswertung');
      #
      self.tabs = {'KVS': kvs_section, 'LoDi': lodi_section, 'Oedo': oedo_section,
         'Triax': triax_section, 'Auswertung': ausw_section};
      #
      menurahmen.grid_columnconfigure(0, weight=1);
      # ----------------------------------------------------------------
      dpi = 150;
      self.figure = matplotlib.figure.Figure(figsize=(self.plotbreite/dpi, self.hoehe/dpi), dpi=dpi);
      #
      zeichnungsrahmen = tkinter.Frame(self.tkroot); #, width=plotbreite, height=plothoehe);
      zeichnungsrahmen.grid(row=0, column=1, sticky='nsew');
      # Mit den beiden Befehlen grid_rowconfigure und grid_columnconfigure kann ein grid-Element
      # auch beim vergroessern die maximale Breite/Hoehe einnehmen (mit entsprechenden sticky-Flags)
      self.tkroot.grid_rowconfigure(0, weight=1);
      self.tkroot.grid_columnconfigure(1, weight=1);
      self.zeichnung = FigureCanvasTkAgg(self.figure, master=zeichnungsrahmen);
      self.zeichnung.draw();
      self.zeichnung.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1);
      self.zeichnung._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1);
      # Final nochmal die Groesse setzen (notwendig?)
      self.tkroot.geometry('{}x{}'.format(self.menubreite+self.plotbreite, self.hoehe));
      #
      self.zeitstempel = datetime.datetime.now().strftime('%Y%m%d-%H%M%S');
      #
      self.tkroot.bind('<Return>', self._PlotbefehlWeiterleiten);
      self.tkroot.bind('<Control-q>', self._Beenden);
      self.tkroot.bind('<Up>', self._LetzterPlotBefehl);
      self.tkroot.bind('<Down>', self._NaechsterPlotBefehl);
   #
   def Ausfuehren(self):
      tkinter.mainloop();
#
