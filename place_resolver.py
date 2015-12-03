
# manages all the mapping from WikiData-Place-Id to
# lat/lon and names
from wikifetcher import WikiFetcher

import os
import json
import urllib.request as request

class PlaceResolver():

    def __init__(self, db_path):
        self.wf = WikiFetcher()
        self.db = self.init_database(db_path)
        self.resolve_list = []
        self.failed_places_no_point = open("failed_places.info", "w+") # holds list of non retrieval places
                                         # (because refers to an object without an 625 Property (geolocation for a point))

    def close_failed_places(self):
        self.failed_places_no_point.close()

    def append_id_to_resolver(self, place_id):
        self.resolve_list.append(place_id)

    def has_place(self, place_id):
        if (place_id in self.db):
            return True
        else:
            return False

    def place_not_none(self, place_id):
        try:
            return self.db[place_id] != None
        except:
            return False

    def return_lat_lon(self, place_id):
        place_info = self.db[place_id]
        return [place_info["lat"], place_info["lon"]]

    def return_lon_lat(self, place_id):
        place_info = self.db[place_id]
        return [place_info["lon"], place_info["lat"]]

    def resolve_pending_ids(self):
        if (len(self.resolve_list) == 0):
            return False
        new_resolve_list = []
        for item in self.resolve_list:
            if (item not in self.db):
                new_resolve_list.append(item)
        #print(self.resolve_list)
        json_resp = self.wf.get_json_for_id_list(new_resolve_list)
        if ("entities" in json_resp):
            for place in json_resp["entities"]:
                if (place not in self.db):
                    #print("Resolving " + place + "...")
                    place_info, exception = self.get_place_info_from_json(json_resp["entities"][place]) 
                    self.db[place] = place_info 
                    if (exception): 
                        if (exception.args[0] == "P625"):
                            if place not in self.failed_places_no_point:
                                self.failed_places_no_point.write(place + "\n")
                                self.failed_places_no_point.flush()

    def get_place_info_from_json(self, json): 
        try:
            lat = json["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]["latitude"]
            lon = json["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]["longitude"]
            try:
                name = json["labels"]["en"]["value"]
            except:
                try:
                    name = json["claims"]["P373"][0]["mainsnak"]["datavalue"]["value"]
                except:
                    name = ""

            return {
                "lat": lat,
                "lon": lon,
                "name": name
            }, None
        except Exception as e:
            #print(json_resp)
            print(e)
            return None, e
            
    # Returns a json object with place-information
    def init_database(self, db_path):
        return json.loads("{}")

    def save_database(self, db_path):
        if (os.path.exists(os.path.dirname(db_path)) == False):
            os.mkdir(os.path.dirname(db_path))
        fh = open(db_path, "w+")
        json.dump(self.db, fh)
        fh.close()
        print("Data was saved to " + db_path + "!")
