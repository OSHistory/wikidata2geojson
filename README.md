# wikidata2geojson

## Purpose

Turns a wikidata query into a geojson file

## Example:
`python3.4 __main__.py -q 'http://wdq.wmflabs.org/api?q=claim[39:19546]%20AND%20claim[31:5]' -o popes.geojson -p P19`

=> Creates a geojson file with the birthplaces of all popes.

See [wikidata API documentation] (https://wdq.wmflabs.org/api_documentation.html) for how to query the wikidata database.

## To Do:

* Add option to set more properties for the features
* Create a simple web map (Leaflet/OL3) to quickly
view the result
* Add option to flip the geocoordinates
