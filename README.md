# LeshanRestAPI
RESTful Library Wrapper for Leshan IOT.

## Installation
Install using pip  
`pip install LeshanRestAPI`

## Getting Started
Find the url of the Leshan client you want to interface with. Some examples are found on on the [leshan website](https://leshan.eclipse.org/#/clients)  
First import the library and instantiate a new class of Client(), passing in the url. If this is the first time you have connected to this client, the html will be extracted and cached in the cached_clients folder in the installation directory of this library. Future connections will use this json cache to avoid the time consuming process of extracting the html from the client webpage. If the webpage has changed from your cache, supply the parameter refresh=True to your instantiation of Client().  

LeshanRestAPI uses json representation of the client objects and searches this dictionary for a match on the resource supplied by the user. The user can supply additional parameters instance or object_ if the client webpage has more than one resource with the same name.  

## Examples
```
from LeshanRestAPI import Client
runner = Client('https://leshan.eclipse.org/#/clients/358185090000024')
print(runner.read("Lifetime"))
runner.observe("Lifetime")
runner.execute("Update")
runner.discover("Lifetime")
```

## Methods
Available methods are 
```
read  
write  
observe  
discover  
excecute  
```
These methods take the following inputs in order:  
`resource,object_=None,instance_=None,timeout=TIMEOUT`  
Write takes an additional parameter: text  
`text,resource,object_None,instance=None,timeout=TIMEOUT`

## Additional Details
The user does not need to enter all details of the object for it to be found. In most cases, the resource name is sufficient. Only when there is more than one resource does the user need to provide additional information such as instance or object_.  Note in examples two and three that the instance can be overloaded in the object_ variable.
The following example illustrates this on this [client](https://leshan.eclipse.org/#/clients/358185090000024)
```
read("Lifetime")
read("Lifetime",0)    #search resource Lifetime on instance 0 with object not specified
read("Lifetime","0")  #search resource Lifetime on instance 0 with object not specified
read("Lifetime",None,0)   #search resource Lifetime on instance 0 with object not specified
read("Lifetime","LwM2M Server")   #search resource LifeTime on Object LwM2M Server with instance not specified
read("Lifetime","LwM2M Server",0)     #search resource LifeTime on Object LwM2M Server on instance 0 
```

Since "Lifetime" resource exists only once on this client. The user can use any of the above to read from it.

## Troubleshooting
If you cannot operate on a resource. Try operating on the resource directly through its webportal. Often times, methods are not allowed for a resource or the resource is not available.

More details of the leshan RESTful API is given [here](http://robertsrhapsody.blogspot.com/2018/01/eclipse-leshan-rest-apis.html)
