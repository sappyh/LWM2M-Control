'''
Library for RESTful API calls to the leshan server

Pasha Stone
pasha.stone@sandc.com

Alex Lundberg
alex.lundberg@sandc.com
'''

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import os

class LRest():
    '''Wrapper class for robot libraries in python that use RESTful API'''

    def __init__(self,server,client):
        '''sets the information required for REST commands
        Keyword arguments:
        leshanServer -- the ip address and port where the leshan server is residing.
        clientEndPoint -- the client end point viewable on the leshan server
        clientNumber -- the client number viewable on leshan server. If only one client on a server than this is zero.
        xmlFolder -- the model folder that contains the GUI element data for the leshan server.
        '''
        self.server = server
        self.client = client
        self.object_mappings = self.getSource(server,client)
        #self.object_mappings = self.parseUrl('http://' + server + '/#/clients/' + client)

    def get(self, resource, object_='default' ,instance=0, timeout=4):
        '''reads the value of the specified instance and resource on the leshan server
        Keyword arguments:
        instance -- string of the instance, eg LED,LCD,Button.
        resource -- string of the resource, eg switch_1_closed, battery_test.
        '''

        # make request
        r = requests.get('http://'+ self.server+ '/api/clients/'+ self.client +self.object_mappings[object_][instance][resource],timeout=timeout)

        # raise error if http request fails
        r.raise_for_status()
        # convert the output into a dictionary and return the result
        rDict = json.loads(r.text)
        return rDict['content']['value']

    def put(self, instance, resource, text, timeout = 4):
        '''writes text to the given instance on the leshan server
        Keyword arguments:
        instance -- string of the instance, eg LED,LCD,Button.
        resource -- string of the resource, eg switch_1_closed, battery_test.
        '''
        # make request
        '''
        r = requests.put(
            'http://' + self.leshanServer + '/api/clients/' + self.clientEndpoint + '/' + self.mappings[instance][
                'id'] + '/' + self.clientNumber + '/' + self.mappings[instance]['resource'][resource],
            json={'id': self.mappings[instance]['resource'][resource], 'value': text},timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()

        '''
    def post(self, instance, resource, timeout = 4):
        '''Posts to the given instance on the leshan server
        Keyword arguments:
        instance -- string of the instance, eg LED,LCD,Button.
        resource -- string of the resource, eg switch_1_closed, battery_test.
        '''
        '''
        # make request
        r = requests.post(
            'http://' + self.leshanServer + '/api/clients/' + self.clientEndpoint + '/' + self.mappings[instance][
                'id'] + '/' + self.clientNumber + '/' + self.mappings[instance]['resource'][resource],timeout=timeout)

        # raise error if http request fails
        r.raise_for_status()
        '''

    def getSource(self,server,client):
        '''returns the source from a file if available or the html if not'''
        for file_name in os.listdir('cached_clients'):
            if file_name==client:
                return json.load(open(file_name))

        return self.getSourceFromHTML(server,client)

    def getSourceFromHTML(self,server,client):
        #launch headless chrome
        driver = self.setBrowser()

        #get the raw html from the webpage
        encoded_source = self.fetchHTML(driver,'http://' + server + '/#/clients/' + client)

        #parse the url into json
        page_objects = self.parseHTML(BeautifulSoup(encoded_source,'html.parser'))

        #cache the page_objects of this client so we dont have to connect to its server again to fetch html
        self.cacheClient(page_objects,client)

        return page_objects

    def fetchHTML(self,driver,url):
        #driver.get(url)
        driver.get('https://leshan.eclipse.org/#/clients/ezhiand-test-virtualdev-leshan')
        time.sleep(2)
        encoded_source=driver.page_source.encode('utf-8')
        driver.close()
        return encoded_source

    def setBrowser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        return webdriver.Chrome(chrome_options=options)

    def cacheClient(self,page_objects,client):
        f=open('cached_clients\\' + client + '.json','w')
        f.write(page_objects)

    def parseHTML(self,page_source):
        '''parses the url of the leshan client webpage into a dictionary containing each object, instance and resource.
        url - the url that contains the leshan client
        '''
        object_dict={}
        instance_dict={}
        resource_dict={}

        #the Leshan html is a tree structure with elements given as objects>instances>resources
        objects = page_source.find_all(attrs={'ng-repeat':'object in objects'})

        for object_ in objects:         
            instances = object_.find_all(attrs={'ng-repeat':'instance in object.instances'})

            for i in range(len(instances)):
                resources = instances[i].find_all(attrs={'ng-repeat':'resource in instance.resources'})
            
                for resource in resources:
                    resource_name = resource.find(class_='resource-name').text.strip()
                    resource_id = resource.find('button').attrs['tooltip-html-unsafe'].split('>')[1]

                    resource_dict[resource_name]=resource_id
            
                instance_dict[i]=resource_dict
                
            object_name = object_.find(class_='object-name').text.strip()
            object_dict[object_name] = instance_dict

        #convert the dictionary to json
        page_objects = json.dumps(object_dict)

        return page_objects
            

