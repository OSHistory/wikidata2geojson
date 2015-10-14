
from geojson_writer import GeoJSONWriter

import optparse
import sys

parser = optparse.OptionParser()

parser.add_option("-q", "--query", dest="query", default=None)
parser.add_option("-o", "--output-file", dest="output_file", default=None)
parser.add_option("-p", "--place-claim", dest="place_claim", default="P19")

opts, remainder = parser.parse_args()

query = opts.query
output_file = opts.output_file
place_claim = opts.place_claim

if (query == None):
    print("Fatal Error: No query specified!")
    print("Exiting...")
    sys.exit(1)
if (output_file == None):
    output_file = "data/" + str(time.time()).replace(".", "") + ".geojson"
    print("Output set to " + output_file)

gw = GeoJSONWriter(query, output_file, place_claim)
