# Mixer Spur Analysis Method 1
 Crossing Spurious Analysis - GUI based
Crossing Spurious Analysis Script

Can read a csv file with spur levels of a harmonic mixer then iterate through all harmonics associated with the RF range and fixed LO.  Then plots the spurs that fall within the designated IF range.

REF: https://www.microwaves101.com/encyclopedias/mixer-spur-chart

Hovering over the spur lines will display the harmonic combination (mRF X nLO) and level (dBc)

If no mixer file is selected, the default Mini-Circuits ASK-1+ parameters are used.

Mixer harmonic files must have *.spr extension and use csv
