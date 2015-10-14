


import json
import urllib.request as request

class WikiFetcher():

    def __init__(self):
        self.id_query_templ = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={idlist}&format=json&languages=en"
        pass

    def get_json_resp(self, url):
        req = request.urlopen(url)
        cont = req.read()
        cont = cont.decode("UTF-8")
        resp_json = json.loads(cont)
        return resp_json

    def get_items_from_query(self, url):
        json_resp = self.get_json_resp(url)
        items = json_resp["items"]
        items = ["Q" + str(item) for item in items]
        return items

    def get_json_for_id_list(self, id_list):
        #print(self.id_query_templ.format(idlist=id_list))
        json_resp = self.get_json_resp(self.id_query_templ.format(idlist="|".join(id_list)))
        return json_resp
