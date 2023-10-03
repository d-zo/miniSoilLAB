
miniSoilLAB 0.6.0
=================

[miniSoilLAB](https://github.com/d-zo/miniSoilLAB) is a graphical frontend for viewing and managing
results of selected geotechnical experiments for soil identification and
(hypoplastic/viscohypoplastic) parameter determination.
It includes a simple parser for selected oedometric and triaxial raw data formats as well as
a template system to read results from Spreadsheets (`.xlsx`-files).
It was created alongside work at the Institute of Geotechnical Engineering
at the Hamburg University of Technology.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4467991.svg)](https://doi.org/10.5281/zenodo.4467991)



Installation
------------

miniSoilLAB requires a working Python 3.x environment and
can be downloaded and run with Python.
It uses [openpyxl](https://openpyxl.readthedocs.io)
and its dependencies [et_xmlfile](https://pypi.org/project/et_xmlfile/)
and [jdcal](https://github.com/phn/jdcal) for reading `.xlsx`-files and
[matplotlib](https://matplotlib.org/) for plotting the results.



Running the program
-------------------

In Linux the following commands can be used in a shell
(the first command has to be adjusted to point to the right directory).

```
cd /path/to/miniSoilLAB
python3 miniSoilLAB.pyz
```

In Windows a batch file can be created to provide access to miniSoilLAB from anywhere.
Therefore, the path to the Python interpreter and the path to miniSoilLAB have to be
defined in the following code.

```
@echo off
pushd C:\path\to\miniSoilLAB
C:\path\to\Python\python.exe C:\path\to\miniSoilLAB\miniSoilLAB.pyz
pause
```

miniSoilLAB depends on templates (JSON-files) to be able to read entries from spreadsheets.
It is assumed that they are located in a folder called `Vorlagen`.
Currently the files have to be in subfolders with the exact name shown below,
but the JSON-files can have any name.
If multiple templates are provided,
spreadsheets with different format can be read.
The templates should uniquely fit to a spreadsheet.
Otherwise a wrong template will be used for reading or nothing is read because no template fits.

```
Vorlagen  ---+ Atterberg                ---+ Atterberg_01.json
             |
             + Auswertung-Hypoplastisch ---+ Auswertung-Hypoplastisch_01.json
             |
             + LoDi                     ---+ LoDi_01.json
             |
             + Oedo                     ---+ Oedo_01.json
             |
             + Oedo-CRL                 ---+ Oedo-CRL_01.json
             |
             + Oedo-CRS                 ---+ Oedo-CRS_01.json
             |
             + Oedo-CRS-Visko           ---+ Oedo-CRS-Visko_01.json
             |
             + Rohdaten                 ---+ Atterberg_01.json
             |
             + Triax-CU                 ---+ Triax-CU_01.json
             |
             + Triax-D                  ---+ Triax-D_01.json
             |
             + Triax-p-q                ---+ Triax-p-q_01.json
```

If the templates are not located in a folder called `Vorlagen` (in the current working directory)
the path to the template folder has to be provided as an argument when starting miniSoilLAB.



Usage and Documentation
-----------------------

A simple function documentation (in german) created with pydoc can be found
[here](https://d-zo.github.io/miniSoilLAB/miniSoilLAB.html "miniSoilLAB documentation").
More information about how to use miniSoilLAB and an example can be found in the
”Using miniSoilLAB“ tutorial.
A html-version of the tutorial can be found
[here](https://d-zo.github.io/miniSoilLAB/usingminisoillab.html "Using miniSoilLAB [html]")
and a pdf-version
[here](https://d-zo.github.io/miniSoilLAB/usingminisoillab.pdf "Using miniSoilLAB [pdf]").



Contributing
------------

**Bug reports**

If you found a bug, make sure you can reproduce it with the latest version of miniSoilLAB.
Please check that the expected results can actually be achieved by other means
and are not considered invalid operations due to problematic template files.
Please give detailed and reproducible instructions in your report including

 - the miniSoilLAB version
 - the expected result
 - the result you received
 - the command(s) used as a _minimal working example_

Note: The bug should ideally be reproducible by the _minimal working example_ alone.
Please keep the example code as short as possible (minimal).


**Feature requests**

If you have an idea for a new feature, consider searching the
[open issues](https://github.com/d-zo/miniSoilLAB/issues) and
[closed issues](https://github.com/d-zo/miniSoilLAB/issues?q=is%3Aissue+is%3Aclosed) first.
Afterwards, please submit a report in the
[Issue tracker](https://github.com/d-zo/miniSoilLAB/issues) explaining the feature and especially

 - why this feature would be useful (use cases)
 - what could possible drawbacks be (e.g. compatibility, dependencies, ...)



License
-------

miniSoilLAB is released under the
[GPL](https://www.gnu.org/licenses/gpl-3.0.html "GNU General Public License"),
version 3 or greater (see als [LICENSE](https://github.com/d-zo/miniSoilLAB/blob/master/LICENSE) file).
It is provided without any warranty.

