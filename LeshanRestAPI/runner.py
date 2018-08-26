from __init__ import Client

runner = Client('https://leshan.eclipse.org/#/clients/358185090000024')
print(runner.read("Lifetime"))