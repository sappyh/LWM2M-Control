'''
Library for RESTful API calls to the leshan server

Pasha Stone
pasha.stone@sandc.com

Alex Lundberg
alex.lundberg@sandc.com
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from bs4 import BeautifulSoup
import json
import os
import requests
import json

class Client():
    '''Wrapper class for robot libraries in python that use RESTful API'''

    def __init__(self, url,refresh=False):
        '''sets the information required for REST commands
        Keyword arguments:
        url -- url of the leshan client
        refresh -- get the elements by scraping the html even if we have the client cached.
        '''
        self.url = url
        self.refresh = refresh
        self.page_objects = getSource(url,refresh)
        
    def read(self, resource, object_=None, instance=None, timeout=4):
        '''reads the value of the specified instance and resource on the leshan server
        Keyword arguments:
        instance -- string of the instance, eg LED,LCD,Button.
        resource -- string of the resource, eg switch_1_closed, battery_test.
        '''
        # search through dictionary to find the resource id to call
        res_id = self.searchDictionary(resource, object_, instance)
        # make request
        r = requests.get(self.url.replace('#', 'api') + res_id, timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()
        # convert the output into a dictionary and return the result
        rDict = json.loads(r.text)
        # return the value of the resource
        return rDict['content']['value']

    def write(self, text, resource, object_=None, instance=None, timeout=4):
        '''writes text to selected resource on the leshan server
        Keyword arguments:
        text -- text to write to resrouce
        resource -- resource you want to write to
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.searchDictionary(resource, object_, instance)
        # make request
        r = requests.put(self.url.replace('#', 'api') + res_id,
                         json={'id': res_id, 'value': text}, timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()

    def observe(self, resource, object_=None, instance=None, timeout=4):
        '''Observe the selected resource on the leshan server
        Keyword arguments:
        resource -- resource you want to observe
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.searchDictionary(resource, object_, instance)
        # make request
        r = requests.post(self.url.replace('#', 'api') +
                          res_id + '/observe', timeout=timeout)
        # raise error if http request fails
        r.raise_for_status()

    def discover(self, resource, object_=None, instance=None, timeout=4):
        '''discover the selected resource on the leshan server
        Keyword arguments:
        resource -- resource you want to observe
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.searchDictionary(resource, object_, instance)
        # make request
        r = requests.get(self.url.replace('#', 'api') +
                         res_id + '/discover', timeout=timeout)
        # raise error if request fails
        r.raise_for_status()

    def execute(self, resource, object_=None, instance=None, timeout=4):
        '''Execute the selected resource on the leshan server
        Keyword arguments:
        resource -- resource you want to observer
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.searchDictionary(resource, object_, instance)
        # make request
        r = requests.post(self.url.replace(
            '#', 'api') + res_id, timeout=timeout)
        # raise error if request fails
        r.raise_for_status()

    def delete(self, resource, object_=None, instance=None, timeout=4):
        '''delete the given resource on the leshan server.
        Keyword arguments:
        resource -- the resource to delete
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        timeout -- time to do rest command before timing out
        '''
        # search through dictionary to find the resource id to call
        res_id = self.searchDictionary(resource, object_, instance)
        # make request
        r = requests.delete(self.url.replace(
            '#', 'api') + res_id, timeout=timeout)
        # raise error if request fails
        r.raise_for_status()

    def searchDictionary(self, resource, object_=None, instance=None):
        '''search the page_objects dictionary for a match on the selected resource
        Keyword arguments:
        resource -- the resource to delete
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        '''
        matches = []

        if object_ is None:
            if instance is None:
                # if user did not supply object or instance then we check all objects and instances.
                for obj_key in self.page_objects.keys():
                    for inst_key in self.page_objects[obj_key].keys():
                        matches = self.searchInstances(
                            resource, obj_key, inst_key, matches)
            else:
                # if user supplied instance but not object then for each object we search entered instance
                # convert to string if user entered an int
                instance = str(instance)
                for obj_key in self.page_objects.keys():
                    matches = self.searchInstances(
                        resource, obj_key, instance, matches)
        else:
            try:
                # handle the case where the user entered an instance in the object_ variable.
                int(object_)
                # set instance to the object_ variable to be consistent
                instance = str(object_)
                # user didnt enter an actual object so we must loop through each object and then search for supplied instance
                for obj_key in self.page_objects.keys():
                    matches = self.searchInstances(
                        resource, obj_key, instance, matches)
            except:
                # the general case if the user enters in variables in the intended order
                if instance is None:
                    # if user supplied object but not instance we search through all instances in supplied object
                    for inst_key in self.page_objects[object_].keys():
                        matches = self.searchInstances(
                            resource, object_, inst_key, matches)
                else:
                    # the simplest case where the user entered both an instance and an object in the correct order.
                    matches = self.searchInstances(
                        resource, object_, instance, matches)

        if len(matches) == 0:
            raise ValueError(
                "Could not find a resource that satisfies conditions")

        return matches[0]

    def searchInstances(self, resource, object_, instance, matches):
        '''helper method of searchDictionary() that checks each resource in the supplied object_ and instance and returns the match.
        Keyword arguments:
        resource -- the resource to match
        object_ -- the highest level object containing the instance and resource
        instance -- the instance of this resource under the object
        '''
        # if this object doesnt have an instance we return an empty list
        if self.page_objects.get(object_).get(instance) is None:
            return []

        for res_key, res_val in self.page_objects[object_][instance].items():
            if res_key.lower() == resource.lower():
                matches.append(res_val)
            # throw error if we have found multiple resources with the conditions
            if len(matches) > 1:
                raise ValueError("Multiple resources were found that satisfy conditions to match resource: " +
                                 resource + ". Please specify instance number or object name")

        return matches

#Helper methods that dont depend on the client class
#These are used primary for parsing html or the json source
def getSource(url,refresh):
    '''returns the source from a file if available or the html if not
    Keyword arguments:
    url -- the url of the leshan client page
    refresh -- get a fresh copy of the dictionary from the html even if we have the client cached.
    '''
    client = url.split(r'/')[-1]
    if not refresh:
        # check if we have a chached dictionary of this client
        for file_name in os.listdir('cached_clients'):       
            if file_name == client+'.json':
                return json.load(open('cached_clients\\' + file_name))
    # if we dont then we have to do the more time consuming option of scraping the html
    return getSourceFromHTML(url, client)


def getSourceFromHTML(url, client):
    '''returns the dictionary of page_objects from the html of the client page
    Keyword arguments:
    url -- the url of the leshan client page
    client -- the name of the client gotten from the url
    '''
    # launch headless chrome
    driver = setBrowser()
    # get the raw html from the webpage
    encoded_source = fetchHTML(driver, url)
    # parse the url into json
    object_dict = parseHTML(BeautifulSoup(encoded_source, 'html.parser'))
    # raise error if parsing was not successful
    if len(object_dict) == 0:
        raise IOError("URL was not rendered into a dictionary")
    # cache the page_objects of this client so we dont have to connect to its server again to fetch html
    cacheClient(object_dict, client)
    return object_dict


def fetchHTML(driver, url):
    '''helper method of getSourceFromHTML that returns the html from the leshan client page
    Keyword arguments:
    url -- the url of the leshan client page
    driver -- selenium webdriver object 
    '''
    driver.get(url)
    #wait until the dom fully renders. We can check that we can find the object-name
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.object-name')))
    # html page is encoded in utf-8 so we must make that explicit
    encoded_source = driver.page_source.encode('utf-8')
    driver.close()
    return encoded_source


def setBrowser():
    '''helper method of getSourceFromHTML() that configures the browser'''
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    return webdriver.Chrome(chrome_options=options)


def cacheClient(object_dict, client):
    '''cache the page_object dictionary of the client so we don't need to scrape the html on future querries
    Keyword arguments:
    object_dict -- dictionary of page_objects that are sent to output file
    client -- name of the client file to store object_dict
    '''
    # convert the dictionary to json string
    page_objects = json.dumps(object_dict)
    # open and write the json string to file
    f = open('cached_clients\\' + client + '.json', 'w')
    f.write(page_objects)


def parseHTML(page_source):
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
