
from place_resolver import PlaceResolver
from wikifetcher import WikiFetcher

import json
import os
import sys



class GeoJSONWriter():

    def __init__(self, query, geojson_path, place_claim="P19", data_path=None):
        self.wf = WikiFetcher()
        self.pr = PlaceResolver("places.json")
        self.STEP = 50
        self.DEBUG_DIR = "debug"
        self.place_claim = place_claim
        self.db = json.loads('{"entities": {} }')
        self.place_info_cnt = 0
        items = self.wf.get_items_from_query(query)
        print("Fetched " + str(len(items)) + " from query...")
        self.process_items(items)
        self.write_geojson(geojson_path)
        self.save_database(data_path, geojson_path)
        self.pr.close_failed_places()
        print("Written " + str(self.place_info_cnt) + " items with geoinformation to geojson file...")
        print("(Equals " + str(round(100 * (self.place_info_cnt / len(items)), 2)) + "%)")

    def save_database(self, data_path, geojson_path):
        if (data_path == None):
            data_path = geojson_path.replace(".geojson", "-data.json")
        dir_path = os.path.dirname(data_path)
        if (dir_path != ""):
            if (os.path.exists(dir_path) == False):
                os.makedirs(dir_path)
        fh = open(data_path, "w+")
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
            place_id = None
            # check if 625 already in object itself (then use own wikidata-id) 
            # Problem: double processing of the same entity
            if ("P625" in self.db["entities"][entity]["claims"]): 
                place_id = entity
                place_info, exception = self.pr.get_place_info_from_json(self.db["entities"][entity])
                feature = self.build_feature(entity, place_info["name"], [place_info["lon"], place_info["lat"]])
                geojson["features"].append(feature)
                self.place_info_cnt += 1
                
            elif (self.place_claim in self.db["entities"][entity]["claims"]):
                try:
                    place_id = self.db["entities"][entity]["claims"][self.place_claim][0]["mainsnak"]["datavalue"]["value"]["numeric-id"]
                    place_id = "Q" + str(place_id)
                    if (self.pr.has_place(place_id)):
                        if (self.pr.place_not_none(place_id)):
                            name = self.get_name(self.db["entities"][entity])
                            coords = self.pr.return_lon_lat(place_id)
                            feature = self.build_feature(entity, name, coords)
                            #feature["properties"]["name"] = self.get_name(self.db["entities"][entity])
                            #feature["geometry"]["coordinates"] = self.pr.return_lon_lat(place_id)
                            geojson["features"].append(feature)
                            self.place_info_cnt += 1
                except Exception as e:
                    print("Exception processing entity: " + entity)
                    print(e)
                
        fh = open(geojson_path, "w+")
        json.dump(geojson, fh)
        fh.close()

    def build_feature(self, wikiid, name, coords):
        feature = json.loads("""{
            "properties": { },
            "geometry": {
                "type": "Point",
                "coordinates": [null, null]
            },
            "type": "Feature"
        }""")
        feature["properties"]["wikiid"] = wikiid
        feature["properties"]["name"] = name
        feature["geometry"]["coordinates"] = coords
        
        return feature
        
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
