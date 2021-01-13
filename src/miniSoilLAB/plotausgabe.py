# -*- coding: utf-8 -*-
"""
plotausgabe.py   v0.3 (2020-02)
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
def DarstellungsgrenzenFinden(minwert, maxwert):
   """Ermittle fuer das Intervall [minwert, maxwert] eine sinnvolle untere und obere
   Darstellungsgrenze. Sinnvoll bezeichnet hier Zahlen mit maximal zwei charakteristichen
   Stellen im Schema, d.h. #.#e+-# fuer # als Zahl von 0-9, die sich recht nah an
   den Grenzen des Intervalls befinden (oder den Grenzen entsprechen).
   """
   from .gleichungsloeser import NaechsterWert
   #
   grenze_unten = NaechsterWert(wert=minwert, spanne=maxwert-minwert, aufsteigend=False);
   grenze_oben = NaechsterWert(wert=maxwert, spanne=maxwert-minwert, aufsteigend=True);
   return [grenze_unten, grenze_oben];
#


# -------------------------------------------------------------------------------------------------
def PlotvorlageVorbereiten(typ=''):
   """Bereite eine generische Struktur fuer die Plotdaten vor, die fuer einen Plot mit
   TkPlot oder EmbeddedPlot genutzt wird. Vor dem eigentlichen Plotten muss noch (mindestens)
   xdaten und ydaten dieser Struktur aktualisiert werden. Typischerweise wird diese Funktion
   innerhalb der Plotdaten...()-Funktionen aufgerufen, aber sie kann auch fuer die Erstellung
   eigener Plots oder Plotfunktionen verwendet werden. Der Uebergabewert typ kann zum Speichern
   von einem Schluesselbegriff verwendet werden. Gibt die Struktur mit den Plotdaten zurueck.
   """
   import datetime
   from .datenstruktur import Datenstruktur
   #
   plotvorlage = Datenstruktur();
   for listeneintrag in ['xdaten', 'ydaten', 'xlim', 'ylim', 'stylelist', 'legendeneintraege', 'textfelder']:
      plotvorlage.update([(listeneintrag, [])]);
   #
   for stringeintrag in ['xlabel', 'ylabel', 'title', 'typ']:
      plotvorlage.update([(stringeintrag, '')]);
   #
   for booleintrag in ['xflip', 'yflip']:
      plotvorlage.update([(booleintrag, False)]);
   #
   plotvorlage.update([('xscale', 'linear')]);
   plotvorlage.update([('yscale', 'linear')]);
   plotvorlage.update([('legendenposition', 'upper right')]);
   plotvorlage.update([('dunkelskala', ['#252525', '#525252', '#737373', '#969696'])]);
   plotvorlage.update([('farbskala 0', ['#016c59', '#1c9099', '#67a9cf', '#bdc9e1'])]);
   plotvorlage.update([('farbskala 1', ['#993404', '#d95f0e', '#fe9929', '#fed98e'])]);
   plotvorlage.update([('typ', typ)]);
   plotvorlage.update([('zeitstempel', datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))]);
   return plotvorlage;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenOedoCRS(boden, varianten=None, yparam='Porenzahl [-]', yflip=False):
   """Bereitet eine Struktur fuer die Plotdaten eines Oedo-CRS-Versuchs vor, die fuer einen Plot mit
   TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden anhand der Daten in
   boden['Oedo-CRS'] und varianten (oder boden['Oedo-CRS-Visko'] wenn variante=['Visko'] extrahiert
   und gespeichert. Die y-Variable kann mit yparam gewaehlt werden (sofern sie in boden['Oedo-CRS']
   existiert). Optional kann ausserdem die y-Achse gespiegelt werden. Gibt die fertigen Plotdaten
   zurueck.
   """
   if (varianten == ['Visko']):
      versuchstyp = 'Oedo-CRS-Visko';
   else:
      versuchstyp = 'Oedo-CRS';
   #
   crsoedo = PlotvorlageVorbereiten(typ=versuchstyp);
   xparam = 'Spannung [kN/m^2]';
   xdaten = [];
   ydaten = [];
   legendeneintraege = [];
   stylelist = [];
   if ((varianten is None) or (varianten == ['Visko'])):
      try:
         xdaten = [boden[versuchstyp][xparam][1:]];
         ydaten = [boden[versuchstyp][yparam][1:]];
      except:
         print('# Warnung: \'' + xparam + '\' oder/und \'' + yparam + '\' nicht in boden gefunden');
         return None;
      #
      legendeneintraege = ['Oedometer'];
      stylelist = [[crsoedo['farbskala 0'][0], '-', 'None']];
   else:
      for idx_var, einzelvariante in enumerate(varianten):
         try:
            xdaten += [boden[versuchstyp][einzelvariante][xparam][1:]];
            ydaten += [boden[versuchstyp][einzelvariante][yparam][1:]];
         except:
            print('# Warnung: Benoetigte Eintraege in boden nicht gefunden');
            return None;
         #
         legendeneintraege += [einzelvariante];
         stylelist += [[crsoedo['farbskala ' + str(idx_var)][0], '-', 'None']];
   #
   crsoedo.update([('xdaten', xdaten)]);
   crsoedo.update([('ydaten', ydaten)]);
   crsoedo.update([('legendeneintraege', legendeneintraege)]);
   crsoedo.update([('stylelist', stylelist)]);
   crsoedo.update([('xlabel', xparam)]);
   crsoedo.update([('ylabel', yparam)]);
   crsoedo.update([('xscale', 'log')]);
   crsoedo.update([('yflip', yflip)]);
   return crsoedo;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenOedoCRL(boden, variante, kurve=0):
   """Bereitet eine Struktur fuer die Plotdaten eines Oedo-CRL-Versuchs vor,
   die fuer einen Plot mit TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden
   anhand der Daten in boden['Oedo-CRL'], variante und kurve extrahiert und gespeichert.
   Dabei steht kurve = 0 fuer alle Kurven und 1-8 fuer die Kurve der jeweiligen Laststufe.
   Gibt die fertigen Plotdaten zurueck.
   """
   from math import log10
   #
   if ('Oedo-CRL' not in boden):
      return None;
   #
   crloedo = PlotvorlageVorbereiten(typ='Oedo-CRL');
   xparam = 'Zeit [h]';
   xdaten = [];
   ydaten = [];
   yparam = 'Setzung-spez [%]';
   xscale = 'log';
   yflip = True;
   legendeneintraege = [];
   stylelist = [];
   extra_text = [];
   #
   if (variante == 'wurzel'):
      xscale = 'sqrt';
   elif (variante == 'porenzahl'):
      yparam = 'Porenzahl [-]';
      yflip = False;
   #
   for idx_var in range(1, 9):
      if ((kurve != 0) and (kurve != idx_var)):
         continue;
      #
      einzelversuch = 'Laststufe ' + str(idx_var);
      if (einzelversuch not in boden['Oedo-CRL']):
         continue;
      #
      try:
         x_temp = boden['Oedo-CRL'][einzelversuch][xparam][1:];
         y_temp = boden['Oedo-CRL'][einzelversuch][yparam][1:];
         laststufen = boden['Oedo-CRL'][einzelversuch]['Laststufen [kN/m^2]'];
      except:
         print('# Warnung: \'' + xparam + '\', \'' + yparam + '\' oder/und \'Laststufen [kN/m^2]\') nicht in boden gefunden');
         return None;
      #
      xdaten += [x_temp];
      ydaten += [y_temp];
      legendeneintraege += [einzelversuch + ' (' + str(round(10.0*laststufen[0])/10.0) + ' bis ' + str(round(10.0*laststufen[1])/10.0) + ' kPa)'];
      stylelist += [[crloedo['farbskala 1'][idx_var % len(crloedo['farbskala 1'])], '-', 'None']];
      #
      if (variante == 'porenzahl'):
         try:
            c_alpha = boden['Oedo-CRL'][einzelversuch]['Parameter']['c_alpha [-]'];
         except:
            print('# Warnung: Benoetigter Eintrag \'c_alpha [-]\' nicht in boden gefunden');
            return None;
         #
         xporp = xdaten[-1][int(0.5*len(xdaten[-1]))];
         yporp = ydaten[-1][-1] - c_alpha*(log10(xporp)-log10(xdaten[-1][-1]));
         xdaten += [[xporp, xdaten[-1][-1]]];
         ydaten += [[yporp, ydaten[-1][-1]]];
         legendeneintraege += [None];
         stylelist += [[crloedo['dunkelskala'][idx_var % len(crloedo['dunkelskala'])], '--', 'None']];
         extra_text += [['c_alph=' + str(round(1e5*c_alpha)/1e5), xporp-0.01, yporp+0.001]];
      else:
         from .parameterbestimmung import _ViskohypoplastischTangentenpunkte
         #
         try:
            zeit = boden['Oedo-CRL'][einzelversuch]['Zeit [h]'];
            spez_setzung = boden['Oedo-CRL'][einzelversuch]['Setzung-spez [%]'];
            log_zu_sqrt = boden['Oedo-CRL'][einzelversuch]['Einstellungen']['Verhaeltnis Log/sqrt'];
            zwischenpunkte = boden['Oedo-CRL'][einzelversuch]['Einstellungen']['Zwischenpunkte'];
            glaettungswert = boden['Oedo-CRL'][einzelversuch]['Einstellungen']['Glaettungswert'];
            linearbereich = boden['Oedo-CRL'][einzelversuch]['Einstellungen']['Linearer Bereich'];
         except:
            print('# Warnung: Benoetigte Eintraege zur Bestimmung der Tangentenpunkte nicht in boden gefunden');
            return None;
         #
         [logschnittpunkt, logwendepunkt, sqrt100punkt, sqrt90punkt, m100, m90] = \
            _ViskohypoplastischTangentenpunkte(zeit=zeit, spez_setzung=spez_setzung,
            log_zu_sqrt=log_zu_sqrt, zwischenpunkte=zwischenpunkte, glaettungswert=glaettungswert,
            linearbereich=linearbereich);
         #
         if (logschnittpunkt is None):
            continue;
         #
         if (variante == 'wurzel'):
            xdaten += [[xdaten[-1][0], sqrt90punkt[0]/(1.15**2)],
                       [xdaten[-1][0], sqrt90punkt[0], sqrt90punkt[0]],
                       [0.0, sqrt100punkt[0], sqrt100punkt[0]],
                       [sqrt100punkt[0]]];
            ydaten += [[ydaten[-1][0], 100.0],
                       [ydaten[-1][0], 100.0, sqrt90punkt[1]],
                       [sqrt100punkt[1], sqrt100punkt[1], 100.0],
                       [sqrt100punkt[1]]];
            legendeneintraege += [None, None, None, None];
            stylelist += [[crloedo['dunkelskala'][2], '--', 'None'],
                          [crloedo['dunkelskala'][1], '--', 'None'],
                          [crloedo['dunkelskala'][3], '--', 'None'],
                          [crloedo['dunkelskala'][0], '-', 'x']];
            extra_text += [['y=' + str(round(100.0*sqrt100punkt[1])/100.0), sqrt100punkt[0]+0.01, sqrt100punkt[1]-5]];
         #
         else:
            punktwl = [10**(log10(logwendepunkt[0])-1.4*(log10(logschnittpunkt[0])-log10(logwendepunkt[0]))),
                     logwendepunkt[1]-1.4*(logschnittpunkt[1]-logwendepunkt[1])];
            punktwr = [10**(log10(logwendepunkt[0])+1.4*(log10(logschnittpunkt[0])-log10(logwendepunkt[0]))),
                     logwendepunkt[1]+1.4*(logschnittpunkt[1]-logwendepunkt[1])];
            punktu = [10**(log10(logschnittpunkt[0])-0.4*(log10(xdaten[-1][-1])-log10(logschnittpunkt[0]))),
                     logschnittpunkt[1]-0.4*(ydaten[-1][-1]-logschnittpunkt[1])];
            xdaten += [[punktwl[0], punktwr[0]], [punktu[0], xdaten[-1][-1]], [logwendepunkt[0]], [logschnittpunkt[0]]];
            ydaten += [[punktwl[1], punktwr[1]], [punktu[1], ydaten[-1][-1]], [logwendepunkt[1]], [logschnittpunkt[1]]];
            legendeneintraege += [None, None, None, None];
            stylelist += [[crloedo['dunkelskala'][3], '--', 'None'],
                          [crloedo['dunkelskala'][3], '--', 'None'],
                          [crloedo['dunkelskala'][0], '-', 'x'],
                          [crloedo['dunkelskala'][0], '-', 'x']];
            extra_text += [['y=' + str(round(100.0*logschnittpunkt[1])/100.0), logschnittpunkt[0]+0.1, logschnittpunkt[1]-5]];
   #
   if (variante == 'wurzel'):
      # Daten ragen beim Wurzelplot ueber die Y-Achse (automatisches Skalieren schlaegt fehl).
      # Deshalb muss explizit das X-Limit gesetzt werden.
      from .gleichungsloeser import NaechsterWert
      #
      maxval = 0;
      for dat in xdaten:
         maxval = max(max(dat), maxval);
      #
      xmax = NaechsterWert(wert=maxval, spanne=maxval, aufsteigend=True);
      crloedo.update([('xlim', [0.0, xmax])]);
   #
   crloedo.update([('xdaten', xdaten)]);
   crloedo.update([('ydaten', ydaten)]);
   crloedo.update([('legendeneintraege', legendeneintraege)]);
   crloedo.update([('stylelist', stylelist)]);
   crloedo.update([('xlabel', xparam)]);
   crloedo.update([('ylabel', yparam)]);
   crloedo.update([('xscale', xscale)]);
   crloedo.update([('yflip', yflip)]);
   crloedo.update([('textfelder', extra_text)]);
   return crloedo;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenOedo(boden, varianten):
   """Bereitet eine Struktur fuer die Plotdaten eines gewoehnlichen Oedometerversuchs vor,
   die fuer einen Plot mit TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden
   anhand der Daten in boden und varianten extrahiert und gespeichert.
   Gibt die fertigen Plotdaten zurueck.
   """
   from math import log
   #
   oedo = PlotvorlageVorbereiten(typ='Oedo');
   # Ein sinnvoller Plot mit den Ausgleichskoeffizienten benoetigt die folgenden xparam und yparam,
   # so dass diese nicht als Argumente uebergeben werden koennen
   xparam = 'Spannung [kN/m^2]';
   yparam = 'Dehnung-axial [-]';
   xdaten = [];
   ydaten = [];
   legendeneintraege = [];
   stylelist = [];
   schritte = ['Erstbelastung', 'Entlastung', 'Wiederbelastung'];
   for idx_var, einzelvariante in enumerate(varianten):
      x_all = [];
      y_all = [];
      y_fitall = [];
      for einzelschritt in schritte:
         try:
            x_temp = boden[einzelvariante][einzelschritt][xparam];
            y_temp = boden[einzelvariante][einzelschritt][yparam];
            a, b, c = boden[einzelvariante][einzelschritt]['Ausgleichs-Koeffizienten'];
         except:
            continue;
         #
         x_all += x_temp;
         y_all += y_temp;
         y_fitall += [a*log(x + b) + c for x in x_temp];
      #
      if (x_all == []):
         print('# Warnung: \'' + xparam + '\', \'' + yparam + '\' oder/und \'Ausgleichs-Koeffizienten\' fuer Belastungsschritte nicht gefunden');
         return None;
      #
      xdaten += [x_all, x_all];
      ydaten += [y_all, y_fitall];
      legendeneintraege += [einzelvariante, einzelvariante + ' (fit)'];
      stylelist += [[oedo['dunkelskala'][idx_var], 'None', 'o'], [oedo['farbskala ' + str(idx_var)][0], '-', 'None']];
   #
   if (len(xdaten) == 0):
      print('# Warnung: Keine Eintraege aus boden extrahiert');
      return None;
   #
   oedo.update([('xdaten', xdaten)]);
   oedo.update([('ydaten', ydaten)]);
   oedo.update([('legendeneintraege', legendeneintraege)]);
   oedo.update([('stylelist', stylelist)]);
   oedo.update([('xlabel', xparam)]);
   oedo.update([('ylabel', yparam)]);
   oedo.update([('xscale', 'log')]);
   oedo.update([('yflip', True)]);
   return oedo;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenTriaxPQ(boden, xparam, yparam):
   """Bereitet eine Struktur fuer die Plotdaten eines Triaxialversuchs mit speziellem Spannungspfad
   vor, die fuer einen Plot mit TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden
   anhand der Daten in boden, xparam und yparam extrahiert und gespeichert.
   Gibt die fertigen Plotdaten zurueck.
   """
   if ('Triax-p-q' not in boden):
      return None;
   #
   triax = PlotvorlageVorbereiten(typ='Triax-p-q');
   if (yparam == 'Hauptspannungsdifferenz [kN/m^2]'):
      if ((xparam != 'Druck-isotrop-eff [kN/m^2]') and (xparam != 'Stauchung [mm]')):
         print('# Warnung: Plot fuer angeforderten xparam/yparam nicht implementiert');
         return None;
      #
      xdaten = [];
      ydaten = [];
      legendeneintraege = [];
      for idx_versuch in range(3):
         pqvariante = 'Versuch ' + str(idx_versuch+1);
         try:
            xdaten += [boden['Triax-p-q'][pqvariante][xparam]];
            ydaten += [boden['Triax-p-q'][pqvariante][yparam]];
            legendeneintraege += [boden['Triax-p-q'][pqvariante]['Spannungspfad']];
         except:
            print('# Warnung: \'' + xparam + '\', \'' + yparam + '\'  oder/und \'Spannungspfad\' nicht in boden gefunden');
            return None;
         #
      #
      stylelist = [[triax['farbskala 0'][idx], '-', 'None'] for idx in range(3)];
   #
   elif (xparam == 'Dehnung [-]'):
      if ((yparam != 'E-Modul [kN/m^2]') and (yparam != 'q/2 [kN/m^2]')):
         print('# Warnung: Plot fuer angeforderten xparam/yparam nicht implementiert');
         return None;
      #
      legendeneintraege = [];
      eps = [];
      q = [];
      epsglatt = [];
      qglatt = [];
      emodulglatt = [];
      R = [];
      versatz = [];
      E_max = [];
      try:
         hoehe = boden['Triax-p-q']['4-Nach Konsolidation']['Hoehe [mm]'][-1];
      except:
         print('# Warnung: Benoetigter Eintrag \'Hoehe [mm]\' nicht in boden gefunden');
         return None;
      #
      for idx_versuch in range(3):
         pqvariante = 'Versuch ' + str(idx_versuch+1);
         try:
            tempschritte = boden['Triax-p-q'][pqvariante]['Schritte'];
            tempstauchung = boden['Triax-p-q'][pqvariante]['Stauchung [mm]'];
            tempq = boden['Triax-p-q'][pqvariante]['Hauptspannungsdifferenz [kN/m^2]'];
            #
            epsglatt += [boden['Triax-p-q'][pqvariante]['Glaettung']['Dehnung [-]']];
            qglatt += [boden['Triax-p-q'][pqvariante]['Glaettung']['q/2 [kN/m^2]']];
            #
            emodulglatt += [boden['Triax-p-q'][pqvariante]['Glaettung']['E-Modul [kN/m^2]']];
            R += [boden['Triax-p-q'][pqvariante]['Glaettung']['R [-]']];
            versatz += [boden['Triax-p-q'][pqvariante]['Glaettung']['Versatz']];
            E_max += [boden['Triax-p-q'][pqvariante]['Glaettung']['E-Modul-max [kN/m^2]']];
            legendeneintraege += [boden['Triax-p-q'][pqvariante]['Spannungspfad']];
         except:
            print('# Warnung: Benoetigte Eintraege zur p-q-Variante nicht in boden gefunden');
            return None;
         #
         startindex = tempschritte[-1];
         eps += [[(einzelstauchung - tempstauchung[startindex])/(hoehe - tempstauchung[startindex]) for einzelstauchung in tempstauchung[startindex:]]];
         q += [[qt/2.0 for qt in tempq[startindex:]]];
      #
      try:
         eps_som = boden['Triax-p-q']['Parameter']['eps_som [-]'];
      except:
         print('# Warnung: Benoetigter Eintrag \'eps_som [-]\' nicht gefunden');
         return None;
      #
      if (yparam == 'E-Modul [kN/m^2]'):
         xdaten = epsglatt + [[epsglatt[2][0], R[2]]] + [[eps_som, eps_som]];
         ydaten = emodulglatt + [[E_max[2], E_max[2]]] + [[0.0, min(E_max)]];
         stylelist = [[triax['farbskala 0'][idx], '-', 'None'] for idx in range(3)] + \
                      [[triax['farbskala 1'][2], '-', 'x']] + \
                      [[triax['dunkelskala'][0], '--', 'None']];
         legendeneintraege += [None, None];
         triax.update([('xscale', 'log')]);
      else:
         xdaten = eps + epsglatt + [[epsglatt[idx][0], R[idx]] for idx in range(3)];
         ydaten = q + qglatt + [[epsglatt[idx][0]*E_max[idx] + versatz[idx], R[idx]*E_max[idx] + versatz[idx]] for idx in range(3)];
         stylelist = [[triax['dunkelskala'][idx], '-', 'None'] for idx in range(3)] + \
                     [[triax['farbskala 0'][idx], '-', 'None'] for idx in range(3)] + \
                     [[triax['farbskala 1'][idx], '--', 'x'] for idx in range(3)];
         legendeneintraege = [None, None, None] + legendeneintraege + [None, None, None];
         triax.update([('legendenposition', 'lower right')]);
         extra_text = [[str(round(E_max[2])) + 'kPa', 2.0*R[2], E_max[2]]];
         triax.update([('textfelder', extra_text)]);
   #
   else:
      print('# Warnung: Plot fuer angeforderten xparam/yparam nicht implementiert');
      return None;
   #
   triax.update([('xdaten', xdaten)]);
   triax.update([('ydaten', ydaten)]);
   triax.update([('legendeneintraege', legendeneintraege)]);
   triax.update([('stylelist', stylelist)]);
   triax.update([('xlabel', xparam)]);
   triax.update([('ylabel', yparam)]);
   return triax;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenTriaxMC(boden, varianten, kreise=True, kohaesion=False):
   """Bereitet eine Struktur fuer die Plotdaten des Spannungsfeld eines Triaxialversuchs vor,
   die fuer einen Plot mit TkPlot oder EmbeddedPlot genutzt wird.
   Relevante Daten fuer die Bruchgerade oder Mohrschen Spannungskreise werden anhand der Daten
   in boden und varianten extrahiert und gespeichert. Falls kreise=True werden die Daten fuer
   die Mohrschen Spannungskreise bereitgestellt. Fuer die Ausgleichsgerade wird abhaengig von
   kohaesion ein vertikales Offset beruecksichtigt (oder nicht). Gibt die fertigen Plotdaten zurueck.
   """
   from math import sin, cos, tan
   from .konstanten import grad2rad
   from .gleichungsloeser import NaechsterWert
   #
   triax = PlotvorlageVorbereiten(typ='Triax');
   if (kreise):
      xparam = 'Sigma_prime [kPa]';
      yparam = 'Tau_prime [kPa]';
   else:
      xparam = '(sig_1prime + sig_3prime)/2.0 [kN/m^2]';
      yparam = '(sig_1 - sig_3)/2.0 [kN/m^2]';
   #
   xdaten = [];
   ydaten = [];
   legendeneintraege = [];
   stylelist = [];
   for idx_var, einzelvariante in enumerate(varianten):
      if (einzelvariante not in boden):
         continue;
      #
      punkte = [];
      for idx_triax in range(3):
         versuchsname = 'Versuch ' + str(idx_triax + 1);
         if (versuchsname not in boden[einzelvariante]):
            print('# Hinweis: Versuch ' + str(idx_triax) + ' nicht gefunden');
            break;
         #
         try:
            sigma1p = boden[einzelvariante][versuchsname]['Peakzustand']['Sigma_1_prime [kN/m^2]'];
            sigma3p = boden[einzelvariante][versuchsname]['Peakzustand']['Sigma_3_prime [kN/m^2]'];
            sigma3 = boden[einzelvariante][versuchsname]['Radialdruck [kN/m^2]'];
         except:
            print('# Warnung: Benoetigte Eintraege zum Peakzustand oder \'Radialdruck [kN/m^2]\' nicht in boden gefunden');
            return None;
         #
         sigma3_gerundet = int(round(sum(sigma3)/len(sigma3)/5.0)*5.0);
         #
         if (kreise):
            xdaten += [[(sigma1p+sigma3p)/2.0 - cos(winkel*grad2rad)*(sigma1p-sigma3p)/2.0 for winkel in range(181)]];
            ydaten += [[sin(winkel*grad2rad)*(sigma1p-sigma3p)/2.0 for winkel in range(181)]];
            legendeneintraege += [einzelvariante + ' ' + str(sigma3_gerundet) + 'kPa'];
            stylelist += [[triax['farbskala ' + str(idx_var)][idx_triax], '-', 'None']];
         else:
            try:
               xwerte = boden[einzelvariante][versuchsname][xparam];
               ywerte = boden[einzelvariante][versuchsname][yparam];
            except:
               print('# Warnung: \'' + xparam + '\' oder/und \'' + yparam + '\' nicht in boden gefunden');
               return None;
            #
            xdaten += [[0.0, (sigma1p+sigma3p)/2.0, (sigma1p+sigma3p)/2.0], xwerte, [(sigma1p+sigma3p)/2.0]];
            ydaten += [[(sigma1p-sigma3p)/2.0, (sigma1p-sigma3p)/2.0, 0.0], ywerte, [(sigma1p-sigma3p)/2.0]];
            punkte += [((sigma1p+sigma3p)/2.0, (sigma1p-sigma3p)/2.0)];
            legendeneintraege += [None, einzelvariante + ' ' + str(sigma3_gerundet) + 'kPa', None];
            stylelist += [[triax['dunkelskala'][idx_triax], '--', 'None'],
                          [triax['farbskala ' + str(idx_var)][idx_triax], '-', 'x'],
                          [triax['dunkelskala'][0], '-', 'x']];
      #
      if (kohaesion):
         try:
            offset = boden[einzelvariante]['Mohr-Coulomb']['Mit Kohaesion']['Kohaesion [kN/m^2]'];
            reibungswinkel = boden[einzelvariante]['Mohr-Coulomb']['Mit Kohaesion']['Reibungswinkel-eff [Grad]'];
         except:
            print('# Warnung: Benoetigte Eintraege zu Mohr-Coulomb nicht in boden gefunden');
            return None;
         #
         legendeneintraege += ['Fit phi=' + str(round(reibungswinkel*10.0)/10.0) + ' Grad, c=' \
            + str(round(offset*10.0)/10.0) + 'kPa'];
      else:
         offset = 0.0;
         try:
            reibungswinkel = boden[einzelvariante]['Mohr-Coulomb']['Ohne Kohaesion']['Reibungswinkel-eff [Grad]'];
         except:
            print('# Warnung: Benoetigte Eintraege zu Mohr-Coulomb nicht in boden gefunden');
            return None;
         #
         legendeneintraege += ['Fit phi=' + str(round(reibungswinkel*10.0)/10.0) + ' Grad'];
      #
      if (kreise):
         xmaxwert = max([max(werte) for werte in xdaten]) - 0.5*max([max(werte) for werte in ydaten]);
         xmaxwert = min(xmaxwert, (xmaxwert - offset)/tan(reibungswinkel*grad2rad));
         xdaten += [[0.0, xmaxwert]];
         ydaten += [[offset, offset + xmaxwert*tan(reibungswinkel*grad2rad)]];
      else:
         xmaxwert = max([max(werte) for werte in xdaten]);
         yoff = [einzelpunkt[1] - einzelpunkt[0]*sin(reibungswinkel*grad2rad) for einzelpunkt in punkte];
         offset = sum(yoff)/len(yoff);
         xdaten += [[0.0, xmaxwert]];
         ydaten += [[offset, offset + xmaxwert*sin(reibungswinkel*grad2rad)]];
      #
      stylelist += [[triax['dunkelskala'][idx_var], '-', 'None']];
   #
   if (len(xdaten) == 0):
      return None;
   #
   xmax = max([max(elem) for elem in xdaten]);
   xmax = NaechsterWert(wert=xmax, spanne=xmax, aufsteigend=True);
   triax.update([('xlim', [0.0, xmax])]);
   triax.update([('ylim', [0.0, 16.5/15.1*xmax])]); # Verhaeltnis der Axes/Figure Groessen fuer 1:1 Verhaeltnis
   #
   triax.update([('xdaten', xdaten)]);
   triax.update([('ydaten', ydaten)]);
   triax.update([('legendeneintraege', legendeneintraege)]);
   triax.update([('legendenposition', 'upper left')]);
   triax.update([('stylelist', stylelist)]);
   triax.update([('xlabel', xparam)]);
   triax.update([('ylabel', yparam)]);
   return triax;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenTriaxD(boden, varianten, yparam='delta V/V_0 [%]'):
   """Bereitet eine Struktur fuer die Plotdaten eines drainierten Triaxialversuchs vor, die fuer
   einen Plot mit TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden anhand der Daten
   in boden und varianten extrahiert und gespeichert. Die y-Variable kann mit yparam gewaehlt 
   werden (sofern sie in boden[einzelvarianten] fuer alle einzelvarianten in varianten existiert).
   Gibt die fertigen Plotdaten zurueck.
   """
   from math import tan
   from .konstanten import grad2rad
   #
   triax = PlotvorlageVorbereiten(typ='Triax-D');
   xparam = 'Dehnung [%]';
   xdaten = [];
   ydaten = [];
   legendeneintraege = [];
   stylelist = [];
   legendenposition = 'lower right';
   extra_xwerte = [];
   extra_ywerte = [];
   extra_style = [];
   extra_text = [];
   for idx_var, einzelvariante in enumerate(varianten):
      if (einzelvariante not in boden):
         continue;
      #
      for idx_triax in range(3):
         versuchsname = 'Versuch ' + str(idx_triax + 1);
         if (versuchsname not in boden[einzelvariante]):
            print('# Hinweis: Versuch ' + str(idx_triax + 1) + ' nicht gefunden');
            break;
         #
         try:
            x_temp = boden[einzelvariante][versuchsname][xparam];
            y_temp = boden[einzelvariante][versuchsname][yparam];
         except:
            print('# Warnung: \'' + xparam + '\' oder/und \'' + yparam + '\' nicht in boden gefunden');
            return None;
         #
         #
         xdaten += [x_temp];
         ydaten += [y_temp];
         #
         if (yparam == 'delta V/V_0 [%]'):
            try:
               idx_peak = boden[einzelvariante][versuchsname]['Peakzustand']['Index'];
               geradenwinkel = boden[einzelvariante][versuchsname]['Peakzustand']['Geradenwinkel [Grad]'];
               dilatanzwinkel = boden[einzelvariante][versuchsname]['Peakzustand']['Dilatanzwinkel [Grad]'];
            except:
               print('# Warnung: Benoetigte Eintraege zum Peakzustand nicht in boden gefunden');
               return None;
            #
            if ('dicht' in einzelvariante):
               xstuetz = [0.5, 10.0];
            else:
               xstuetz = [0.5, 20.0];
            #
            ystuetz = [ydaten[-1][idx_peak] - (xdaten[-1][idx_peak] - xstuetz[0])*tan(geradenwinkel*grad2rad),
                       ydaten[-1][idx_peak] + (xstuetz[1] - xdaten[-1][idx_peak])*tan(geradenwinkel*grad2rad)];
            extra_xwerte += [xstuetz, xdaten[-1][idx_peak]];
            extra_ywerte += [ystuetz, ydaten[-1][idx_peak]];
            extra_style += [[triax['dunkelskala'][idx_triax], '-', 'None'], [triax['dunkelskala'][idx_triax], '', 'x']];
         elif (yparam == '(sig_1 - sig_3)/2.0 [kN/m^2]'):
            try:
               idx_peak = boden[einzelvariante][versuchsname]['Peakzustand']['Index'];
            except:
               print('# Warnung: Benoetigte Eintraege zum Peakzustand nicht in boden gefunden');
               return None;
            #
            extra_xwerte += [xdaten[-1][idx_peak]];
            extra_ywerte += [ydaten[-1][idx_peak]];
            extra_text += [[str(round(10.0*ydaten[-1][idx_peak])/10.0) + 'kPa', xdaten[-1][idx_peak]+3.5, ydaten[-1][idx_peak]-10]]; # Nur seitlich vom Peak
            #extra_text += [[str(round(10.0*ydaten[-1][idx_peak])/10.0) + 'kPa', xdaten[-1][idx_peak]+1.5, ydaten[-1][idx_peak]+25]];
            extra_style += [[triax['dunkelskala'][idx_triax], '', 'x']];
         elif ((yparam == 'Porenzahl [-]') or (yparam == 'Reibungswinkel [Grad]')):
            pass;
         else:
            print('# Warnung: Plot fuer angeforderten yparam nicht implementiert');
            return None;
         #
         try:
            sigma3 = boden[einzelvariante][versuchsname]['Radialdruck [kN/m^2]'];
         except:
            print('# Warnung: Benoetigter Eintrag \'Radialdruck [kN/m^2]\' nicht in boden gefunden');
            return None;
         #
         sigma3_gerundet = int(round(sum(sigma3)/len(sigma3)/5.0)*5.0);
         legendeneintraege += [einzelvariante + ' ' + str(sigma3_gerundet) + 'kPa'];
         stylelist += [[triax['farbskala ' + str(idx_var)][idx_triax], '-', 'None']];
   #
   if (len(xdaten) == 0):
      return None;
   #
   if (yparam == 'delta V/V_0 [%]'):
      xdaten = extra_xwerte + xdaten;
      ydaten = extra_ywerte + ydaten;
      stylelist = extra_style + stylelist;
      legendeneintraege = [None for idx in range(len(extra_xwerte))] + legendeneintraege;
   elif (yparam == '(sig_1 - sig_3)/2.0 [kN/m^2]'):
      xdaten = xdaten + extra_xwerte;
      ydaten = ydaten + extra_ywerte;
      stylelist = stylelist + extra_style;
      legendeneintraege = legendeneintraege + [None for idx in range(len(extra_xwerte))];
      triax.update([('textfelder', extra_text)]);
   #
   triax.update([('xdaten', xdaten)]);
   triax.update([('ydaten', ydaten)]);
   triax.update([('legendeneintraege', legendeneintraege)]);
   triax.update([('legendenposition', 'lower right')]);
   triax.update([('stylelist', stylelist)]);
   triax.update([('xlabel', xparam)]);
   triax.update([('ylabel', yparam)]);
   return triax;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenTriaxCU(boden, yparam='(sig_1 - sig_3)/2.0 [kN/m^2]'):
   """Bereitet eine Struktur fuer die Plotdaten eines undrainierten Triaxialversuchs vor, die fuer
   einen Plot mit TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden anhand der Daten
   in boden extrahiert und gespeichert. Die y-Variable kann mit yparam gewaehlt werden (sofern sie
   in boden[einzelvarianten] existiert). Gibt die fertigen Plotdaten zurueck.
   """
   from math import tan
   from .konstanten import grad2rad
   #
   if ('Triax-CU' not in boden):
      return None;
   #
   triax = PlotvorlageVorbereiten(typ='Triax-CU');
   xparam = 'Dehnung [%]';
   xdaten = [];
   ydaten = [];
   legendeneintraege = [];
   stylelist = [];
   for idx_triax in range(3):
      versuchsname = 'Versuch ' + str(idx_triax + 1);
      if (versuchsname not in boden['Triax-CU']):
         print('# Hinweis: Versuch ' + str(idx_triax + 1) + ' nicht gefunden');
         break;
      #
      try:
         x_temp = boden['Triax-CU'][versuchsname][xparam];
         y_temp = boden['Triax-CU'][versuchsname][yparam];
      except:
         print('# Warnung: \'' + xparam + '\' oder/und \'' + yparam + '\' nicht in boden gefunden');
         return None;
      #
      xdaten += [x_temp];
      ydaten += [y_temp];
      #
      try:
         sigma3 = boden['Triax-CU'][versuchsname]['Radialdruck [kN/m^2]'];
      except:
         print('# Warnung: Benoetigter Eintrag \'Radialdruck [kN/m^2]\' nicht in boden gefunden');
         return None;
      #
      sigma3_gerundet = int(round(sum(sigma3)/len(sigma3)/5.0)*5.0);
      legendeneintraege += ['Triax-CU ' + str(sigma3_gerundet) + 'kPa'];
      stylelist += [[triax['farbskala 1'][idx_triax], '-', 'None']];
      #
      if ((yparam == '(sig_1 - sig_3)/2.0 [kN/m^2]') or (yparam == 'Porenwasserdruck-Delta [kN/m^2]')):
         pass;
      elif (yparam == 'sig1_prime/sig3_prime [-]'):
         try:
            idx_peak = boden['Triax-CU'][versuchsname]['Peakzustand']['Index'];
         except:
            print('# Warnung: Benoetigter Eintrag zum Peakzustand nicht in boden gefunden');
            return None;
         #
         xdaten += [[xdaten[-1][idx_peak], xdaten[-1][idx_peak]]];
         ydaten += [[1.0, ydaten[-1][idx_peak]]];
         legendeneintraege += [None];
         stylelist += [[triax['dunkelskala'][idx_triax], '-', 'None']];
      else:
         print('# Warnung: Plot fuer angeforderten yparam nicht implementiert');
         return None;
   #
   triax.update([('xdaten', xdaten)]);
   triax.update([('ydaten', ydaten)]);
   triax.update([('legendeneintraege', legendeneintraege)]);
   triax.update([('legendenposition', 'lower right')]);
   triax.update([('stylelist', stylelist)]);
   triax.update([('xlabel', xparam)]);
   triax.update([('ylabel', yparam)]);
   return triax;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenKVS(boden):
   """Bereitet eine Struktur fuer die Plotdaten einer Koernungsverteilung vor, die fuer
   einen Plot mit TkPlot oder EmbeddedPlot genutzt wird. Relevante Daten werden anhand der Daten
   in boden extrahiert und gespeichert. Es werden die Datensaetze aus bis zu acht Schluesseln in
   boden fuer die Erstellung der Plotdaten verwendet. Gibt die fertigen Plotdaten zurueck.
   """
   if ('Kornverteilung' not in boden):
      return None;
   #
   kvs = PlotvorlageVorbereiten(typ='KVS');
   xdaten = [];
   ydaten = [];
   legendeneintraege = [];
   zwischenpunkte = [];
   # Eine Dummy-Stylelist erstellen, damit die Zuordnung bei VordefinierteMultiPlots ohne zusaetzliche
   # Anpassungen funktioniert
   stylelist = [];
   #
   for idx_kvs in range(8):
      kvsname = 'Sieblinie ' + str(idx_kvs + 1);
      if (kvsname not in boden['Kornverteilung']):
         break;
      #
      try:
         x_temp = boden['Kornverteilung'][kvsname]['Interpolation']['Siebdurchmesser [mm]'];
         y_temp = boden['Kornverteilung'][kvsname]['Interpolation']['Summierte Masseanteile Gesamtmenge [%]'];
         temp_zwischenpunkte = boden['Kornverteilung'][kvsname]['Interpolation']['Interpolationspunkte [-]'];
      except:
         print('# Warnung: \'' + xparam + '\', \'' + yparam + '\' oder/und zur Interpolationsdaten nicht in boden gefunden');
         return None;
      #
      xdaten += [x_temp];
      ydaten += [y_temp];
      stylelist += [[kvs['dunkelskala'][0], '-', 'None']];
      zwischenpunkte += [temp_zwischenpunkte];
      #
      tiefe = boden['Kornverteilung'][kvsname]['Tiefe'];
      if (tiefe == '') or (tiefe == '-'):
         tiefe = '';
      else:
         tiefe = ' ' + tiefe;
      #
      if ('Ungleichfoermigkeitszahl [-]' in boden['Kornverteilung'][kvsname]['Interpolation']):
         try:
            temp_legendeneintrag = boden['Kornverteilung'][kvsname]['Entnahmestelle'] + tiefe + ': U=' \
            + str(boden['Kornverteilung'][kvsname]['Interpolation']['Ungleichfoermigkeitszahl [-]']) \
            + ', Cc=' + str(boden['Kornverteilung'][kvsname]['Interpolation']['Kruemmungszahl [-]']);
         except:
            print('# Warnung: Benoetigte Eintraege zur Interpolation nicht in boden gefunden');
            return None;
         #
         legendeneintraege += [temp_legendeneintrag];
      else:
         try:
            temp_legendeneintrag = boden['Kornverteilung'][kvsname]['Entnahmestelle'] + tiefe;
         except:
            print('# Warnung: Benoetigter Eintrag \'Entnahmestelle\' nicht in boden gefunden');
            return None;
            
         legendeneintraege += [temp_legendeneintrag];
   #
   if ( 'Sieblinie ' + str(idx_kvs + 2) in boden['Kornverteilung']):
      print('# Konnte nicht alle Sieblinien zeichnen');
   #
   kvs.update([('xdaten', xdaten)]);
   kvs.update([('ydaten', ydaten)]);
   kvs.update([('legendeneintraege', legendeneintraege)]);
   kvs.update([('legendenposition', 'lower right')]);
   kvs.update([('stylelist', stylelist)]);
   kvs.update([('xlabel', 'Siebdurchmesser [mm]')]);
   kvs.update([('ylabel', 'Summierte Masseanteile Gesamtmenge [%]')]);
   kvs.update([('xscale', 'log')]);
   kvs.update([('zwischenpunkte', zwischenpunkte)]);
   return kvs;
#


# -------------------------------------------------------------------------------------------------
def PlotdatenAusSchluesselbegriff(boden, schluesselbegriff):
   """Bereite Plotdaten zu einem boden anhand eines uebergebenen schluesselbegriff vor und gebe
   diese zurueck.
   """
   plotname_klein = schluesselbegriff.lower();
   if ('oedo-crs-visko' in plotname_klein):
      yparam = 'Porenzahl [-]';
      yflip = False;
      if ('setzung' in plotname_klein):
         yparam = 'eps [%]'
         yflip = True;
      #
      plotdaten = PlotdatenOedoCRS(boden=boden, varianten=['Visko'], yparam=yparam, yflip=yflip);
   #
   elif ('oedo-crs' in plotname_klein):
      versuchsvarianten = [];
      if ('dicht' in plotname_klein):
         versuchsvarianten += ['Oedo-dicht'];
      #
      if ('locker' in plotname_klein):
         versuchsvarianten += ['Oedo-locker'];
      #
      if (versuchsvarianten == []):
         print('# Hinweis: Oedo-CRS muss dicht oder/und locker im Plotnamen haben');
         return None;
      #
      yparam = 'Porenzahl [-]';
      yflip = False;
      if ('stauchung' in plotname_klein):
         yparam = 'Stauchung [%]'
         yflip = True;
      #
      plotdaten = PlotdatenOedoCRS(boden=boden, varianten=versuchsvarianten, yparam=yparam, yflip=yflip);
   #
   elif ('oedo-crl' in plotname_klein):
      if ('fit' in plotname_klein):
         plotdaten = PlotdatenOedo(boden=boden, varianten=['Oedo-CRL']);
      else:
         kurve = 0;
         if (('wurzel' in plotname_klein) or ('sqrt(' in plotname_klein)):
            variante = 'wurzel';
         elif (('logarithm' in plotname_klein) or ('log(' in plotname_klein) or ('log10(' in plotname_klein)):
            variante = 'log';
         elif ('porenzahl' in plotname_klein):
            variante = 'porenzahl';
         else:
            print('# Hinweis: Unbekanntes/fehlendes Schlagwort fuer Oedo-CRL im Plotnamen');
            print('# Erwartet eines von: Fit, Wurzel, Logarithmus, Porenzahl');
            return None;
         #
         if ('laststufe 1' in plotname_klein):
            kurve = 1;
         elif ('laststufe 2' in plotname_klein):
            kurve = 2;
         elif ('laststufe 3' in plotname_klein):
            kurve = 3;
         elif ('laststufe 4' in plotname_klein):
            kurve = 4;
         elif ('laststufe 5' in plotname_klein):
            kurve = 5;
         elif ('laststufe 6' in plotname_klein):
            kurve = 6;
         elif ('laststufe 7' in plotname_klein):
            kurve = 7;
         elif ('laststufe 8' in plotname_klein):
            kurve = 8;
         #
         plotdaten = PlotdatenOedoCRL(boden=boden, variante=variante, kurve=kurve);
   #
   elif ('oedo' in plotname_klein):
      versuchsvarianten = [];
      if ('dicht' in plotname_klein):
         versuchsvarianten += ['Oedo-dicht'];
      #
      if ('locker' in plotname_klein):
         versuchsvarianten += ['Oedo-locker'];
      #
      if (versuchsvarianten == []):
         print('# Hinweis: Oedo muss dicht oder/und locker im Plotnamen haben');
         return None;
      #
      plotdaten = PlotdatenOedo(boden=boden, varianten=versuchsvarianten);
   #
   elif ('triax-d' in plotname_klein):
      versuchsvarianten = [];
      if ('dicht' in plotname_klein):
         versuchsvarianten += ['Triax-D-dicht'];
      #
      if ('locker' in plotname_klein):
         versuchsvarianten += ['Triax-D-locker'];
      #
      if (versuchsvarianten == []):
         print('# Hinweis: Triax-D muss dicht oder/und locker im Plotnamen haben');
         return None;
      #
      mc = False;
      kreise = False;
      if ('volume' in plotname_klein):
         yparam = 'delta V/V_0 [%]';
      elif ('reibungswinkel' in plotname_klein):
         yparam = 'Reibungswinkel [Grad]';
      elif ('porenzahl' in plotname_klein):
         yparam = 'Porenzahl [-]';
      elif ('mittelspannung' in plotname_klein):
         yparam = '(sig_1 - sig_3)/2.0 [kN/m^2]';
      elif (('eff' in plotname_klein) and ('mitt' in plotname_klein) and ('spannung' in plotname_klein)):
         mc = True;
         kreise = False;
      elif ('bruchgerade' in plotname_klein):
         mc = True;
         kreise = False;
      elif (('mohr' in plotname_klein) or ('spannungskreis' in plotname_klein)):
         mc = True;
         kreise = True;
      else:
         print('# Hinweis: Unbekanntes/fehlendes Schlagwort fuer Triax-D im Plotnamen');
         print('# Normaler Triax-D: Volumen, Reibungswinkel, Porenzahl, Mittelspannung');
         print('# Mohr-Coulomb-Daten Triax-D: eff. mittlere Spannung, Bruchgerade, Spannungskreis, Mohr');
         return None;
      #
      if (mc):
         plotdaten = PlotdatenTriaxMC(boden=boden, varianten=versuchsvarianten, kreise=kreise, kohaesion=False);
      else:
         plotdaten = PlotdatenTriaxD(boden=boden, varianten=versuchsvarianten, yparam=yparam);
   #
   elif ('triax-cu' in plotname_klein):
      mc = False;
      kreise = False;
      if ('hauptspannungsverhaeltnis' in plotname_klein):
         yparam = 'sig1_prime/sig3_prime [-]';
      elif ('mittelspannung' in plotname_klein):
         yparam = '(sig_1 - sig_3)/2.0 [kN/m^2]';
      elif ('porenwasserdruck' in plotname_klein):
         yparam = 'Porenwasserdruck-Delta [kN/m^2]';
      elif (('eff' in plotname_klein) and ('mitt' in plotname_klein) and ('spannung' in plotname_klein)):
         mc = True;
         kreise = False;
      elif ('bruchgerade' in plotname_klein):
         mc = True;
         kreise = False;
      elif (('mohr' in plotname_klein) or ('spannungskreis' in plotname_klein)):
         mc = True;
         kreise = True;
      else:
         print('# Hinweis: Unbekanntes/fehlendes Schlagwort fuer Triax-CU im Plotnamen');
         print('# Normaler Triax-CU: hauptspannungsverhaeltnis, Mittelspannung, Porenwasserdruck');
         print('# Mohr-Coulomb-Daten Triax-CU: eff. mittlere Spannung, Bruchgerade, Spannungskreis, Mohr');
         return None;
      #
      if (mc):
         plotdaten = PlotdatenTriaxMC(boden=boden, varianten=['Triax-CU'], kreise=kreise, kohaesion=True);
      else:
         plotdaten = PlotdatenTriaxCU(boden=boden, yparam=yparam);
   #
   elif ('triax-p-q' in plotname_klein):
      xparam = 'Dehnung [-]';
      yparam = 'Hauptspannungsdifferenz [kN/m^2]';
      #
      if ('dehnung' in plotname_klein):
         yparam = 'q/2 [kN/m^2]';
      elif ('modul' in plotname_klein):
         yparam = 'E-Modul [kN/m^2]';
      elif ('stauchung' in plotname_klein):
         xparam = 'Stauchung [mm]';
      else:
         xparam = 'Druck-isotrop-eff [kN/m^2]';
      #
      plotdaten = PlotdatenTriaxPQ(boden=boden, xparam=xparam, yparam=yparam);
   #
   elif (('kvs' in plotname_klein) or ('kornverteilung' in plotname_klein) or ('sieblinie' in plotname_klein)):
      plotdaten = PlotdatenKVS(boden);
   else:
      print('# Hinweis: Schluesselwoerter im Plotnamen nicht erkannt/nicht implementiert');
      return None;
   #
   return plotdaten;
#


# -------------------------------------------------------------------------------------------------
def VordefinierteMultiPlots(boden, plotname, figure=None):
   """Plottet alle Datensaetze aus boden anhand von Schluesselwoertern in plotname. Aehnlich wie
   VordefiniertePlots(), aber fuer viele Bodensaetze in boden statt nur einem.
   """
   multifarben = ['#a83c66', '#a248a8', '#7d67d4', '#5391d5', '#3fb7af', '#52cb7b', '#88c95a',
                  '#c9b960', '#faab8d', '#ffaaca'];
   plotdaten = None;
   idx_farbe = 0;
   for bodenschluessel in boden.keys():
      temp_plotdaten = PlotdatenAusSchluesselbegriff(boden=boden[bodenschluessel],
         schluesselbegriff=plotname);
      if (temp_plotdaten is None):
         continue;
      #
      temp_style = temp_plotdaten['stylelist'];
      temp_legende = temp_plotdaten['legendeneintraege'];
      neu_style = [];
      neu_legende = [];
      for cur_style, cur_legend in zip(temp_style, temp_legende):
         if (cur_legend is not None):
            neu_legende += [bodenschluessel + ' ' + cur_legend];
            cur_style[0] = multifarben[idx_farbe % len(multifarben)];
            idx_farbe += 1;
         else:
            neu_legende += [None];
         #
         neu_style += [cur_style];
      #
      if (plotdaten is None):
         # Alle wichtigen Eigenschaften von dem ersten Satz an plotdaten uebernehmen
         plotdaten = temp_plotdaten;
         plotdaten['legendeneintraege'] = neu_legende;
         plotdaten['stylelist'] = neu_style;
      else:
         plotdaten['xdaten'] = plotdaten['xdaten'] + temp_plotdaten['xdaten'];
         plotdaten['ydaten'] = plotdaten['ydaten'] + temp_plotdaten['ydaten'];
         plotdaten['textfelder'] = plotdaten['textfelder'] + temp_plotdaten['textfelder'];
         plotdaten['legendeneintraege'] = plotdaten['legendeneintraege'] + neu_legende;
         plotdaten['stylelist'] = plotdaten['stylelist'] + neu_style;
         #
         xlim = plotdaten['xlim'];
         if (len(xlim) > 0):
            # Wenn fuer eines vorhanden, wird fuer alle eins vorhanden sein
            if ((xlim[0] > temp_plotdaten['xlim'][0]) or (xlim[1] < temp_plotdaten['xlim'][1])):
               plotdaten['xlim'] = [min(xlim[0], temp_plotdaten['xlim'][0]), max(xlim[1], temp_plotdaten['xlim'][1])];
         #
         ylim = plotdaten['ylim'];
         if (len(ylim) > 0):
            # Wenn fuer eines vorhanden, wird fuer alle eins vorhanden sein
            if ((ylim[0] > temp_plotdaten['ylim'][0]) or (ylim[1] < temp_plotdaten['ylim'][1])):
               plotdaten['ylim'] = [min(ylim[0], temp_plotdaten['ylim'][0]), max(ylim[1], temp_plotdaten['ylim'][1])];
         #
         if ('zwischenpunkte' in plotdaten):
            plotdaten['zwischenpunkte'] = plotdaten['zwischenpunkte'] + temp_plotdaten['zwischenpunkte'];
   #
   if (plotdaten is None):
      return;
   #
   plotdaten.update([('title', plotname)]);
   if (figure is None):
      TkPlot(plotdaten=plotdaten);
   else:
      EmbeddedPlot(plotdaten=plotdaten, figure=figure);
#


# -------------------------------------------------------------------------------------------------
def VordefiniertePlots(boden, plotname, figure=None):
   """Plottet einen Datensatz aus boden, der anhand von Schluesselwoertern in plotname ausgewaehlt
   wird. Falls keine figure uebergeben wird, wird ein neues Fenster erstellt, in dem geplottet wird.
   Andernfalls wird die uebergebene figure als Leinwand fuer den ausgewaehlten Plot verwendet.
   Schluesselwoerter fuer plotname setzen sich aus einem Freitext aus der Versuchsbezeichnung
   (wie er auch in der boden-Struktur gespeichert ist), der Lagerungsdichte und evtl. weiteren
   Begriffen zusammen. Beispielsweise werden aus
   plotname='dichter Oedo-CRS' oder plotname='Oedo-CRS-Versuch (dichte Lagerung)'
   jeweils die gleichen Schluesselwoerter 'dicht' und 'Oedo-CRS' fuer die Auswahl des Plots
   extrahiert.
   """
   plotdaten = PlotdatenAusSchluesselbegriff(boden=boden, schluesselbegriff=plotname);
   if (plotdaten is None):
      return;
   #
   plotdaten.update([('title', plotname)]);
   if (figure is None):
      TkPlot(plotdaten=plotdaten);
   else:
      EmbeddedPlot(plotdaten=plotdaten, figure=figure);
#


# -------------------------------------------------------------------------------------------------
def _SieblinienPlot(figure, plotdaten):
   """Erstelle auf Basis der Daten zu einer oder mehr Koernungsverteilungen in plotdaten einen
   Plot nach einem festen vordefinierten Schema, der auf der uebergebenen figure ausgegeben wird.
   Die plotdaten solten auf das Resultat von PlotdatenKVS() aufbauen, damit alle erforderlichen
   Schluessel in der plotdaten-Struktur existieren.
   """
   import matplotlib
   from math import floor, log10
   #
   axis = figure.add_subplot(111);
   #
   xdaten = plotdaten['xdaten'];
   ydaten = plotdaten['ydaten'];
   stylelist = plotdaten['stylelist'];
   #
   # Fuege die Grobunterteilungen als Linien im Plot hinzu
   for x_unter in [0.002, 0.06, 2, 60]:
      axis.plot([x_unter, x_unter], [0.0, 100.0], color='#000000', linestyle='--',
         linewidth=0.5, label='_nolegend_');
   #
   Colors = [[0, 0, 1], [1, 0, 0], [0, 1, 0], [1, 0, 1], [0.5, 0, 0], [0.5, 0.5, 0], [0.5, 0, 1], [0, 0, 0]];
   Markers = ['o', 'x', 's', '+', '*', 'd', '^', 'v', 'None'];
   Linestyles = ['-', ':', '--'];
   #
   for idx_daten in range(len(xdaten)):
      axis.plot(xdaten[idx_daten], ydaten[idx_daten], color=Colors[idx_daten % len(Colors)],
         linestyle=Linestyles[int(idx_daten/len(Colors)) % len(Linestyles)],
         marker=Markers[idx_daten % len(Markers)], markevery=plotdaten['zwischenpunkte'][idx_daten],
         clip_on=False, zorder=10);
   #
   axis.grid(which='major', color='#808080',linestyle=':');
   axis.grid(which='minor', color='#dddddd', linestyle=':');
   axis.set_xscale(plotdaten['xscale']);
   axis.set_yscale(plotdaten['yscale']);
   #
   axis.set_xlim([0.001, 100.0]);
   axis.set_ylim([0, 100]);
   #
   axis.set_xlabel('Korndurchmesser d in mm', fontsize=11);
   axis.set_ylabel('Massenanteile der Körner < d in % der Gesamtmenge', fontsize=11);
   axis.set_xticks([0.001, 0.002, 0.006, 0.01, 0.02, 0.06, 0.1, 0.2, 0.6, 1.0, 2.0, 6.0, 10.0, 20.0, 60.0, 100.0]);
   axis.set_xticklabels([0.001, 0.002, '0.006  ', '  0.01', ' 0.02', 0.06, 0.1, 0.2, 0.6, 1, 2, 6, 10, 20, 60, 100]);
   axis.set_yticks([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]);
   axis.set_yticks([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]);
   for tick in axis.xaxis.get_major_ticks():
      tick.label.set_fontsize(11);
   #
   for tick in axis.yaxis.get_major_ticks():
      tick.label.set_fontsize(11);
   #
   axstart = [0.08, 0.1];
   axsize = [0.85, 0.65];
   axis.set_position([axstart[0], axstart[1], axsize[0], axsize[1]]);
   axis.legend(plotdaten['legendeneintraege'], loc=plotdaten['legendenposition']).set_zorder(15);
   #
   for counter in range(12):
      if ((counter == 0) or (counter == 4) or (counter == 11)):
         xoffset = 0;
         if (counter == 0):
            xoffset = -floor((counter-1.0)/2.0);
         else:
            if (counter == 4):
               xoffset = log10(6.0);
         #
         hoehe = 0.2;
      else:
         hoehe = 0.06;
         if ((counter % 2) == 0):
            xoffset = log10(6.0);
         else:
            xoffset = log10(2.0);
         #
         if ((counter == 1) or (counter == 7) or (counter == 10)):
            hoehe = 0.12;
      #
      axpos = axstart[0] + axsize[0]/5.0*(floor((counter-1.0)/2.0) + xoffset);
      newline = matplotlib.lines.Line2D([axpos, axpos], [axstart[1]+axsize[1], axstart[1]+axsize[1]+hoehe],
         transform=figure.transFigure, figure=figure, color='#000000', linewidth=0.5, zorder=0);
      figure.lines.extend([newline]);
   #
   newline = matplotlib.lines.Line2D([axstart[0], axstart[0]+axsize[0]],
      [axstart[1]+axsize[1]+0.12, axstart[1]+axsize[1]+0.12], transform=figure.transFigure,
      figure=figure, color='#000000', linewidth=0.5, zorder=0);
   figure.lines.extend([newline]);
   #
   ypos_schrifta = 103;
   ypos_schriftb = 113;
   ypos_schriftc = 125;
   schrifta_fsize = 9;
   schriftb_fsize = 10;
   schriftc_fsize = 12;
   #
   axis.text(0.0014, (ypos_schrifta+ypos_schriftb)/2, 'Feinstes', ha='center', fontsize=schrifta_fsize);
   axis.text(0.0035, ypos_schrifta, 'Fein-', ha='center', fontsize=schrifta_fsize);
   axis.text(0.0114, ypos_schrifta, 'Mittel-', ha='center', fontsize=schrifta_fsize);
   axis.text(0.035, ypos_schrifta, 'Grob-', ha='center', fontsize=schrifta_fsize);
   axis.text(0.012, ypos_schriftb, 'Schluffkorn', ha='center', fontsize=schriftb_fsize);
   axis.text(0.008, ypos_schriftc, 'Schlämmkorn', ha='center', fontsize=schriftc_fsize);
   #
   axis.text(0.114, ypos_schrifta, 'Fein-', ha='center', fontsize=schrifta_fsize);
   axis.text(0.35, ypos_schrifta, 'Mittel-', ha='center', fontsize=schrifta_fsize);
   axis.text(1.14, ypos_schrifta, 'Grob-', ha='center', fontsize=schrifta_fsize);
   axis.text(0.35, ypos_schriftb, 'Sandkorn', ha='center', fontsize=schriftb_fsize);
   #
   axis.text(3.5, ypos_schrifta, 'Fein-', ha='center', fontsize=schrifta_fsize);
   axis.text(11.2, ypos_schrifta, 'Mittel-', ha='center', fontsize=schrifta_fsize);
   axis.text(35.0, ypos_schrifta, 'Grob-', ha='center', fontsize=schrifta_fsize);
   axis.text(11.2, ypos_schriftb, 'Kieskorn', ha='center', fontsize=schriftb_fsize);
   axis.text(78.0, (ypos_schrifta+ypos_schriftb)/2, 'Steine', ha='center', fontsize=schrifta_fsize);
   axis.text(2.5, ypos_schriftc, 'Siebkorn', ha='center', fontsize=schriftc_fsize);
#


# -------------------------------------------------------------------------------------------------
def _NormalerPlot(figure, plotdaten):
   """Erstelle auf Basis der Daten in plotdaten einen Plot, der auf der uebergebenen figure
   ausgegeben wird. Die plotdaten solten auf das Resultat von PlotvorlageVorbereiten() aufbauen,
   damit alle relevanten Schluessel in der plotdaten-Struktur existieren, mit denen hier
   Anpassungen vorgenommen werden koennen (bspw. xdaten, xlabel, stylelist, ...).
   """
   import numpy
   import matplotlib
   #
   class SqrtScale(matplotlib.scale.ScaleBase):
      name = 'sqrt';
      #
      def __init__(self, axis, **kwargs):
         # FIXME: Python 3.6/3.7 Fix
         try:
            # Python 3.6 und entsprechende matplotlib-Version
            matplotlib.scale.ScaleBase.__init__(self);
         except:
            # Python 3.7 und entsprechende matplotlib-Version
            matplotlib.scale.ScaleBase.__init__(self, axis);
      def get_transform(self):
         return self.SqrtTransform();
      def set_default_locators_and_formatters(self, axis):
         axis.set_major_locator(matplotlib.ticker.AutoLocator());
         axis.set_major_formatter(matplotlib.ticker.ScalarFormatter());
         axis.set_minor_locator(matplotlib.ticker.NullLocator());
         axis.set_minor_formatter(matplotlib.ticker.NullFormatter());
      def limit_range_for_scale(self, vmin, vmax, minpos):
         return max(vmin, 0.0), vmax;
      #
      class SqrtTransform(matplotlib.transforms.Transform):
         input_dims = 1;
         output_dims = 1;
         is_separable = True;
         #
         def __init__(self):
            matplotlib.transforms.Transform.__init__(self);
         #
         def transform_non_affine(self, a):
            return numpy.sqrt(a);
         def inverted(self):
            return SqrtScale.InvertedSqrtTransform();
      #
      class InvertedSqrtTransform(matplotlib.transforms.Transform):
         input_dims = 1;
         output_dims = 1;
         is_separable = True;
         #
         def __init__(self):
            matplotlib.transforms.Transform.__init__(self);
         def transform_non_affine(self, a):
            return numpy.square(a);
         def inverted(self):
            return SqrtScale.SqrtTransform();
   #
   matplotlib.scale.register_scale(SqrtScale);
   #
   axis = figure.add_subplot(111);
   #
   xdaten = plotdaten['xdaten'];
   ydaten = plotdaten['ydaten'];
   stylelist = plotdaten['stylelist'];
   xlim = plotdaten['xlim'];
   ylim = plotdaten['ylim'];
   if (stylelist == []):
      stylelist = [['#808080', '-', 'None']];
   #
   for idx_daten in range(len(xdaten)):
      cur_style = stylelist[idx_daten % len(stylelist)];
      temp_label = plotdaten['legendeneintraege'][idx_daten];
      if (temp_label is None):
         temp_label = '_nolegend_';
      #
      axis.plot(xdaten[idx_daten], ydaten[idx_daten], color=cur_style[0], linestyle=cur_style[1],
         marker=cur_style[2], clip_on=False, label=temp_label, zorder=10);
   #
   axis.tick_params(direction='inout');
   axis.grid(which='major', linestyle=':');
   axis.grid(which='minor', color='#eeeeee', linestyle=':');
   axis.set_xscale(plotdaten['xscale']);
   axis.set_yscale(plotdaten['yscale']);
   #
   if (xlim != []):
      axis.set_xlim(xlim[0], xlim[1]);
   #
   if (ylim != []):
      axis.set_ylim(ylim[0], ylim[1]);
   #
   if (plotdaten['xflip']):
      axis.invert_xaxis();
   #
   if (plotdaten['yflip']):
      axis.invert_yaxis();
   #
   axis.set_xlabel(plotdaten['xlabel']);
   axis.set_ylabel(plotdaten['ylabel']);
   axis.set_title(plotdaten['title']);
   axis.set_position([0.18, 0.12, 0.72, 0.78]);
   for textfeld in plotdaten['textfelder']:
      axis.text(textfeld[1], textfeld[2], textfeld[0], ha='center', fontsize=12, zorder=11);
   #
   axis.legend(loc=plotdaten['legendenposition']).set_zorder(15);
#


# -------------------------------------------------------------------------------------------------
def TkPlot(plotdaten):
   """Erzeuge ein neues Fenster mit einem Plot. Die Daten dazu werden aus plotdaten extrahiert.
   Die plotdaten solten auf das Resultat von PlotvorlageVorbereiten() oder einer der anderen
   Plotdaten...()-Funktionen aufbauen, damit alle relevanten Schluessel in der plotdaten-Struktur
   existieren.
   """
   import tkinter
   import matplotlib
   matplotlib.use('TkAgg')
   from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
   #
   tk_bildanker = tkinter.Tk();
   pdfdateiname = plotdaten['zeitstempel'] + '-' + plotdaten['typ'] + '.pdf';
   pngdateiname = plotdaten['zeitstempel'] + '-' + plotdaten['typ'] + '.png';
   #
   if (plotdaten['title'] != ''):
      tk_bildanker.title(plotdaten['title']);
   #
   plotbreite = 800;
   plothoehe = 600;
   if (plotdaten['typ'] == 'KVS'):
      plotbreite = 1600;
      plothoehe = 800;
   #
   fensterbreite = plotbreite;
   fensterhoehe = plothoehe + 40;
   dpi = 150;
   tk_bildanker.geometry('{}x{}'.format(fensterbreite, fensterhoehe))
   #
   figure = matplotlib.figure.Figure(figsize=(plotbreite/dpi, plothoehe/dpi), dpi=dpi);
   linienbreite = 0.5;
   matplotlib.rcParams['axes.linewidth'] = linienbreite;
   matplotlib.rcParams['lines.linewidth'] = 2.4*linienbreite;
   matplotlib.rcParams['grid.linewidth'] = linienbreite;
   matplotlib.rcParams['xtick.major.width'] = linienbreite;
   matplotlib.rcParams['xtick.minor.width'] = linienbreite;
   matplotlib.rcParams['ytick.major.width'] = linienbreite;
   matplotlib.rcParams['ytick.minor.width'] = linienbreite;
   if (plotdaten['typ'] == 'KVS'):
      _SieblinienPlot(figure=figure, plotdaten=plotdaten);
   else:
      _NormalerPlot(figure=figure, plotdaten=plotdaten);
   #
   zeichnungsrahmen = tkinter.Frame(tk_bildanker, width=plotbreite, height=plothoehe);
   zeichnungsrahmen.grid(row=1, sticky='s');
   zeichnung = FigureCanvasTkAgg(figure, master=zeichnungsrahmen);
   zeichnung.draw();
   zeichnung.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1);
   zeichnung._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1);
   #
   kontrollrahmen = tkinter.Frame(tk_bildanker, width=fensterbreite, height=fensterhoehe-plothoehe);
   kontrollrahmen.grid(row=0, sticky='n');
   # Ohne Lambda oder vergleichbares wuerde der Plot immer gespeichert werden
   savebutton = tkinter.Button(master=kontrollrahmen, text='Save pdf', command=lambda: figure.savefig(pdfdateiname));
   savebutton.grid(row=0, column=0, padx=50, sticky='e');
   savebutton = tkinter.Button(master=kontrollrahmen, text='Save png', command=lambda: figure.savefig(pngdateiname));
   savebutton.grid(row=0, column=1, padx=50, sticky='e');
   exitbutton = tkinter.Button(master=kontrollrahmen, text='Quit', command=tk_bildanker.destroy);
   exitbutton.grid(row=0, column=2, padx=50, sticky='w');
   #
   #tk_bildanker.bind('<Control-q>', _Exit_GUI);
   tkinter.mainloop();
#


# -------------------------------------------------------------------------------------------------
def EmbeddedPlot(plotdaten, figure):
   """Erzeuge einen Plot in der uebergebenen figure. Die Daten dazu werden aus plotdaten extrahiert.
   Die plotdaten solten auf das Resultat von PlotvorlageVorbereiten() oder einer der anderen
   Plotdaten...()-Funktionen aufbauen, damit alle relevanten Schluessel in der plotdaten-Struktur
   existieren.
   """
   import matplotlib
   #
   linienbreite = 0.5;
   matplotlib.rcParams['axes.linewidth'] = linienbreite;
   matplotlib.rcParams['lines.linewidth'] = 2.4*linienbreite;
   matplotlib.rcParams['grid.linewidth'] = linienbreite;
   matplotlib.rcParams['xtick.major.width'] = linienbreite;
   matplotlib.rcParams['xtick.minor.width'] = linienbreite;
   matplotlib.rcParams['ytick.major.width'] = linienbreite;
   matplotlib.rcParams['ytick.minor.width'] = linienbreite;
   if (plotdaten['typ'] == 'KVS'):
      _SieblinienPlot(figure=figure, plotdaten=plotdaten);
   else:
      _NormalerPlot(figure=figure, plotdaten=plotdaten);
#
