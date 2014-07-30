'''
Created on Jul 24, 2014

@author: webber
'''
import os
import gc
from psutil_wrapper import PsutilWrapper

if __name__ == '__main__':
    gc.enable()
    ps = PsutilWrapper(os.getpid())
    ps.memory_start()
    r = range(1,2000000)
    del r
    gc.collect()
    #len(gc.get_objects())
    ps.memory_end()
    ps.memory_print(tag="r")
