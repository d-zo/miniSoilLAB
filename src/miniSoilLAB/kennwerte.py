# -*- coding: utf-8 -*-
"""
kennwerte.py   v0.4 (2023-09)
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
def Vorbereitung(daten, vorlage):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der uebergebenen vorlage und
    speichere sie in der uebergebenen Struktur daten, sofern diese den gueltigen Vorgaben entspricht.
    """
    from .verarbeitung_korndichte import VorbereitungKorndichte
    from .verarbeitung_lodi import VorbereitungLoDi
    from .verarbeitung_atterberg import VorbereitungAtterberg
    from .verarbeitung_hypo import VorbereitungHypo
    from .verarbeitung_oedo import VorbereitungOedo
    from .verarbeitung_oedocrl import VorbereitungOedoCRL
    from .verarbeitung_oedocrs import VorbereitungOedoCRS
    from .verarbeitung_oedocrsvisko import VorbereitungOedoCRSVisko
    from .verarbeitung_triaxd import VorbereitungTriaxD
    from .verarbeitung_triaxcu import VorbereitungTriaxCU
    from .verarbeitung_triaxpq import VorbereitungTriaxpq

    bearbeitungsliste = [
        ('Korndichte', VorbereitungKorndichte),
        ('LoDi', VorbereitungLoDi),
        ('VorbereitungAtterberg', VorbereitungAtterberg),
        ('Oedo', VorbereitungOedo),
        ('Oedo-CRL', VorbereitungOedoCRL),
        ('Oedo-CRS', VorbereitungOedoCRS),
        ('Oedo-CRS-Visko', VorbereitungOedoCRSVisko),
        ('Triax-D', VorbereitungTriaxD),
        ('Triax-CU', VorbereitungTriaxCU),
        ('Triax-p-q', VorbereitungTriaxpq),
        ('Auswertung-Hypoplastisch', VorbereitungHypo),
    ]
    for vorb_name, vorb_aufruf in bearbeitungsliste:
        if (vorlage == vorb_name):
            vorb_aufruf(daten=daten)
            break



# -------------------------------------------------------------------------------------------------
def Kennwertberechnungen(daten, vorlage=None):
    """Bestimme die Kennwerte zu einer eingelesenen Dateistruktur nach der uebergebenen vorlage und
    speichere sie in der uebergebenen Struktur daten, sofern diese den gueltigen Vorgaben entspricht.
    Falls keine vorlage uebergeben wird, werden die Kennwerte aller Unterstrukturen ermittelt.
    """
    from .konstanten import gueltige_vorlagen, debugmodus
    from .datenstruktur import Datenstruktur
    from .verarbeitung_kvs import KennwerteKVS
    from .verarbeitung_korndichte import KennwerteKorndichte
    from .verarbeitung_lodi import KennwerteLoDi
    from .verarbeitung_atterberg import KennwerteAtterberg
    from .verarbeitung_hypo import KennwerteHypo
    from .verarbeitung_oedo import KennwerteOedo
    from .verarbeitung_oedocrl import KennwerteOedoCRL
    from .verarbeitung_oedocrs import KennwerteOedoCRS
    from .verarbeitung_oedocrsvisko import KennwerteOedoCRSVisko
    from .verarbeitung_triaxd import KennwerteTriaxD
    from .verarbeitung_triaxcu import KennwerteTriaxCU
    from .verarbeitung_triaxpq import KennwerteTriaxpq

    status = False

    if (vorlage is not None):
        vorlagenliste = [vorlage]
        if (vorlage not in gueltige_vorlagen):
            print('# Warnung: Ungueltige Vorlage')
            return False
    else:
        vorlagenliste = []
        vergleichsliste = list(daten.keys())
        # Hinweis: gueltige_vorlagen ist sortiert, so dass alle Abhaengigkeiten einer Vorlage davor
        #          in der Liste stehen. Dadurch sollten Fehler bei der Berechnung von Kennwerten nur
        #          durch tatsaechlich fehlende Daten entstehen
        for temp_vorlage in gueltige_vorlagen:
            if (temp_vorlage in vergleichsliste):
                vorlagenliste += [temp_vorlage]

        if (len(vorlagenliste) == 0):
            print('# Warnung: Keine gueltigen Vorlagen in Struktur gefunden')
            return False

    # Die Reihenfolge entspricht der Abfolge in gueltige_vorlagen. Dadurch koennen die Eintraege
    # hintereinander geprueft werden. Fuer die Kennwertbestimmung zu bearbeitungsliste_eins
    # sind auch keine zusaetzlichen Abhaenigkeiten noetig und lediglich "Korndichte" speichert
    # ein zusaetzliches Ergebnis in der Hauptstruktur
    idx = 0
    num_vorlagen = len(vorlagenliste)

    bearbeitungsliste = [
        ('KVS', KennwerteKVS, []),
        ('Korndichte', KennwerteKorndichte, []),
        ('Atterberg', KennwerteAtterberg, []),
        ('Auswertung-Hypoplastisch', KennwerteHypo, []),
        ('LoDi', KennwerteLoDi, ['Korndichte [g/cm^3]']),
        ('Oedo', KennwerteOedo, ['Korndichte [g/cm^3]']),
        ('Oedo-CRL', KennwerteOedoCRL, ['Korndichte [g/cm^3]']),
        ('Oedo-CRS', KennwerteOedoCRS, ['Korndichte [g/cm^3]']),
        ('Oedo-CRS-Visko', KennwerteOedoCRSVisko, ['Korndichte [g/cm^3]']),
        ('Triax-CU', KennwerteTriaxCU, ['Korndichte [g/cm^3]', 'Fliessgrenze [%]', 'Ausrollgrenze [%]', 'Ueberkornanteil > 0,4mm [%]']),
        ('Triax-D', KennwerteTriaxD, ['Korndichte [g/cm^3]', 'Trockendichte-min [g/cm^3]', 'Trockendichte-max [g/cm^3]']),
        ('Triax-p-q', KennwerteTriaxpq, ['Korndichte [g/cm^3]', 'Trockendichte-min [g/cm^3]', 'Trockendichte-max [g/cm^3]']),
    ]
    refwerte = Datenstruktur()
    fehlerfrei = True
    for kenn_name, kenn_aufruf, voraussetzungen in bearbeitungsliste:
        if (vorlagenliste[idx] == kenn_name):
            if (kenn_name not in daten):
                print('# Warnung: ' + kenn_name + ' nicht wie erwartet in uebergebenen daten')
                return False

            if (debugmodus):
                print('# Debug: Bearbeite Kennwerte ' + kenn_name)

            for ref_voraus in voraussetzungen:
                if (ref_voraus not in refwerte):
                    if (ref_voraus in daten):
                        print('# Hinweis: Verwende Vorgabewert zu ' + ref_voraus)
                        refwerte.update([(ref_voraus, daten[ref_voraus])])
                    else:
                        gefunden = False
                        schluesselliste = list(daten.keys())
                        for schluessel in schluesselliste:
                            try:
                                wert = daten[schluessel][daten[schluessel]['_Refwahl']][ref_voraus]
                            except:
                                continue

                            gefunden = True
                            print('# Hinweis: Verwende Vorgabewert zu ' + ref_voraus + ' aus ' + schluessel)
                            refwerte.update([(ref_voraus, wert)])
                            break

                        if (not gefunden):
                            try:
                                # Versuche, den erforderlichen Wert aus dem ersten Datensatz der zu verarbeitenden Daten zu extrahieren
                                wert = daten[kenn_name]['_Ref_001'][ref_voraus]
                                refwerte.update([(ref_voraus, wert)])
                            except:
                                print('# Warnung: Allgemeiner Eintrag ' + ref_voraus + ' fehlt zur Berechnung von ' + kenn_name)
                                return False

            if (kenn_aufruf(daten=daten[kenn_name], refwerte=refwerte)):
                if (kenn_name == 'Korndichte'):
                    refwerte.update([('Korndichte [g/cm^3]', daten['Korndichte']['Korndichte [g/cm^3]'])])
                elif (kenn_name == 'Atterberg'):
                    refwerte.update([('Fliessgrenze [%]', daten['Atterberg']['Fliessgrenze [%]'])])
                    refwerte.update([('Ausrollgrenze [%]', daten['Atterberg']['Ausrollgrenze [%]'])])
                    refwerte.update([('Ueberkornanteil > 0,4mm [%]', daten['Atterberg']['Ueberkornanteil > 0,4mm [%]'])])
                elif (kenn_name == 'LoDi'):
                    refwerte.update([('Trockendichte-min [g/cm^3]', daten['LoDi']['Trockendichte-min [g/cm^3]'])])
                    refwerte.update([('Trockendichte-max [g/cm^3]', daten['LoDi']['Trockendichte-max [g/cm^3]'])])

            else:
                print('# Warnung: Bearbeitung von ' + kenn_name + ' fehlgeschlagen')
                fehlerfrei = False

            idx += 1
            if (idx >= num_vorlagen):
                return fehlerfrei

    # Wenn der folgende Code erreicht wird, entspricht die angenommene Reihenfolge der Vorlagen
    # nicht gueltige_vorlagen
    print('# Warnung: Interne Reihenfolge der Vorlagen nicht wie erwartet - Code pruefen')
    return False


