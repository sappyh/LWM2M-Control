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
        #self.object_mappings = self.parseUrl('http://' + server + '/#/clients/' + client)
        self.object_mappings = self.parseUrl('http://169.254.235.45:5004/#/clients/6803-10.20.51.218')
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
    def parseUrl(self, url):
        '''parses the url of the leshan client webpage into a dictionary containing each object, instance and resource.
        url - the url that contains the leshan client
        '''
        object_dict={}
        instance_dict={}
        resource_dict={}
        default_instance_dict={}

        #soup = self.getSource(url)
        soup = self.getSourceFromText('out.txt')
        print(soup.prettify().encode('utf-8'))
        #the Leshan html is a tree structure with elements given as objects>instances>resources
        objects = soup.find_all(attrs={'ng-repeat':'object in objects'})

        for object_ in objects:         
            instances = object_.find_all(attrs={'ng-repeat':'instance in object.instances'})

            for i in range(len(instances)):
                resources = instances[i].find_all(attrs={'ng-repeat':'resource in instance.resources'})
            
                for resource in resources:
                    resource_name = resource.find(class_='resource-name').text
                    print(resource_name)
                    resource_id = resource.find('button').attrs['tooltip-html-unsafe'].split('>')[1]

                    resource_dict[resource_name]=resource_id

                #we make two separate dictionaries, for when the user searches with and without an object.
                instance_dict[i] = resource_dict
                #default_instance_dict[i]=[default_instance_dict[i],resource_dict]
                default_instance_dict.setdefault([i],[]).append(resource_dict)
            
            object_name = object_.find(class_='object-name').text
            object_dict[object_name] = instance_dict
            object_dict.setdefault(['default'],[]).append(default_instance_dict)
           # object_dict['default'] = [object_dict['default'],default_instance_dict]    

        print(object_dict)
        return object_dict
            
    def getSourceFromText(self,file_):
        '''get the source from an html text file instead of going to the webpage. for testing purposes'''
        f=open(file_)
        content=f.read()
        return BeautifulSoup(content,'html.parser')


    def getSource(self,url):
        '''returns the rendered html of the leshan client'''
        #launch headless chrome
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        driver = webdriver.Chrome(chrome_options=options)

        #navigate to leshan client and return rendered html source
        #driver.get(url)
        driver.get('http://169.254.235.45:5004/#/clients/6803-10.20.51.218')
        time.sleep(2)
        encoded_source=driver.page_source.encode('utf-8')
        driver.close()

        return BeautifulSoup(encoded_source,'html.parser')


    def printDictionary(self):
        '''prints the mappings dictionary'''
        print(self.mappings)

    def printInstances(self):
        '''prints available instances with their id'''
        print('instances: ')
        print(self.mappings.keys())

    def printResources(self, instance):
        '''prints resources associated to a instance'''
        print('resources on instance ' + instance + ': ')
        print(self.mappings[instance]['resource'].keys())