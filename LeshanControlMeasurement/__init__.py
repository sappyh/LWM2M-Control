import os
import requests
import json
import datetime
import logging
import time
import random

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TIMEOUT = 5000

class Server():
    '''returns information on the clients attached to the server'''
    def __init__(self, url):
        self.url=url

    def getClients(self,timeout=TIMEOUT):
        '''return the client endpoints attached to this server'''
        #sometimes the user may enter the url of the server with or without the #/clients appended to it.
        if "clients" in self.url:
            r = requests.get(self.url.replace('#','api'), timeout=timeout)
        else:
            r = requests.get(self.url + "/api/clients", timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()
        # return result
        rDict = json.loads(r.text)
        clientList=[]
        for client in rDict:
            endpoint= client['endpoint']
            clientList.append(self.url + "/api/clients/"+endpoint)
        return clientList

    def __str__(self):
        return self.url

def clientRead(requestUrl, resource, logger, timeout=TIMEOUT):
        time.sleep(random.randrange(40))
        
        # raise error if http request fails
        try:
            start=datetime.datetime.now()
            r = requests.get(requestUrl + resource, timeout=timeout)
            end=datetime.datetime.now()
            rtt=(end-start).total_seconds()*1000
            r.raise_for_status()
            # convert the output into a dictionary and return the result
            hDict = r.headers
            rDict = json.loads(r.text)
            client_name= requestUrl.split("/")[-1]
            logger.info("Client Name: "+client_name+",LWM2M RTT: "+hDict['RTT']+", Application RTT: "+'%.2f' % rtt+", Temperature: "+ str(rDict['content']['value']))
            # return the value of the resource
            # try:
            return rDict['content']['value'], int(hDict['RTT'])
            # except KeyError:
                # raise KeyError("resource " + resource +
                            # " is not available for reading")
        except requests.HTTPError:
            client_name= requestUrl.split("/")[-1]
            logger.info("Client Name: "+client_name+", Error")
            return 0,0
