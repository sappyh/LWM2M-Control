'''
Library for RESTful API calls to the leshan server

Pasha Stone
pasha.stone@sandc.com

Alex Lundberg
alex.lundberg@sandc.com
'''

import requests
import time
import json
import GetSource


class LRest():
    '''Wrapper class for robot libraries in python that use RESTful API'''

    def __init__(self, url):
        '''sets the information required for REST commands
        Keyword arguments:
        url -- url of the leshan client
        '''
        self.url = url
        self.page_objects = GetSource.getSource(url)

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
