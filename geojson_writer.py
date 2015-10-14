
from place_resolver import PlaceResolver
from wikifetcher import WikiFetcher

import json
import os
import sys



class GeoJSONWriter():

    def __init__(self, query, geojson_path, place_claim="P19", quick_map=False, properties):
        self.wf = WikiFetcher()
        self.pr = PlaceResolver("places.json")
        self.STEP = 50
        self.DEBUG_DIR = "debug"
        self.place_claim = place_claim
        self.properties = self.__resolve_properties(properties)
        self.db = json.loads('{"entities": {} }')
        self.place_info_cnt = 0
        items = self.wf.get_items_from_query(query)
        print("Fetched " + str(len(items)) + " from query...")
        self.process_items(items)
        self.write_geojson(geojson_path)
        self.save_database("mydata.json")
        self.pr.close_failed_places()
        print("Written " + str(self.place_info_cnt) + " items with geoinformation to geojson file...")
        print("(Equals " + str(round(100 * (self.place_info_cnt / len(items)), 2)) + "%)")

    def __resolve_properties(self, properties):
        split_props = properties.split(":")
        props = [prop.split("/") for prop in split_props]
        return props

    def save_database(self, datapath):
        dir_path = os.path.dirname(datapath)
        if (dir_path != ""):
            if (os.path.exists(dir_path) == False):
                os.makedirs(dir_path)
        fh = open(datapath, "w+")
        json.dump(self.db, fh)
        fh.close()

    def write_geojson(self, geojson_path):
        geojson = json.loads("""{
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": { "name": "urn:ogc:def:crs:EPSG::4326" }
            },
            "features": []
        }""")
        for entity in self.db["entities"]:
            # TODO: set properties to be written via cmd-line
            #print(entity)
            feature = json.loads("""{
                "properties": { },
                "geometry": {
                    "type": "Point",
                    "coordinates": [null, null]
                },
                "type": "Feature"
            }""")
            if (self.place_claim in self.db["entities"][entity]["claims"]):
                try:
                    place_id = self.db["entities"][entity]["claims"][self.place_claim][0]["mainsnak"]["datavalue"]["value"]["numeric-id"]
                    place_id = "Q" + str(place_id)
                    if (self.pr.has_place(place_id)):
                        if (self.pr.place_not_none(place_id)):
                            feature["properties"]["name"] = self.get_name(self.db["entities"][entity])
                            if (feature["properties"]["name"] == ""):
                                print(json.dumps(self.db["entities"][entity], indent=7))
                                sys.exit(1)
                            feature["geometry"]["coordinates"] = self.pr.return_lon_lat(place_id)
                            geojson["features"].append(feature)
                            self.place_info_cnt += 1
                except Exception as e:
                    print("Exception processing entity: " + entity)
                    print(e)

        fh = open(geojson_path, "w+")
        json.dump(geojson, fh)
        fh.close()

    def get_name(self, entity):
        if ("en" in entity["labels"]):
            if ("value" in entity["labels"]["en"]):
                return entity["labels"]["en"]["value"]
        # No value for en, check for sitelinks
        for link in entity["sitelinks"]:
            if ("title" in entity["sitelinks"][link]):
                if (entity["sitelinks"][link]["title"] != ""):
                    return entity["sitelinks"][link]["title"]
        return ""

    def process_items(self, items):
        cnt = 0
        length = len(items)

        while (cnt < length):
            print("Processing items " + str(cnt) + " to " + str(cnt + self.STEP))
            curr_id_list = items[cnt:cnt+self.STEP]
            curr_json = self.wf.get_json_for_id_list(curr_id_list)
            for entity in curr_json["entities"]:
                self.db["entities"][entity] = curr_json["entities"][entity]
                if (self.place_claim in curr_json["entities"][entity]["claims"]):
                    try:
                        curr_place_id = "Q" + str(curr_json["entities"][entity]["claims"][self.place_claim][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])
                        if (self.pr.has_place(curr_place_id) == False):
                            self.pr.append_id_to_resolver(curr_place_id)
                    except Exception as e:
                        print("Exception: ")
                        print(e)
            cnt += self.STEP
            self.pr.resolve_pending_ids()
