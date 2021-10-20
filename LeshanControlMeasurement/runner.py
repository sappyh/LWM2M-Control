from __init__ import Server
from __init__ import clientRead
from timeloop import Timeloop
from datetime import timedelta
import time
import threading
import random
import logging

server = Server('http://127.0.0.1:8080')
print(server)
clientlist=[]

mesgpersec=5
tl=Timeloop()

@tl.job(interval=timedelta(seconds=1))
def get_client_list():
    global clientlist
    clientlist = server.getClients()
    print(clientlist)

@tl.job(interval=timedelta(seconds=1/mesgpersec))
def read_client():
    threads=[]
    global clientlist
    if clientlist:
        for client in clientlist:
            t = threading.Thread(target=clientRead, args=(client,'/3303/0/5700', logger))
            threads.append(t)
            t.start()
    if threads:
        for t in threads:
            if(t.is_alive()):
                t.join()

##Create logger
open("Measurement.csv", "w").close()

logger = logging.getLogger('Measurement')
logger.setLevel(logging.INFO)

#Create log handler
fh= logging.FileHandler('Measurement.csv')
fh.setLevel(logging.INFO)

formatter=logging.Formatter("%(asctime)s, %(message)s")

fh.setFormatter(formatter)

logger.addHandler(fh)

tl.start()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        tl.stop()
        break