'''
Library for RESTful API calls to the leshan server

Pasha Stone
pasha.stone@sandc.com

Alex Lundberg
alex.lundberg@sandc.com
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os
import requests
import json

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TIMEOUT = 4

class Server():
    '''returns information on the clients attached to the server'''
    def __init__(self, url):
        self.url=url

    def getClients(self,timeout=TIMEOUT):
        '''return the client endpoints attached to this server'''
        r = requests.get(self.url + "/api/clients", timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()
        # return result
        rDict = json.loads(r.text)
        clientList=[]
        for client in rDict:
            clientList.append(client['endpoint'])
        return clientList

    def cacheClients(self,refresh=False):
        '''return a list of client objects attached to this server and cache the clients'''
        clientNames = self.getClients()
        clientList = []
        for clientName in clientNames:
            #initialize a new client, cache it and add it to a list
            client = Client(self.url + '/#/clients/' + clientName,refresh)
            clientList.append(client)
        return clientList

    def __str__(self):
        return self.url

class Client():
    '''Wrapper class for robot libraries in python that use RESTful API'''

    def __init__(self, url, refresh=False, models=None):
        '''sets the information required for REST commands
        Keyword arguments:
        url -- url of the leshan client
        refresh -- get the elements by scraping the html even if we have the client cached.
        '''
        self.url = url
        if 'clients' not in self.url:  #if we dont have the full clients name then we need to replace "client" with "clients"
            self.requestUrl = self.requestUrl.replace("client","clients")
        self.requestUrl = self.url.replace('#', 'api').replace("/default",'')
        # extract the client name from the html which we use for the name of the cached client.
        self.client = self.requestUrl.split(r'/')[-1]
        self.refresh = refresh
        self.models = models
        self.page_objects = self.__getSource()

    def read(self, resource, object_=None, instance=None, timeout=TIMEOUT):
        '''reads the value of the specified instance and resource on the leshan server
        Keyword arguments:
        instance -- string of the instance, eg LED,LCD,Button.
        resource -- string of the resource, eg switch_1_closed, battery_test.
        '''
        # search through dictionary to find the resource id to call
        res_id = self.__searchDictionary(resource, object_, instance)
        # make request
        r = requests.get(self.requestUrl + res_id, timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()
        # convert the output into a dictionary and return the result
        rDict = json.loads(r.text)
        # return the value of the resource
        try:
            return rDict['content']['value']
        except KeyError:
            raise KeyError("resource " + resource +
                           " is not available for reading")

    def write(self, text, resource, object_=None, instance=None, timeout=TIMEOUT):
        '''writes text to selected resource on the leshan server
        Keyword arguments:
        text -- text to write to resrouce
        resource -- resource you want to write to
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.__searchDictionary(resource, object_, instance)
        # make request
        r = requests.put(self.requestUrl + res_id,
                         json={'id': res_id.split("/")[-1], 'value': text}, timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()

    def observe(self, resource, object_=None, instance=None, timeout=TIMEOUT):
        '''Observe the selected resource on the leshan server
        Keyword arguments:
        resource -- resource you want to observe
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.__searchDictionary(resource, object_, instance)
        # make request
        r = requests.post(self.requestUrl +
                          res_id + '/observe', timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()

    def discover(self, resource, object_=None, instance=None, timeout=TIMEOUT):
        '''discover the selected resource on the leshan server
        Keyword arguments:
        resource -- resource you want to observe
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.__searchDictionary(resource, object_, instance)
        # make request
        r = requests.get(self.requestUrl +
                         res_id + '/discover', timeout=timeout)
        # raise error if request fails
        r.raise_for_status()

    def execute(self, resource, object_=None, instance=None, timeout=TIMEOUT):
        '''Execute the selected resource on the leshan server
        Keyword arguments:
        resource -- resource you want to observer
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.__searchDictionary(resource, object_, instance)
        # make request
        r = requests.post(self.requestUrl + res_id, timeout=timeout)
        # raise error if request fails
        r.raise_for_status()

    def delete(self, resource, object_=None, instance=None, timeout=TIMEOUT):
        '''delete the given resource on the leshan server.
        Keyword arguments:
        resource -- the resource to delete
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.__searchDictionary(resource, object_, instance)
        # make request
        r = requests.delete(self.requestUrl + res_id, timeout=timeout)
        # raise error if request fails
        r.raise_for_status()

    def assertread(self,assertValue,resource,object_=None,instance=None,timeout=TIMEOUT):
        '''check if output from read is equal to input string. Exists for testing ease in robot-framework.
        Keyword arguments:
        assertValue -- the string to assert equals on the value returned from the REST read call on resource.
        resource -- the resource to read.
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        assert(assertValue==self.read(resource,object_,instance,timeout))

    def __searchDictionary(self, resource, object_=None, instance=None):
        '''search the page_objects dictionary for a match on the selected resource
        Keyword arguments:
        resource -- the resource to delete
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        '''
        matches = []
        #TODO THIS IS BAD CODING. PUT THIS INTO EACH A SEPARATE METHOD!
        if object_ is None:
            if instance is None:
                # if user did not supply object or instance then we check all objects and instances.
                for obj_key in self.page_objects.keys():
                    for inst_key in self.page_objects[obj_key].keys():
                        matches = self.__searchInstances(
                            resource, obj_key, inst_key, matches)
            else:
                # if user supplied instance but not object then for each object we search entered instance
                # convert to string if user entered an int
                instance = str(instance)
                for obj_key in self.page_objects.keys():
                    matches = self.__searchInstances(
                        resource, obj_key, instance, matches)
        else:
            try:
                # check if the user swapped object and instance
                int(object_)
                # if so then we swap object and instance to be consistent
                temp = str(object_)
                object_ = str(instance.lower())
                instance = temp
                # user didnt enter an actual object so we must loop through each object and then search for supplied instance
                if object_ == 'None':
                    for obj_key in self.page_objects.keys():
                        matches = self.__searchInstances(
                            resource, obj_key, instance, matches)
                else:
                    matches = self.__searchInstances(
                        resource, object_, instance, matches)
            except ValueError:
                # the general case if the user enters in variables in the intended order
                # convert input object to lower case
                object_ = object_.lower()
                if instance is None:
                    # if user supplied object but not instance we search through all instances in supplied object
                    for inst_key in self.page_objects[object_].keys():
                        matches = self.__searchInstances(
                            resource, object_, inst_key, matches)
                else:
                    # the simplest case where the user entered both an instance and an object in the correct order.
                    # convert to instance number to a string.
                    instance = str(instance)
                    matches = self.__searchInstances(
                        resource, object_, instance, matches)

        if len(matches) == 0:
            raise LookupError(
                "Could not find a resource that satisfies conditions")

        return matches[0]

    def __searchInstances(self, resource, object_, instance, matches):
        '''helper method of searchDictionary() that checks each resource in the supplied object_ and instance and returns the match.
        Keyword arguments:
        resource -- the resource to match
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        '''
        # if this object doesnt have an instance we return to sender
        if self.page_objects.get(object_) is None or self.page_objects.get(object_).get(instance) is None:
            return matches

        for res_key, res_val in self.page_objects[object_][instance].items():
            if res_key.lower() == resource.lower():
                matches.append(res_val)
            # throw error if we have found multiple resources with the conditions
            if len(matches) > 1:
                raise LookupError("Multiple resources were found that satisfy conditions to match resource: " +
                                  resource + ". Please specify instance number or object name")

        return matches

    def __getSource(self):
        '''returns the source from a file if available or the html if not'''
        if not self.refresh:
            # check if we have a cached dictionary of this client
            for file_name in os.listdir(DIR_PATH + '\\cached_clients'):
                if file_name == self.client+'.json':
                    return json.load(open(DIR_PATH+'\\cached_clients\\' + file_name))
        # if we dont then we have to do the more time consuming option of scraping the html
        if self.models is None:
            return self.__getSourceFromHTML()
        else:
            return self.__getSourceFromXML()
    
    def __getSourceFromXML(self):
        '''returns the source from the xml models folder which shows the server side resources'''
        object_dict = {}
        for filename in os.listdir(self.models):
            if filename.endswith(".xml"): #ignore all files in models folder that are not xmls
                # get the root of the xml document
                root = ET.parse(os.path.join(self.models, filename)).getroot()

                object_name = root.findall('Object')[0].getchildren()[0].text
                object_id = root.findall('Object')[0].getchildren()[2].text

                instance_dict={}
                instance_id = '0'  #right now only one instance can be handled when using the xml parser.

                 # iterate through root, and create the dictionary of resources
                resource_dict = {}
                for resource in root.findall('Object/Resources/Item'):
                    resource_name = resource.getchildren()[0].text
                    resource_id = resource.attrib['ID'] 
                     #the resource_id given on the xml is different than the resource_id given by the html scrape so we convert this resource_id to be consistent
                    resource_dict[resource_name] = '/' + object_id + '/' + instance_id + '/' + resource_id

                # form the final outputDict
                instance_dict[instance_id] = resource_dict #as we are only parsing for one instance currently we do not need a for loop like in the html scape
                object_dict[object_name] = instance_dict

        return object_dict
        
    def __getSourceFromHTML(self):
        '''returns the dictionary of page_objects from the html of the client page'''
        # launch headless chrome
        driver = self.__setBrowser()
        # get the raw html from the webpage
        encoded_source = self.__fetchHTML(driver)
        # parse the url into json
        object_dict = self.__parseHTML(
            BeautifulSoup(encoded_source, 'html.parser'))
        # raise error if parsing was not successful
        if len(object_dict) == 0:
            raise IOError("URL was not rendered into a dictionary")
        # convert object_dict to lowercase
        object_dict = {k.lower(): v for k, v in object_dict.items()}
        # cache the page_objects of this client so we dont have to connect to its server again to fetch html
        self.__cacheClient(object_dict)
        return object_dict

    def __fetchHTML(self, driver):
        '''helper method of getSourceFromHTML that returns the html from the leshan client page
        Keyword arguments:
        driver -- selenium webdriver object 
        '''
        driver.get(self.url)
        # wait until the dom fully renders. We can check that we can find the object-name
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.object-name')))
        # html page is encoded in utf-8 so we must make that explicit
        encoded_source = driver.page_source.encode('utf-8')
        driver.close()
        return encoded_source

    def __setBrowser(self):
        '''helper method of getSourceFromHTML() that configures the browser'''
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        return webdriver.Chrome(chrome_options=options)

    def __cacheClient(self, object_dict):
        '''cache the page_object dictionary of the client so we don't need to scrape the html on future querries
        Keyword arguments:
        object_dict -- dictionary of page_objects that are sent to output file
        '''
        # convert the dictionary to json string
        page_objects = json.dumps(object_dict)
        # open and write the json string to file
        f = open(DIR_PATH + '\\cached_clients\\' + self.client + '.json', 'w')
        f.write(page_objects)

    def __parseHTML(self, page_source):
        '''parses the url of the leshan client webpage into a dictionary containing each object, instance and resource.
        Keyword arguments:
        page_source -- raw html to parse and return page_objects dictionary
        '''
        object_dict = {}
        # the Leshan html is a tree structure with elements given as objects>instances>resources
        objects = page_source.find_all(
            attrs={'ng-repeat': 'object in objects'})
        # for each object we find all elements that contain the instances
        for object_ in objects:
            instances = object_.find_all(
                attrs={'ng-repeat': 'instance in object.instances'})
            instance_dict = {}
            # for each instance element we find we find all resources attached to that resource
            for i in range(len(instances)):
                resources = instances[i].find_all(
                    attrs={'ng-repeat': 'resource in instance.resources'})
                resource_dict = {}
                # find the resource_name and id and put that into the dictionary
                for resource in resources:
                    resource_name = resource.find(
                        class_='resource-name').text.strip()
                    resource_id = resource.find(
                        'button').attrs['tooltip-html-unsafe'].split('>')[1]
                    resource_dict[resource_name] = resource_id
                instance_dict[i] = resource_dict
            # we put all the resource objects into a nested dictionary of object>instance>resources
            object_name = object_.find(class_='object-name').text.strip()
            object_dict[object_name] = instance_dict

        return object_dict

    def printPageObjects(self):
        '''helper method to pretty print the page_objects for debugging'''
        print(json.dumps(self.page_objects, indent=4, sort_keys=True))
    
    def __str__(self):
        return self.client