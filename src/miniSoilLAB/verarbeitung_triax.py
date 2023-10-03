# -*- coding: utf-8 -*-
"""
verarbeitung_triax.py   v0.3 (2023-09)
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


# -------------------------------------------------------------------------------------------------
def _KennwerteTriaxVersuchstabelle(daten, refwerte, typ):
    """Bestimme die Kennwerte der Versuchstabelle zu einer eingelesenen Dateistruktur nach der
    Vorlage Triax-D, Triax-CU oder Triax-p-q und speichere sie in der uebergebenen Struktur daten,
    sofern diese den Vorgaben entspricht.
    """
    from math import pi
    from .datenstruktur import Datenstruktur
    from .verarbeitung_hilfen import GespeicherterWertOderUebergabe

    herstellung = daten['1-Probenherstellung']
    saettigung = daten['2-Saettigung']
    konsolidation = daten['3-Konsolidation']

    hoehe_e = herstellung['Hoehe [mm]']
    durchmesser_e = herstellung['Durchmesser [mm]']

    korndichte = refwerte['Korndichte [g/cm^3]']
    if (typ == 'Triax-CU'):
        fliessgrenze = refwerte['Fliessgrenze [%]']
        ausrollgrenze = refwerte['Ausrollgrenze [%]']
        ueberkorn = refwerte['Ueberkornanteil > 0,4mm [%]']

        abscheren = daten['5-Abscheren']

        feuchtmasse_e = herstellung['Feuchtmasse [g]']
        delta_hoehe_k = konsolidation['Delta Hoehe [mm]']
        trockenmasse_e = abscheren['Trockenmasse [g]']
        herstellung.update([('Trockenmasse [g]', trockenmasse_e)])
    elif ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        trockenmasse_e = herstellung['Trockenmasse [g]']
        backvolume_start_s = saettigung['Backvolume-Start [mm^3]']
        backvolume_ende_s = saettigung['Backvolume-Ende [mm^3]']
        backvolume_ende_k = konsolidation['Backvolume-Ende [mm^3]']
        dichte_locker, dichte_dicht = [refwerte[x] for x in ['Trockendichte-min [g/cm^3]', 'Trockendichte-max [g/cm^3]']]

        if (typ == 'Triax-D'):
            abscheren = daten['5-Abscheren']
            backvolume_ende_a = abscheren['Backvolume-Ende [mm^3]']

    else:
        print('# Warnung: Triax-Tabelle konnte keiner (implementierten) Variante zugeordnet werden')
        return False

    zelldruck = saettigung['Zelldruck [kN/m^2]']
    saettigungsdruck = saettigung['Saettigungsdruck [kN/m^2]']

    tol = 1e-6
    # --------------------- Probenherstellung --------------------

    # Normalerweise sollten immer drei Versuche durchgefuehrt werden, aber im Allgemeinen wird die
    # Versuchsanzahl aus den eingetragenen/gueltigen Anfangshoehen hoehe_e abgeleitet
    anzahl_versuche = len(hoehe_e)
    volumen_e = [pi*(durchmesser_e[idx]/10.0/2.0)**2 * hoehe_e[idx]/10.0 for idx in range(anzahl_versuche)]
    herstellung.update([('Volumen [cm^3]', volumen_e)])

    nulltests = [('Trockenmasse', trockenmasse_e), ('Volumen', volumen_e)]
    for bezeichnung, wert in nulltests:
        if (any([(abs(einzelvar) < tol) for einzelvar in wert])):
            print('# Warnung: Mindestens ein(e) ' + bezeichnung + ' annaehernd Null')
            return False

    wassergehalt100 = [(volumen_e[idx] - trockenmasse_e[idx]/korndichte)/trockenmasse_e[idx] for idx in range(anzahl_versuche)]
    herstellung.update([('Wassergehalt-100%-Saettigung [-]', wassergehalt100)])

    if ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        wassergehalt_e = [(volumen_e[idx] - trockenmasse_e[idx]/korndichte - backvolume_ende_s[idx]/1000.0)/trockenmasse_e[idx] for idx in range(anzahl_versuche)]
    elif (typ == 'Triax-CU'):
        wassergehalt_e = [(feuchtmasse_e[idx]-trockenmasse_e[idx])/trockenmasse_e[idx] for idx in range(anzahl_versuche)]

    herstellung.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_e])])
    wassermasse = [wassergehalt_e[idx]*trockenmasse_e[idx] for idx in range(anzahl_versuche)]
    herstellung.update([('Wassermasse [g]', wassermasse)])

    # FIXME: Der folgende Block fuer alle Triaxialversuche?
    feuchtmasse_e = [trockenmasse_e[idx]+wassermasse[idx] for idx in range(anzahl_versuche)]
    herstellung.update([('Feuchtmasse [g]', feuchtmasse_e)])

    einbaudichte = [feuchtmasse_e[idx]/volumen_e[idx] for idx in range(anzahl_versuche)]
    herstellung.update([('Dichte [g/cm^3]', einbaudichte)])
    trockendichte_e = [trockenmasse_e[idx]/volumen_e[idx] for idx in range(anzahl_versuche)]
    herstellung.update([('Dichte-trocken [g/cm^3]', trockendichte_e)])

    # FIXME: Die folgenden Bloecke fuer alle Triaxialversuche?
    porenanteil_e = [1.0 - trockendichte_e[idx]/korndichte for idx in range(anzahl_versuche)]
    herstellung.update([('Porenanteil [-]', porenanteil_e)])

    nulltests = [('Trockendichte', trockendichte_e), ('Porenanteil', porenanteil_e)]
    for bezeichnung, variable in nulltests:
        if (any([(abs(einzelvar) < tol) for einzelvar in variable])):
            print('# Warnung: Mindestens ein(e) ' + bezeichnung + ' (Herstellung) annaehernd Null')
            return False

    porenzahl_e = [korndichte/trockendichte_e[idx] - 1.0 for idx in range(anzahl_versuche)]
    herstellung.update([('Porenzahl [-]', porenzahl_e)])
    saettigung_e = [wassergehalt_e[idx]*trockendichte_e[idx]/porenanteil_e[idx] for idx in range(anzahl_versuche)]
    herstellung.update([('Saettigungsgrad [-]', saettigung_e)])

    if ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        lagerungsdichte_e = [(trockendichte_e[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)]
        herstellung.update([('Lagerungsdichte [-]', lagerungsdichte_e)])
        lagerungsdichte_e_bez = [lagerungsdichte_e[idx]*dichte_dicht/trockendichte_e[idx] for idx in range(anzahl_versuche)]
        herstellung.update([('Lagerungsdichte-bez [-]', lagerungsdichte_e_bez)])
    elif (typ == 'Triax-CU'):
        if (fliessgrenze == ausrollgrenze):
            print('# Warnung: Fliessgrenze entspricht Ausrollgrenze')
            return False

        konsistenzzahl_e = [(fliessgrenze-100.0*wassergehalt_e[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)]
        herstellung.update([('Konsistenzzahl [-]', konsistenzzahl_e)])
        liquiditaetszahl_e = [1.0-temp_kons for temp_kons in konsistenzzahl_e]
        herstellung.update([('Liquiditaetszahl [-]', liquiditaetszahl_e)])

    # ------------------------ Saettigung ------------------------
    if ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        wassermasse_s = [(backvolume_ende_s[idx] - backvolume_start_s[idx])/1000.0 + wassermasse[idx] for idx in range(anzahl_versuche)]
        wassergehalt_s = [wassermasse_s[idx]/trockenmasse_e[idx] for idx in range(anzahl_versuche)]
    elif (typ == 'Triax-CU'):
        wassergehalt_s = wassergehalt100
        wassermasse_s = [trockenmasse_e[idx]*wassergehalt100[idx] for idx in range(anzahl_versuche)]

    saettigung.update([('Wassermasse [g]', wassermasse_s)])
    saettigung.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_s])])
    dichte_s = [(wassermasse_s[idx] + trockenmasse_e[idx])/volumen_e[idx] for idx in range(anzahl_versuche)]
    saettigung.update([('Dichte [g/cm^3]', dichte_s)])
    trockendichte_s = [dichte_s[idx]/(1.0 + wassergehalt_s[idx]) for idx in range(anzahl_versuche)]
    saettigung.update([('Dichte-trocken [g/cm^3]', trockendichte_s)])

    if (any([(abs(einzelvar) < tol) for einzelvar in trockendichte_s])):
        print('# Warnung: Mindestens eine Trockendichte (Saettigung) annaehernd Null')
        return False
    # FIXME: Der folgende Block fuer alle Triaxialversuche?
    porenanteil_s = [1.0 - trockendichte_s[idx]/korndichte for idx in range(anzahl_versuche)]
    saettigung.update([('Porenanteil [-]', porenanteil_s)])
    porenzahl_s = [korndichte/trockendichte_s[idx] - 1.0 for idx in range(anzahl_versuche)]
    saettigung.update([('Porenzahl [-]', porenzahl_s)])
    saettigung_s = [wassergehalt_s[idx]*trockendichte_s[idx]/porenanteil_s[idx] for idx in range(anzahl_versuche)]
    saettigung.update([('Saettigungsgrad [-]', saettigung_s)])

    if ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        lagerungsdichte_s = [(trockendichte_s[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)]
        saettigung.update([('Lagerungsdichte [-]', lagerungsdichte_s)])
        lagerungsdichte_s_bez = [lagerungsdichte_s[idx]*dichte_dicht/trockendichte_s[idx] for idx in range(anzahl_versuche)]
        saettigung.update([('Lagerungsdichte-bez [-]', lagerungsdichte_s_bez)])
    elif (typ == 'Triax-CU'):
        konsistenzzahl_s = [(fliessgrenze-100.0*wassergehalt_s[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)]
        saettigung.update([('Konsistenzzahl [-]', konsistenzzahl_s)])
        liquiditaetszahl_s = [1.0-temp_kons for temp_kons in konsistenzzahl_s]
        saettigung.update([('Liquiditaetszahl [-]', liquiditaetszahl_s)])

    # ----------------------- Konsolidation ----------------------
    if (typ == 'Triax-CU'):
        hoehe_k = [hoehe_e[idx]-delta_hoehe_k[idx] for idx in range(anzahl_versuche)]
        konsolidation.update([('Hoehe [mm]', hoehe_k)])
        durchmesser_k = [durchmesser_e[idx] * hoehe_k[idx]/hoehe_e[idx] for idx in range(anzahl_versuche)]
        konsolidation.update([('Durchmesser [mm]', durchmesser_k)])

        volumen_k = [(hoehe_k[idx])/10.0*pi*(durchmesser_k[idx]/2.0/10.0)**2 for idx in range(anzahl_versuche)]
        delta_volumen_k = [volumen_e[idx] - volumen_k[idx] for idx in range(anzahl_versuche)]
    elif ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        delta_volumen_k = [(backvolume_ende_s[idx] - backvolume_ende_k[idx])/1000.0 for idx in range(anzahl_versuche)]
        volumen_k = [volumen_e[idx] - delta_volumen_k[idx] for idx in range(anzahl_versuche)]
        hoehe_k = [hoehe_e[idx]*(1.0 - delta_volumen_k[idx]/volumen_e[idx]/3.0) for idx in range(anzahl_versuche)]
        konsolidation.update([('Hoehe [mm]', hoehe_k)])
        durchmesser_k = [durchmesser_e[idx]*(1.0 - delta_volumen_k[idx]/volumen_e[idx]/3.0) for idx in range(anzahl_versuche)]
        konsolidation.update([('Durchmesser [mm]', durchmesser_k)])

    if (any([(abs(einzelvar) < tol) for einzelvar in hoehe_k])):
        print('# Warnung: Mindestens eine Hoehe (Konsolidation) annaehernd Null')
        return False

    konsolidation.update([('Volumenaenderung [cm^3]', delta_volumen_k)])
    konsolidation.update([('Volumen [cm^3]', volumen_k)])

    if (any([(abs(einzelvar) < tol) for einzelvar in volumen_k])):
        print('# Warnung: Mindestens ein Volumen (Konsolidation) annaehernd Null')
        return False

    # --------------------- Nach Konsolidation -------------------
    nachkon = GespeicherterWertOderUebergabe(daten=daten,
        bezeichnung='4-Nach Konsolidation', uebergabe=Datenstruktur())

    feuchtmasse_n = [trockenmasse_e[idx] + wassermasse_s[idx] - delta_volumen_k[idx] for idx in range(anzahl_versuche)]
    nachkon.update([('Feuchtmasse [g]', feuchtmasse_n)])
    wassergehalt_n = [(feuchtmasse_n[idx]-trockenmasse_e[idx])/trockenmasse_e[idx] for idx in range(anzahl_versuche)]
    nachkon.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_n])])
    dichte_n = [feuchtmasse_n[idx]/volumen_k[idx] for idx in range(anzahl_versuche)]
    nachkon.update([('Dichte [g/cm^3]', dichte_n)])
    trockendichte_n = [trockenmasse_e[idx]/volumen_k[idx] for idx in range(anzahl_versuche)]
    nachkon.update([('Dichte-trocken [g/cm^3]', trockendichte_n)])

    if (any([(abs(einzelvar) < tol) for einzelvar in trockendichte_n])):
        print('# Warnung: Mindestens eine Trockendichte (Nach Konsolidation) annaehernd Null')
        return False

    # FIXME: Der folgende Block fuer alle Triaxialversuche?
    porenanteil_n = [1.0 - trockendichte_n[idx]/korndichte for idx in range(anzahl_versuche)]
    nachkon.update([('Porenanteil [-]', porenanteil_n)])
    porenzahl_n = [korndichte/trockendichte_n[idx] - 1.0 for idx in range(anzahl_versuche)]
    nachkon.update([('Porenzahl [-]', porenzahl_n)])
    saettigung_n = [wassergehalt_n[idx]*trockendichte_n[idx]/porenanteil_n[idx] for idx in range(anzahl_versuche)]
    nachkon.update([('Saettigungsgrad [-]', saettigung_n)])

    if ((typ == 'Triax-D') or (typ == 'Triax-p-q')):
        lagerungsdichte_n = [(trockendichte_n[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)]
        nachkon.update([('Lagerungsdichte [-]', lagerungsdichte_n)])
        lagerungsdichte_n_bez = [lagerungsdichte_n[idx]*dichte_dicht/trockendichte_n[idx] for idx in range(anzahl_versuche)]
        nachkon.update([('Lagerungsdichte-bez [-]', lagerungsdichte_n_bez)])
    elif (typ == 'Triax-CU'):
        konsistenzzahl_n = [(fliessgrenze-100.0*wassergehalt_n[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)]
        nachkon.update([('Konsistenzzahl [-]', konsistenzzahl_n)])
        liquiditaetszahl_n = [1.0-temp_kons for temp_kons in konsistenzzahl_n]
        nachkon.update([('Liquiditaetszahl [-]', liquiditaetszahl_n)])

    if (typ == 'Triax-p-q'):
        # ----------------------- p-q-Pfad ------------------------
        for segmentname in ['Segment 2', 'Segment 4']:
            segment = daten['5-p-q-Pfad'][segmentname]
            porenwasserdruck_p = segment['Porenwasserdruck [kN/m^2]']
            eff_iso_druck_p = segment['Druck-isotrop-eff [kN/m^2]']
            hauptspannungsdiff_p = segment['Hauptspannungsdifferenz [kN/m^2]']

            druck_total_iso_p = [porenwasserdruck_p[idx] + eff_iso_druck_p[idx] for idx in range(anzahl_versuche)]
            segment.update([('Druck-isotrop [kN/m^2]', druck_total_iso_p)])
            zelldruck_p = [(3.0*druck_total_iso_p[idx] - hauptspannungsdiff_p[idx])/3.0 for idx in range(anzahl_versuche)]
            segment.update([('Zelldruck [kN/m^2]', zelldruck_p)])
            normalspannung_p = [zelldruck_p[idx] + hauptspannungsdiff_p[idx] for idx in range(anzahl_versuche)]
            segment.update([('Normalspannung [kN/m^2]', normalspannung_p)])

        # Falls ein p-q-Pfad vorhanden ist, existiert kein abscheren-Eintrag -> beenden
        return True

    elif (typ == 'Triax-D'):
        # ----------------------- Abscheren -----------------------
        delta_volumen_a = [(backvolume_ende_k[idx] - backvolume_ende_a[idx])/1000.0 for idx in range(anzahl_versuche)]
        abscheren.update([('Volumenaenderung [cm^3]', delta_volumen_a)])
        volumen_a = [volumen_k[idx] - delta_volumen_a[idx] for idx in range(anzahl_versuche)]
    elif (typ == 'Triax-CU'):
        delta_volumen_a = [0 for idx in range(anzahl_versuche)]
        volumen_a = volumen_k

    abscheren.update([('Volumen [cm^3]', volumen_a)])

    if (any([(abs(einzelvar) < tol) for einzelvar in volumen_a])):
        print('# Warnung: Mindestens ein Volumen (Abscheren) annaehernd Null')
        return False

    feuchtmasse_a = [feuchtmasse_n[idx] - delta_volumen_a[idx] for idx in range(anzahl_versuche)]
    abscheren.update([('Feuchtmasse [g]', feuchtmasse_a)])
    wassergehalt_a = [(feuchtmasse_a[idx]-trockenmasse_e[idx])/trockenmasse_e[idx] for idx in range(anzahl_versuche)]
    abscheren.update([('Wassergehalt [%]', [100.0*wert for wert in wassergehalt_a])])
    dichte_a = [feuchtmasse_a[idx]/volumen_a[idx] for idx in range(anzahl_versuche)]
    abscheren.update([('Dichte [g/cm^3]', dichte_a)])
    trockendichte_a = [trockenmasse_e[idx]/volumen_a[idx] for idx in range(anzahl_versuche)]
    abscheren.update([('Dichte-trocken [g/cm^3]', trockendichte_a)])

    if (any([(abs(einzelvar) < tol) for einzelvar in trockendichte_n])):
        print('# Warnung: Mindestens eine Trockendichte (Abscheren) annaehernd Null')
        return False

    # FIXME: Der folgende Block fuer alle Triaxialversuche?
    porenanteil_a = [1.0 - trockendichte_a[idx]/korndichte for idx in range(anzahl_versuche)]
    abscheren.update([('Porenanteil [-]', porenanteil_a)])
    porenzahl_a = [korndichte/trockendichte_a[idx] - 1.0 for idx in range(anzahl_versuche)]
    abscheren.update([('Porenzahl [-]', porenzahl_a)])
    saettigung_a = [wassergehalt_a[idx]*trockendichte_a[idx]/porenanteil_a[idx] for idx in range(anzahl_versuche)]
    abscheren.update([('Saettigungsgrad [-]', saettigung_a)])

    if (typ == 'Triax-D'):
        lagerungsdichte_a = [(trockendichte_a[idx] - dichte_locker)/(dichte_dicht - dichte_locker) for idx in range(anzahl_versuche)]
        abscheren.update([('Lagerungsdichte [-]', lagerungsdichte_a)])
        lagerungsdichte_a_bez = [lagerungsdichte_a[idx]*dichte_dicht/trockendichte_a[idx] for idx in range(anzahl_versuche)]
        abscheren.update([('Lagerungsdichte-bez [-]', lagerungsdichte_a_bez)])
    elif (typ == 'Triax-CU'):
        konsistenzzahl_a = [(fliessgrenze-100.0*wassergehalt_a[idx]/(1.0-ueberkorn/100.0))/(fliessgrenze-ausrollgrenze) for idx in range(anzahl_versuche)]
        abscheren.update([('Konsistenzzahl [-]', konsistenzzahl_a)])
        liquiditaetszahl_a = [1.0-temp_kons for temp_kons in konsistenzzahl_a]
        abscheren.update([('Liquiditaetszahl [-]', liquiditaetszahl_a)])

    return True



# -------------------------------------------------------------------------------------------------
def _KennwerteTriaxDundCU(daten, refwerte, typ):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der Vorlage Triax-D oder
    Triax-CU und speichere sie in der uebergebenen Struktur daten, sofern diese den Vorgaben
    entspricht. Fuer den typ "Triax-D" werden zusaetzlich "Korndichte [g/cm^3]",
    "Trockendichte-min [g/cm^3]" und "Trockendichte-min [g/cm^3]" in refwerte benoetigt,
    fuer "Triax-CU" die Werte "Fliessgrenze [%]", "Ausrollgrenze [%]" und
    "Ueberkornanteil > 0,4mm [%]". Aktualisiert die Struktur daten und gibt True bei erfolgreicher
    Bestimmung der Kennwerte zuruck, sonst False.
    """
    from math import asin, atan
    from .konstanten import grad2rad
    from .datenstruktur import Datenstruktur
    from .verarbeitung_hilfen import SekundenOhneOffsetBereitstellen, GespeicherterWertOderUebergabe
    from .gleichungsloeser import LinearesAusgleichsproblem, LinearInterpoliertenIndexUndFaktor
    from .gleichungsloeser import WinkelTangenteAnKreisboegen

    if (not _KennwerteTriaxVersuchstabelle(daten=daten, refwerte=refwerte, typ=typ)):
        print('# Warnung: Bestimmung der Kennwerte fehlgeschlagen')
        return False

    # Einstellbare Parameter fuer Triaxialversuche, falls keine Vorgaben existieren
    param_spanne = 1.2           # Betrachteter prozentualer Bereich um die Peakdehnung
    param_c_delta = 0.1          # Anfangsschrittweite/-genauigkeit bei der Bestimmung der Kohaesion
    param_max_c_schritte = 800   # Max. erlaubte Schritte zur Bestimmung der Kohaesion (limitiert Schrittweite/Genauigkeit)

    herstellung = daten['1-Probenherstellung']
    trockenmasse_e = herstellung['Trockenmasse [g]']

    konsolidation = daten['3-Konsolidation']
    hoehe_k = konsolidation['Hoehe [mm]']
    volumen_k = konsolidation['Volumen [cm^3]']

    tol = 1e-6

    sigma_1 = [None, None, None]
    sigma_3 = [None, None, None]

    for idx_triax, triax_versuch in enumerate(['Versuch 1', 'Versuch 2', 'Versuch 3']):
        try:
            triax = daten[triax_versuch]
        except KeyError as errormessage:
            print('# Warnung: Mindestens eine erforderliche Struktur nicht vorhanden - ' + str(errormessage))
            continue

        radialdruck = triax['Radialdruck [kN/m^2]']
        porenwasserdruck = triax['Porenwasserdruck [kN/m^2]']
        axialkraft = triax['Axialkraft [kN]']
        stauchung = triax['Stauchung [mm]']

        if (not SekundenOhneOffsetBereitstellen(daten=triax, formatliste=['%Y-%m-%d %H:%M:%S', '%H:%M:%S'])):
            print('# Warnung: Zeit [s] konnte nicht erfolgreich gebildet/angepasst werden')
            continue

        numdaten = len(triax['Zeit [s]'])
        kraft = [einzel_axialkraft-axialkraft[0] for einzel_axialkraft in axialkraft]
        dehnung = [100.0*(einzel_stauchung-stauchung[0])/hoehe_k[idx_triax] for einzel_stauchung in stauchung]

        if (any([(abs(hoehe_k[idx_triax] - tempstauchung) < tol) for tempstauchung in stauchung])):
            print('# Warnung: Stauchung entspricht annaehernd der Hoehe der konsolidierten Probe')
            continue

        if (typ == 'Triax-D'):
            porenwasservolumen = triax['Porenwasservolumen [mm^3]']

            delta_volumen = [(vol-porenwasservolumen[0])/1000.0 for vol in porenwasservolumen]
            flaeche = [1000.0*(volumen_k[idx_triax]+delta_volumen[idx])/(hoehe_k[idx_triax]-stauchung[idx]) for idx in range(numdaten)]
            delta_v_v0 = [100.0*delta_volumen[idx]/(volumen_k[idx_triax]) for idx in range(numdaten)]
            triax.update([('delta V/V_0 [%]', delta_v_v0)])
        if (typ == 'Triax-CU'):
            flaeche = [1000.0*(volumen_k[idx_triax])/(hoehe_k[idx_triax]-stauchung[idx]) for idx in range(numdaten)]

        if (any([(abs(tempflaeche) < tol) for tempflaeche in flaeche])):
            print('# Warnung: Mindestens eine Flaeche annaehernd Null')
            continue

        sig1sig3diff = [1e6*kraft[idx]/flaeche[idx]/2.0 for idx in range(numdaten)]
        sigma1prime = [(2.0*sig1sig3diff[idx] + radialdruck[idx]) - porenwasserdruck[idx] for idx in range(numdaten)]
        sigma3prime = [radialdruck[idx] - porenwasserdruck[idx] for idx in range(numdaten)]
        sig1sig3primesum = [(sigma1prime[idx] + sigma3prime[idx])/2.0 for idx in range(numdaten)]

        if (typ == 'Triax-CU'):
            if (any([(abs(tempsig3) < tol) for tempsig3 in sigma3prime])):
                print('# Warnung: Mindestens ein sigma3\' annaehernd Null')
                continue

            sig1psig3p = [sigma1prime[idx]/sigma3prime[idx] for idx in range(numdaten)]
            triax.update([('sig1_prime/sig3_prime [-]', sig1psig3p)])
            triax.update([('Porenwasserdruck-Delta [kN/m^2]', [porendruck - porenwasserdruck[0] for porendruck in porenwasserdruck])])

        try:
            phi_prime = [asin((sigma1prime[idx]-sigma3prime[idx])/(sigma1prime[idx]+sigma3prime[idx]))/grad2rad for idx in range(numdaten)]
        except:
            print('# Warnung: phi\' konnte nicht bestimmt werden')
            continue

        if (typ == 'Triax-D'):
            # Es wird bereits vorher sichergestellt, dass trockenmasse_e ungleich Null ist
            if (any([(abs(volumen_k[idx_triax]+temp_vol) < tol) for temp_vol in delta_volumen])):
                print('# Warnung: Differenz von mindestens einem Volumen zu Delta Volumen annaehernd Null')
                continue

            korndichte = refwerte['Korndichte [g/cm^3]']
            triax_porenzahlen = [korndichte/(trockenmasse_e[idx_triax]/(volumen_k[idx_triax]+delta_volumen[idx]))-1.0 for idx in range(numdaten)]
            triax.update([('Porenzahl [-]', triax_porenzahlen)])

        triax.update([('(sig_1 - sig_3)/2.0 [kN/m^2]', sig1sig3diff)])
        triax.update([('(sig_1prime + sig_3prime)/2.0 [kN/m^2]', sig1sig3primesum)])
        triax.update([('Reibungswinkel [Grad]', phi_prime)])
        triax.update([('Dehnung [%]', dehnung)])

        peak = GespeicherterWertOderUebergabe(daten=triax, bezeichnung='Peakzustand',
            uebergabe=Datenstruktur())
        if (typ == 'Triax-D'):
            idx_peak = sig1sig3diff.index(max(sig1sig3diff))
            peak.update([('Porenzahl [-]', triax_porenzahlen[idx_peak])])
        elif (typ == 'Triax-CU'):
            idx_peak = sig1psig3p.index(max(sig1psig3p))
            peak.update([('Porenwasserdruck [kN/m^2]', porenwasserdruck[idx_peak])])

        peak.update([('Index', idx_peak)])
        peak.update([('Sigma_1_prime [kN/m^2]', sigma1prime[idx_peak])])
        peak.update([('Sigma_3_prime [kN/m^2]', sigma3prime[idx_peak])])
        peak.update([('Dehnung [%]', dehnung[idx_peak])])

        sigma_1[idx_triax] = sigma1prime[idx_peak]
        sigma_3[idx_triax] = sigma3prime[idx_peak]

        if (typ == 'Triax-D'):
            einstellungen = GespeicherterWertOderUebergabe(daten=triax, bezeichnung='Einstellungen',
                uebergabe=Datenstruktur())

            spanne = GespeicherterWertOderUebergabe(daten=einstellungen, bezeichnung='Spanne',
                uebergabe=param_spanne)

            maxspanne = max(min(dehnung), dehnung[idx_peak]-spanne)
            minspanne = min(max(dehnung), dehnung[idx_peak]+spanne)
            idx_dehnstart, faks = LinearInterpoliertenIndexUndFaktor(vergleichswert=maxspanne,
                vergleichswertliste=dehnung)
            idx_dehnende, faks = LinearInterpoliertenIndexUndFaktor(vergleichswert=minspanne,
                vergleichswertliste=dehnung)

            einstellungen.update([('Dehnungsspanne (min/max)', [minspanne, maxspanne])])

            if ((idx_dehnstart is None) or (idx_dehnende is None)):
                continue

            steigung, offset = LinearesAusgleichsproblem(x=dehnung[idx_dehnstart:idx_dehnende],
                y=delta_v_v0[idx_dehnstart:idx_dehnende])

            if (steigung < -1.0):
                print('# Warnung: Steigung sollte positiv (und muss groesser als -1) sein')
                continue

            geradenwinkel = atan(steigung)/grad2rad
            dilatanzwinkel = asin(steigung/(2.0+steigung))/grad2rad
            peak.update([('Geradenwinkel [Grad]', geradenwinkel)])
            peak.update([('Dilatanzwinkel [Grad]', dilatanzwinkel)])


    if (any([(tempsig is None) for tempsig in sigma_1]) or any([(tempsig is None) for tempsig in sigma_3])):
        print('# Warnung: Es konnten nicht alle drei Spannungen von sigma1/sigma3 erkannt werden')
        return False

    # --------------------- Mohr-Coulomb-Daten -------------------
    mc = GespeicherterWertOderUebergabe(daten=daten, bezeichnung='Mohr-Coulomb', uebergabe=Datenstruktur())
    mc.update([('Sigma_1 [kN/m^2]', sigma_1)])
    mc.update([('Sigma_3 [kN/m^2]', sigma_3)])

    if (typ == 'Triax-D'):
        ohne_c = GespeicherterWertOderUebergabe(daten=mc, bezeichnung='Ohne Kohaesion',
            uebergabe=Datenstruktur())

        # Finde den dazugehoerigen Reibungswinkel
        ohneKohaesion = WinkelTangenteAnKreisboegen(x_min=sigma_3, x_max=sigma_1, y_0=0)
        ohne_c.update([('Reibungswinkel-eff [Grad]', ohneKohaesion[1])])
    else:
        mitKohaesion = [None, None, None]
        # Es gibt wahrscheinlich bessere Abschaetzungen, aber die Kohaesion
        # ist zumindest kleiner als der minimale radius
        # FIXME: Am besten das Intervall erst grob und dann in immer feineren Schritten unterteilen.
        max_kohaesion = min([(sigma_1[idx] - sigma_3[idx])/2.0 for idx in range(3)])

        c_delta = param_c_delta
        c_delta_max = int((param_max_c_schritte - 1.0)*max_kohaesion)
        if (c_delta > c_delta_max):
            print('# Hinweis: Verringere Iterationen zur Bestimmung der Kohaesion (ungenauerer Wert)')
            c_delta = c_delta_max

        c_schritte = int(max_kohaesion/c_delta + 1.0)
        for idx_kohaesion in range(c_schritte):
            c = idx_kohaesion*c_delta
            temp_abstand, temp_winkel = WinkelTangenteAnKreisboegen(x_min=sigma_3, x_max=sigma_1, y_0=c)

            if ((mitKohaesion[0] is None) or ((mitKohaesion[0] is not None) and (temp_abstand < mitKohaesion[0]))):
                mitKohaesion = [temp_abstand, temp_winkel, c]

        mit_c = GespeicherterWertOderUebergabe(daten=mc, bezeichnung='Mit Kohaesion',
            uebergabe=Datenstruktur())

        mit_c.update([('Reibungswinkel-eff [Grad]', mitKohaesion[1])])
        mit_c.update([('Kohaesion [kN/m^2]', mitKohaesion[2])])

    return True


