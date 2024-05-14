# STCH - CZ
Skript STCH (Comparison of Selected Thermal CHaracteristics - Srovnání vybraných termálních charakteristik) 
slouží jako příloha k bakalářské práci s názvem SROVNÁNÍ VYBRANÝCH TERMÁLNÍCH CHARAKTERISTIK KRAJINY ZA POMOCÍ TECHNIK DPZ.
Účelem tohoto skriptu je automatizace výpočtů jednotlivých termálních charakteristik krajiny (albedo, povrchová teplota, teplotní spoudění) za pomocí satelitních snímků Landsat 8 a Landsat 9.


## INFO
Tato bakalářská práce se zaměřuje na srovnání vybraných termálních charakteristik krajiny za pomocí technik dálkového průzkumu Země. 
Konkrétně zkoumá albedo, povrchovou teplotu a teplotní proudění půdy s cílem zjistit a ověřit nejvhodnější metodu pro měření jednotlivých charakteristik. 

Součástí práce je také programový kód, vytvořený pro automatizaci výpočtů jednotlivých termálních charakteristik. Tento kód byl inspirován kódem ([CCi.py](https://github.com/terezano/)) a výstupy, které vytváří jsou ve formě rastrových souborů (.TIF).

Výsledky této práce mohou být využitelné při rozhodování, jakou metodu vybrat při zpracování určité termální charakteristiky.


## SPUŠTĚNÍ
Ke spuštění tohoto skriptu jsou zapotřebí oba dva soubory (STCH.py a calc_STCH.py), dále složka 'input', do které se vloží všechny soubory, které jsou obsaženy v jednotlivých satelitních snímcích a složku 'output', která slouží jako výstupní složka pro vytvořená rastrová data.


## WEB
Bližší informace k tomuto skriptu (použité metody, způsob spuštění, výsledky apod.) naleznete na webových stránkách ([WEB](https://geoinformatics.upol.cz/dprace/bakalarske/stuchly24/))


## ZDROJ PROGRAMOVÉHO KÓDU
Zdrojový programový kód, který byl upraven pro potřeby této bakalářské práce je od ([Tereza Nováková 2021 - Diplomová práce](https://www.geoinformatics.upol.cz/dprace/magisterske/novakova21/zaver.html)),
která jej vytvořila v rámci své diplomové práce a slouží k výpočtu EVAPOTRANSPIRAČNÍ A OCHLAZOVACÍ FUNKCE.


# STCH - EN
Script STCH (Comparison of Selected Thermal CHaracteristics) serves as an appendix to the bachelor thesis entitled COMPARISON OF SELECTED THERMAL CHARACTERISTICS OF A COUNTRY USING STCH TECHNIQUES.
The purpose of this script is to automate the calculation of individual thermal landscape characteristics (albedo, surface temperature, temperature triggering) using Landsat 8 and Landsat 9 satellite imagery.


## INFO
This bachelor thesis focuses on the comparison of selected thermal landscape characteristics using remote sensing techniques. 
Specifically, it examines albedo, surface temperature, and ground thermal flow in order to identify and validate the most appropriate method for measuring each characteristic. 

The thesis also includes program code developed to automate the calculation of each thermal characteristic. This code was inspired by the code ([CCi.py](https://github.com/terezano/)) and the outputs it produces are in the form of raster files (.TIF).

The results of this work can be useful in deciding which method to choose when processing a particular thermal characteristic.


## RUNNING THE SCRIPT 
In order to run this script, both files (STCH.py and calc_STCH.py) are required, as well as an 'input' folder that holds all the files that are contained in each satellite image and an 'output' folder that serves as the output folder for the raster data produced.


## WEB
For more information on this script (methods used, method of execution, results, etc.), please visit the website ([WEB](https://geoinformatics.upol.cz/dprace/bakalarske/stuchly24/))


## PROGRAM CODE SOURCE
The source program code that has been adapted for the needs of this bachelor thesis is from ([Tereza Nováková 2021 - Diploma Thesis](https://www.geoinformatics.upol.cz/dprace/magisterske/novakova21/zaver.html)), who created it as part of her thesis and used it to calculate the EVAPOTRANSPIRATION AND COOLING FUNCTIONS.
