from cProfile import run
from calendar import prcal
from cgi import test
from locale import currency
from pdb import Pdb
from io import BytesIO
from multiprocessing import Process

import os
import tarfile
from time import sleep

a,b = os.pipe()
c,d = os.pipe()

def runpdb(pip):
    f2 = os.fdopen(pip, 'w')
    instance = Pdb(stdout=f2)
    Pdb._runscript(instance, './test.py')

p = Process(target=runpdb, args=(d, ))
p.start()
res = os.read(c, 1000)
print(res)
p.join()

