from __init__ import Client

runner = Client('http://localhost:5004/#/clients/6803-10.20.51.218')
#print(runner.printPageObjects())
print(runner.read('switch 1 closed','0'))
print(runner.read('switch 1 closed',0))
print(runner.read('switch 1 closed','0',None))
print(runner.read('switch 1 closed',0,None))
print(runner.read('switch 1 closed',None,0))
print(runner.read('switch 1 closed',None,'0'))
print(runner.read('switch 1 closed','LEDs',0))
print(runner.read('switch 1 closed','LEDs','0'))
print(runner.read('switch 1 closed','LEDs',None))
print(runner.read('switch 1 closed','LEDs'))
print(runner.read('switch 1 closed','LEDs','0'))
print(runner.read('switch 1 closed','0','LEDs'))


