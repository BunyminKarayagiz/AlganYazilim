import requests
import time

class MAVLINK():
    def __init__(self) -> None:
        self.URL = "http://" + "localhost"+ ":56781"  + "/mavlink/"
        #self.URL = "http://127.0.0.1:56781/mavlink/"
        self.data:any

    def get(self):
        start=time.time()
        r = requests.get(url = self.URL)
        print(r.json())
        final=time.time()-start
        print(final)
    def parse(self):
        pass

#TEST

mavlink_obj = MAVLINK()
while True:
    
    mavlink_obj.get()
