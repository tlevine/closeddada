import os
import logging

filename = os.path.expanduser('~/.dadawarehouse/warehouse.log')

logger = logging.getLogger('dadawarehouse')
logger.setLevel(logging.DEBUG)

stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
logger.addHandler(stream)

'''
logfile = logging.FileHandler(filename, 'a')
logfile.setLevel(logging.DEBUG)
logger.addHandler(logfile)
'''
