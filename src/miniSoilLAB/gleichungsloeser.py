# -*- coding: utf-8 -*-
"""
gleichungsloeser.py   v0.4 (2019-11)
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
def LinearesAusgleichsproblem(x, y):
   """Bestimmt die Steigung m und den y-Achsen-Abstand b fuer das lineare Ausgleichsproblem mit der
   Gleichung y = m*x + b. Gibt Steigung und y-Achsen-Abstand zurueck.
   """
   x_m = sum(x)/len(x);
   y_m = sum(y)/len(y);
   m_a = sum([(x[idx]-x_m)*(y[idx]-y_m) for idx in range(len(x))]);
   m = m_a/sum([(x[idx]-x_m)**2 for idx in range(len(x))]);
   b = y_m - m*x_m;
   return [m, b];
#


# -------------------------------------------------------------------------------------------------
def QuadratischesAusgleichsproblem(x, y):
   """Bestimme die Parameter a, b und c fuer das lineare Ausgleichsproblem mit quadratischer
   Gleichung y = a*x**2 + b*x + c. Gibt die drei Parameter [a, b, c] zurueck.
   """
   n = len(x);
   sumxy = sum([x[idx]*y[idx] for idx in range(n)]);
   sumx2 = sum([x_i * x_i for x_i in x]);
   sumx3 = sum([x_i * x_i *x_i for x_i in x]);
   sumx4 = sum([x_i * x_i *x_i *x_i for x_i in x]);
   sumx2y = sum([x[idx]*x[idx]*y[idx] for idx in range(n)]);
   nenner = n*sumx2*sumx4 + 2*sum(x)*sumx2*sumx3 - sumx2**3 - sum(x)**2 * sumx4 - n*sumx3**2;
   #
   a = (n*sumx2*sumx2y + sum(x)*sumx3*sum(y) + sum(x)*sumx2*sumxy - sumx2**2 * sum(y) - sum(x)**2 * sumx2y - n*sumx3*sumxy) / nenner;
   b = (n*sumx4*sumxy + sum(x)*sumx2*sumx2y + sumx2*sumx3*sum(y) - sumx2**2 * sumxy - sum(x)*sumx4*sum(y) - n*sumx3*sumx2y) / nenner;
   c = (sumx2*sumx4*sum(y) + sumx2*sumx3*sumxy + sum(x)*sumx3*sumx2y - sumx2**2 * sumx2y - sum(x)*sumx4*sumxy - sumx3**2*sum(y)) / nenner;
   return [a, b, c];
#


# -------------------------------------------------------------------------------------------------
def WinkelTangenteAnKreisboegen(x_min, x_max, y_0, winkeldelta=0.05):
   """Bildet Halbkreise aus den gegebenen x_min und x_max, die auf der x-Achse liegen.
   (x_min[i] und x_max[i] sind je Schnittpunkte von einem Kreis mit Radius (x_min[i]+x_max[i])/2.0)
   Findet die Gerade, die fuer x=0 den gegebenen y-Achsen-Abstand y_0 hat und alle Halbkreise
   moeglichst nur tangiert. Minimiert den Abstand zwischen dem idealen Tangentenpunkt jedes
   Halbkreises und der Geraden. Gibt den Winkel (in Grad) zurueck, fuer den der Fehler minimal ist.
   """
   from math import sin, cos, asin
   from .konstanten import grad2rad
   #
   minabstand = None;
   bester_winkel = None;
   #
   num_werte = len(x_min);
   mittelpunkte = [(x_max[idx] + x_min[idx])/2.0 for idx in range(num_werte)];
   radien = [(x_max[idx] - x_min[idx])/2.0 for idx in range(num_werte)];
   # Eine Abschaetzung fuer den minimalen/maximalen Winkel. Der mit steigendem y_0 kleiner werdende
   # maximale Winkel wird dabei zusaetzlich mit einem Puffer zum min_winkel abgeschaetzt, um
   # unnoetige Rechenoperationen einzusparen.
   min_winkel = min([asin((radien[idx]-y_0)/mittelpunkte[idx]) for idx in range(num_werte)]);
   max_winkel = min(min_winkel+15.0*grad2rad, max([asin(radien[idx]/mittelpunkte[idx]) for idx in range(num_werte)]));
   #
   winkeldelta_rad = winkeldelta*grad2rad;
   schritte = int((max_winkel-min_winkel)/winkeldelta_rad + 1.0);
   for idx_winkel in range(schritte):
      winkel = min_winkel + idx_winkel*winkeldelta_rad;
      r_hypothetisch = [mittelpunkte[idx]*sin(winkel) + y_0*cos(winkel) for idx in range(num_werte)];
      temp_abstand = sum([(r_hypothetisch[idx] - radien[idx])**2 for idx in range(num_werte)]);
      if ((minabstand is None) or ((minabstand is not None) and (temp_abstand < minabstand))):
         minabstand = temp_abstand;
         bester_winkel = winkel/grad2rad;
   #
   return [minabstand, bester_winkel];
#


# -------------------------------------------------------------------------------------------------
def LinearInterpoliertenIndexUndFaktor(vergleichswert, vergleichswertliste):
   """Bestimme die Position von einem vergleichswert in einer (streng monoton steigenden)
   vergleichswertliste. Dabei wird linear zwischen Zwei Werten interpoliert. Gibt den Indiex des
   Wertes vor/zu dem vergleichswert und einen faktor zurueck [idx_davor, faktor].
   Fuer spaeteres Interpolieren kann folgender, linearer Zusammenhang genutzt werden:
   zielwert = zielvec[idx_davor] + faktor*(zielvec[idx_davor+1]-zielvec[idx_davor])
   """
   letzterIndex = len(vergleichswertliste) - 1;
   for idx_wert, listenwert in enumerate(vergleichswertliste):
      if (listenwert == vergleichswert):
         if (idx_wert == letzterIndex):
            return [idx_wert-1, 1.0];
         else:
            return [idx_wert, 0.0];
      elif (listenwert > vergleichswert):
         if (idx_wert == 0):
            break;
         #
         faktor = (vergleichswert-vergleichswertliste[idx_wert-1]) / (vergleichswertliste[idx_wert]-vergleichswertliste[idx_wert-1]);
         return [idx_wert-1, faktor];
   #
   print('# Warnung: Vergleichswert nicht in Liste gefunden (echt kleiner/groesser oder Liste unsortiert)');
   return [None, None];
#


# -------------------------------------------------------------------------------------------------
def FunktionswerteAnGleichenXWerten(fx, fy, gx, gy):
   """Benoetigt werden zwei streng monoton steigende Vektoren fx und gx, die aber unterschiedlich
   lang sein koennen. Die dazugehoerigen fy-Werte muessen aber so viele Eintraege enthalten wie fx
   (analog gy wie gx). Es wird eine aufsteigende Liste aller x-Werte in den gemeinsamen Grenzen
   erstellt und die y-Werte für alle Zwischenpunkte beider x-Vektoren interpoliert.
   Gibt [xwerte, fy_interp, gy_interp] zurueck.
   """
   minwert = max(fx[0], gx[0]);
   maxwert = min(fx[-1], gx[-1]);
   xwerte = fx + gx;
   xwerte.sort();
   #
   fy_interp = [];
   gy_interp = [];
   #
   startidx = 0;
   stopidx = len(xwerte);
   for idx in range(len(xwerte)):
      if (xwerte[idx] < minwert):
         startidx = idx + 1;
         continue;
      #
      if (xwerte[idx] > maxwert):
         stopidx = idx;
         break;
      #
      fidx, ffak = LinearInterpoliertenIndexUndFaktor(vergleichswert=xwerte[idx], vergleichswertliste=fx);
      fy_interp += [fy[fidx] + ffak*(fy[fidx+1]-fy[fidx])];
      gidx, gfak = LinearInterpoliertenIndexUndFaktor(vergleichswert=xwerte[idx], vergleichswertliste=gx);
      gy_interp += [gy[gidx] + gfak*(gy[gidx+1]-gy[gidx])];
   #
   return [xwerte[startidx:stopidx], fy_interp, gy_interp];
#


# -------------------------------------------------------------------------------------------------
def _SchrittgroesseBestimmen(spanne):
   """Bestimme eine sinnvolle Schrittgroesse zwischen Zahlenwerten auf Basis der uebergebenen spanne.
   """
   from math import log10
   #
   logwert = log10(spanne);
   logganze = int(logwert);
   d0 = logwert - logganze;
   if (logwert <= 0 ):
      d0 = 1.0 + d0;
      logganze -= 1;
   #
   if (abs(d0) <=abs(log10(2.5))):
      rindex = 0;
   elif (abs(d0) < abs(log10(5.5))):
      rindex = 1;
   elif (abs(d0) < abs(log10(8.5))):
      rindex = 2;
   else:
      rindex = 3;
   #
   refzahl = [0.2, 0.5, 1.0, 2.0];
   return refzahl[rindex] * 10**logganze;
#


# -------------------------------------------------------------------------------------------------
def NaechsterWert(wert, spanne, aufsteigend=True):
   """Bestimme eine sinnvolle Schrittgroesse auf Basis der uebergebenen spanne.
   Ermittle auf Basis einer zu ermittelnden Schrittgroesse naechste/vorherige Zahl (Vielfaches der
   Schrittgroesse von wert aus gesehen, abhaengig von austeigend) und gebe sie zurueck.
   """
   tol = 1e-6;
   schrittgroesse = _SchrittgroesseBestimmen(spanne=spanne);
   if (aufsteigend):
      return (int((wert-schrittgroesse*tol)/schrittgroesse) + 1)*schrittgroesse;
   else:
      return int((wert-schrittgroesse*tol)/schrittgroesse)*schrittgroesse;
#


# -------------------------------------------------------------------------------------------------
def LetzterIndexMitWertKleinerAls(liste, grenzwert):
   """Finde in einer uebergebenen liste mit Zahlen die letzte Stelle, an der ein Listenwert kleiner
   oder gleich dem grenzwert ist. Gibt den Index dieses Werts zurueck oder None, falls kein Eintrag
   kleiner/gleich dem grenzwert ist.
   """
   testliste = list(reversed(liste));
   zielidx = None;
   for idx, wert in enumerate(testliste):
      if (wert < grenzwert):
         zielidx = idx;
         break;
   #
   if (zielidx is not None):
      zielidx = len(liste) - 1 - zielidx;
   #
   return zielidx;
#


# -------------------------------------------------------------------------------------------------
def WertInZulaessigemBereich(name, liste, minmax, meldung=True):
   """Ueberpruefe, ob sich alle Werte der uebergebene liste mit der Bezeichnung name in den
   Schranken minmax=[min_wert, max_wert] befindet. Gibt bei erfolgreicher Ueberpruefung True
   zurueck, ansonsten (bei meldung=True) eine Fehlermeldung und False.
   """
   if (len(liste) == 0):
      print('# Warnung: Zulaessiger Bereich kann fuer leere Liste nicht geprueft werden');
      return False;
   #
   for elem in liste:
      if ((not isinstance(elem, int)) and (not isinstance(elem, float))):
         print('# Warnung: Mindestens ein Eintrag von ' + name + ' ist keine Zahl');
         return False;
   #
   if (min(liste) < minmax[0]):
      if (meldung):
         print('# Warnung: Mindestens ein Eintrag von ' + name + ' (' + str(min(liste)) + ') ist kleiner als Minimum ' + str(minmax[0]));
      #
      return False;
   #
   if (max(liste) > minmax[1]):
      if (meldung):
         print('# Warnung: Mindestens ein Eintrag von ' + name + ' (' + str(max(liste)) + ') ist groesser als Maximum ' + str(minmax[1]));
      #
      return False;
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def _LoeseGleichungAlnxpbpc(x, y, freier_param):
   """Bestimme die Koeffizienten a, [b] und c aus der Gleichung y = a*ln(x+b)+c mit gegebenen x- und
   y-Werten sowie dem freien Parameter b. Bestimme die Abweichung zwischen den Funktionswerten
   y* = f(x) und y. Gibt die Koeffizienten und die dazugehoerige Abweichung zurueck.
   """
   from math import log
   #
   b = freier_param;
   a_nenner = [log((b + x[ref])/(b + x[(ref+1)%len(x)])) for ref in range(len(x))];
   if (any([(x == 0.0) for x in a_nenner])):
      # FIXME: Sinnvollen Rueckgabewert pruefen
      return [[0.0, b, 0.0], 1000000.0];
   #
   a = sum([(y[ref]-y[(ref+1)%len(x)])/log((b + x[ref])/(b + x[(ref+1)%len(x)])) for ref in range(len(x))])/len(x);
   c = sum([y[ref]-a*log(b+x[ref]) for ref in range(len(x))])/len(x);
   abweichung = sum([(y[num] - a*log(b + x[num]) - c)**2 for num in range(len(x))]);
   return [[a, b, c], abweichung];
#


# -------------------------------------------------------------------------------------------------
def LoeseGleichung(gleichung, x, y, intervall, max_it=500, puffergroesse=0.5, tol=1e-6):
   """Gleichungsloeser, der numerisch die Parameter fuer die gegebene Gleichung bestimmt (sofern
   die Gleichung implementiert ist). Dazu wird die Abweichung zwischen dem berechneten y*=f(x) und y
   bestimmt und minimiert. Als Suchraum muss ein intervall an Werten fuer den freien Parameter der
   entsprechenden Gleichung uebergeben werden. Das Intervall wird in jedem Schritt um puffergroesse
   verkleinert. Sinnvolle Werte sind im Bereich 0.5 (um die Haelfte verkleinern auf Mittelwert) bis
   0.99 (ein Prozent vom Ende mit der groesseren Abweichung entfernen).
   Bei zu grosser puffergroesse wird die Konvergenz verlangsamt, bei zu kleiner puffergroesse kann
   je nach Gleichung der Bereich mit der besten Loesung uebersprungen werden.
   
   Diese Funktion verkleinert das intervall, bis das Intervall um den Zielwert auf die gewuenschte
   Toleranz tol minimiert worden ist oder vorher max_it Iterationen durchlaufen woren sind.
   Gibt die berechneten Parameter der geforderten Gleichung mit der minimalen Abweichung zurueck.
   """
   if (gleichung == 'y = a*ln(x+b)+c'):
      Gleichungsfunktion = _LoeseGleichungAlnxpbpc;
   else:
      print('# Fehler: Gleichung nicht unterstuetzt');
      return [];
   #
   # Erstmal grob den Loesungsbereich zu finden
   param, initialabweichung = Gleichungsfunktion(x=x, y=y, freier_param=intervall[0]);
   #
   min_idx = 0;
   for idx, freier_param in enumerate(intervall):
      param, temp_abweichung = Gleichungsfunktion(x=x, y=y, freier_param=freier_param);
      if (temp_abweichung < initialabweichung):
         initialabweichung = temp_abweichung;
         min_idx = idx;
   #
   # Im Loesungsbereich eine optimierte Suche starten
   if (min_idx == 0):
      min_idx = 1;
   #
   if (min_idx == len(intervall)-1):
      min_idx = len(intervall)-2;
   #
   grenzen = [intervall[min_idx-1], intervall[min_idx+1]];
   param, abweichung0 = Gleichungsfunktion(x=x, y=y, freier_param=grenzen[0]);
   param, abweichung1 = Gleichungsfunktion(x=x, y=y, freier_param=grenzen[1]);
   #
   minmaxabweichung = [abweichung0, abweichung1];
   abweichung = min(minmaxabweichung);
   intervallgroesse = grenzen[1]-grenzen[0];
   #
   iterationen = 0;
   while (intervallgroesse > tol):
      iterationen += 1;
      param, abweichung = Gleichungsfunktion(x=x, y=y, freier_param=sum(grenzen)/2.0);
      #
      if (minmaxabweichung[0] > minmaxabweichung[1]):
         freier_param = puffergroesse*grenzen[0] + (1.0-puffergroesse)*grenzen[1];
         param, mod_abweichung = Gleichungsfunktion(x=x, y=y, freier_param=freier_param);
         minmaxabweichung[0] = mod_abweichung;
         grenzen[0] = freier_param;
      else:
         freier_param = (1.0-puffergroesse)*grenzen[0] + puffergroesse*grenzen[1];
         param, mod_abweichung = Gleichungsfunktion(x=x, y=y, freier_param=freier_param);
         minmaxabweichung[1] = mod_abweichung;
         grenzen[1] = freier_param;
      #
      intervallgroesse = grenzen[1]-grenzen[0];
      #
      if (iterationen >= max_it):
         print('# Warnung: Zu viele Iterationen vor ausreichender Konvergenz; abweichung=' + str(intervallgroesse));
         break;
   #
   param, mod_abweichung = Gleichungsfunktion(x=x, y=y, freier_param=min(grenzen));
   return param;
#


# -------------------------------------------------------------------------------------------------
def AbleitungDyNachDx(x, y):
   """Berechne fuer alle y-Werte die Ableitungen dy/dx ueber Differenzenquotienten
   dy_dx = (y_(i+1) - y_i)/(x_(i+1) - x_i). Da die Ableitungen jeweils fuer einen Bereich zwischen
   zwei Punkten x_i und x_(i+1) ausgewertet werden, wird auch ein dazugehoeriger Vektor mit den
   Mittelpunkten x_(m,i) = (x_i + x_(i+1))/2 erstellt. Gibt [x_m, dy_dx] zurueck.
   """
   tol = 1e-10;
   xneu = [(x[idx+1] + x[idx])/2.0 for idx in range(len(x)-1)];
   nenner = [x[idx+1] - x[idx] for idx in range(len(x)-1)];
   if (any([(wert == 0)  for wert in nenner])):
      print('# Abbruch: Muesste beim Ableiten durch Null teilen');
      idx = nenner.index(0);
      print('           Wert an Stelle ' + str(idx) + ' und Folgewert identisch');
      return [None, None];
   #
   ydiff = [(y[idx+1] - y[idx]) / nenner[idx] for idx in range(len(x)-1)];
   return [xneu, ydiff];
#


# -------------------------------------------------------------------------------------------------
def IntegrationDyMitDx(x0, y0, dx, dy):
   """Integriere alle dy-Werte mit einem einfachen Euler-Explizit-Verfahren bezueglich der Abstaende
   x_(i+1) - x_i. Der Startwert fuer die integrierten Werte y ist y0. Fuer die Differenzen dx
   wird mit dem Startwert x0 die x-Werte erzeugt. Gibt [x, y] zurueck.
   """
   # FIXME: Anpassung von x sinnvoll?
   xinteg = [x0];
   yinteg = [y0];
   for idx in range(len(dx)-1):
      xinteg += [xinteg[-1] + dx[idx]];
      yinteg += [yinteg[-1] + dy[idx]*dx[idx]];
   #
   return [xinteg, yinteg];
#


# -------------------------------------------------------------------------------------------------
def LokalerExtremwert(werte, intervall, maximum=True):
   """Bestimme je nach maximum entweder Maximalwerte oder Minimalwerte aus werte. Dabei werden nur
   Extremwerte beruecksichtigt, die mindestens im lokalen Bereich intervall vor und nach dem Wert
   groesser oder kleiner als alle anderen Werte sind. Gibt [indizes] der Extremwerte aus werte zurueck.
   """
   idxliste = [];
   num_werte = len(werte);
   #
   if (intervall > num_werte):
      print('Intervall fuer FindLocalMin zu gross gewaehlt');
      return [];
   #
   for idx_wert, wert in enumerate(werte):
      idx_links = idx_wert - int(intervall);
      idx_rechts = idx_wert + int(intervall);
      if (idx_links < 0):
         idx_links = 0;
      #
      if (idx_rechts > num_werte):
         idx_rechts = num_werte;
      #
      temp_werte = werte[idx_links:idx_rechts];
      if (maximum):
         if (any([einzelwert > wert for einzelwert in temp_werte])):
            continue;
      else:
         if (any([einzelwert < wert for einzelwert in temp_werte])):
            continue;
      idxliste += [idx_wert];
   #
   return idxliste;
#


# -------------------------------------------------------------------------------------------------
def SortierenUndDoppelteXEintraegeEntfernen(x, y):
   """Verknuepfe die Eintraege zweier gleichlanger Vektoren x und y und sortiere sie nach x ohne
   die Zuordnung x_i zu y_i zu aendern (d.h. die Eintraege aus y werden i.A. ihre Position aendern).
   Entferne anschliessend doppelte Eintraege in x. Der Mittelwert aller dazugehoerigen y-Werte
   wird dem y-Wert des verbleibenden x-Wertes zugewiesen. Gibt [xsort, ysort] zurueck.
   """
   sortblock = list(zip(x, y));
   sortblock.sort(key=lambda z: z[0]);
   xsort = [];
   ysort = [];
   vielfaches = 0;
   for idx_block in range(len(sortblock)):
      xtemp, ytemp = sortblock[idx_block];
      if (idx_block > 0):
         if (xtemp == xsort[-1]):
            vielfaches += 1;
            ysort[-1] = (ysort[-1]*vielfaches + ytemp) / (vielfaches + 1);
            continue;
         #
         vielfaches = 0;
      #
      xsort += [xtemp];
      ysort += [ytemp];
   #
   return [xsort, ysort];
#


# -------------------------------------------------------------------------------------------------
def GlaettungFunktionswerte(werte, glaettungsbereich):
   """Glaette die uebergebenen werte mit einem gleitenden Mittelwert. Der Einflussbereich des
   Fensters von Werten fuer die Mittelwertbildung sind die naechsten glaettungsbereich Punkte vom
   aktuellen Wert aus. Folglich hat der geglaettete Vektor glaettungsbereich-Eintraege weniger.
   Gibt den geglaetteten Vektor zurueck.
   """
   if (glaettungsbereich == 0):
      return werte;
   else:
      return [sum(werte[idx:(idx+glaettungsbereich)])/glaettungsbereich for idx in range(len(werte)-glaettungsbereich)];
#


# -------------------------------------------------------------------------------------------------
def SteigungUndGrenzeLinearerAnfangsbereich(x, y, refbereich, delta_max):
   """Betrachte aus den uebergebenen Daten x und y einen refbereich, der als (mehr oder weniger)
   linear angesehen werden kann. Erhoehe die obere Grenze von refbereich so lange, wie die
   Abweichung zwischen einer linearen Ausgleichsfunktion und dem Funktionswert selbst kleiner
   als delta_max ist. Gebe die Steigung der linearen Ausgleichsfunktion zurueck und den Index,
   an dem die Abweichung gerade noch kleiner als delta_max ist.
   """
   steigung, achsenabstand = LinearesAusgleichsproblem(x=x[refbereich[0]:refbereich[1]],
      y=y[refbereich[0]:refbereich[1]]);
   idx_grenz = -1;
   for idx in range(len(x[:refbereich[1]]), len(x)):
      temp_fehler = (y[idx] - steigung*x[idx] - achsenabstand)**2;
      if (temp_fehler > delta_max):
         break;
      #
      idx_grenz += 1;
   #
   if (idx_grenz == -1):
      print('# Warnung: Suche nach dem Punkt mit delta_max Unterschied fehlgeschlagen');
      idx_grenz = 0;
   #
   return [idx_grenz + refbereich[1], steigung, achsenabstand];
#


# -------------------------------------------------------------------------------------------------
def Spline2DInterpolation(xwerte, ywerte, zwischenpunkte=5, tangentenfaktor=1.0):
   """Erwartet zwei gleichlange Vektoren xwerte und ywerte. Auf Basis kubischer Splines werden
   jeweils zwischen zwei Punkten neue Punkte interpoliert (zwischenpunkte). Der Einfluss der
   Kruemmung aus der Tangentenbestimmung kann mit tangentenfaktor [0-1] gesteuert werden, wobei
   ein hoeherer Faktor fuer einen groesseren Einfluss steht. Gibt die interpolierten Punkte
   [xinterp, yinterp] zurueck.
   """
   from math import sqrt
   #
   numpunkte = len(xwerte);
   x_rueck = [];
   y_rueck = [];
   tol = 1e-8;
   zwischenwerte = [x/zwischenpunkte for x in range(zwischenpunkte)];
   #
   # FIXME: Besser dokumentieren oder leserlicher schreiben!
   for idxpunkt in range(1, numpunkte-2):
      P0 = [xwerte[idxpunkt-1], ywerte[idxpunkt-1]];
      P1 = [xwerte[idxpunkt], ywerte[idxpunkt]];
      P2 = [xwerte[idxpunkt+1], ywerte[idxpunkt+1]];
      P3 = [xwerte[idxpunkt+2], ywerte[idxpunkt+2]];
      #
      dir20 = _Vektorrichtung(vektor=[a-b for a, b in zip(P2, P0)]);
      dir13 = _Vektorrichtung(vektor=[a-b for a, b in zip(P1, P3)]);
      vec21 = [a-b for a, b in zip(P2, P1)];
      dir21 = _Vektorrichtung(vektor=vec21);
      #
      len12 = _Vektor2norm(vektor=vec21);
      if (len12 <= tol):
         x_rueck += [P1[0] for x in range(zwischenpunkte)];
         y_rueck += [P1[1] for y in range(zwischenpunkte)];
         continue;
      #
      ortdir = _Orthogonaler2DVektor(vektor=dir21);
      fac1 = 0.0;
      nenner1 = (dir20[0]*(P2[1]-P1[1]) - dir20[1]*(P2[0]-P1[0]));
      if (sum([abs(a-b) for a, b in zip(P1, P0)]) > tol) and (abs(nenner1) > tol):
         fac1 = (ortdir[0]*(P2[1]-P1[1]) - ortdir[1]*(P2[0]-P1[0]))/nenner1;
      #
      fac2 = 0.0;
      nenner2 = (dir13[0]*(P2[1]-P1[1]) - dir13[1]*(P2[0]-P1[0]));
      if (sum([abs(a-b) for a, b in zip(P2, P3)]) > tol) and (abs(nenner2) > tol):
         fac2 = (ortdir[0]*(P2[1]-P1[1]) - ortdir[1]*(P2[0]-P1[0]))/nenner2;
      #
      if (fac1*fac2 < tol):
         fac1 = 1.0;
         fac2 = 1.0;
      #
      skalierungsfaktor = 1.0/sqrt(2.0)*len12 / (fac1+fac2);
      K1 = [P1[idx] + tangentenfaktor*fac1*skalierungsfaktor*dir20[idx] for idx in range(2)];
      K2 = [P2[idx] + tangentenfaktor*fac2*skalierungsfaktor*dir13[idx] for idx in range(2)];
      #
      x_rueck += [P1[0] + 3.0*(K1[0]-P1[0])*temp_wert + 3.0*(P1[0]-2.0*K1[0]+K2[0])*temp_wert**2 + (P2[0]-P1[0]+3.0*(K1[0]-K2[0]))*temp_wert**3 for temp_wert in zwischenwerte];
      y_rueck += [P1[1] + 3.0*(K1[1]-P1[1])*temp_wert + 3.0*(P1[1]-2.0*K1[1]+K2[1])*temp_wert**2 + (P2[1]-P1[1]+3.0*(K1[1]-K2[1]))*temp_wert**3 for temp_wert in zwischenwerte];
   #
   x_rueck += [xwerte[-1]];
   y_rueck += [ywerte[-1]];
   return [x_rueck, y_rueck];
#


# -------------------------------------------------------------------------------------------------
def _Vektor2norm(vektor):
   """Berechne die 2-Norm des uebergebenen vektor und gib diese zurueck.
   """
   from math import sqrt
   #
   return sqrt(sum([eintrag**2 for eintrag in vektor]));
#


# -------------------------------------------------------------------------------------------------
def _Vektorrichtung(vektor):
   """Bestimme die Richtung des uebergebenen vektor. Gib den Einheitsvektor mit der gleichen
   Richtung wie vektor zurueck.
   """
   richtung = [0.0 for eintrag in vektor];
   vecnorm = _Vektor2norm(vektor);
   if (vecnorm > 0.0):
      richtung = [eintrag/vecnorm for eintrag in vektor];
   #
   return richtung;
#


# -------------------------------------------------------------------------------------------------
def _Orthogonaler2DVektor(vektor):
   """Bestimme einen orthogonalen Vektor zum uebergebenen vektor und gib diesen zurueck.
   """
   orth = [0.0, 0.0];
   if (vektor[0] != 0.0):
      orth = [vektor[1], -vektor[0]];
   else:
      if (vektor[1] != 0.0):
         orth = [-vektor[1], 0.0];
   #
   return orth;
#
