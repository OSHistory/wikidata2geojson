# wikidata2geojson
Turns a wikidata query into a geojson file

Example: 
python3.4 \_\_main\_\_.py -q 'http://wdq.wmflabs.org/api?q=claim[39:19546]%20AND%20claim[31:5]' -o popes.geojson -p P19
Creates a geojson file with the birthplaces of all popes. 

