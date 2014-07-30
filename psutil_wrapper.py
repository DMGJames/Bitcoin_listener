'''
Created on Jul 24, 2014

@author: webber
'''
import sys
import os
import psutil

BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * BYTES_PER_KB
BYTES_PER_GB = 1024 * BYTES_PER_MB
BYTES_PER_TB = 1024 * BYTES_PER_GB

class PsutilWrapper:
    def __init__(self):
        self.__init_base__()

    def __init__(self, pid):
        self.__init_base__()
        self.set_process(pid)

    def __init_base__(self):
        self.process = None
        self.last_rss = 0
        self.last_vms = 0
        self.start_rss = None
        self.start_vms = None
        self.end_rss = None
        self.end_vms = None

    def set_process(self, pid):
        self.process = psutil.Process(pid)

    def memory_now(self, readable = True, tag = ""):
        rss, vms = self.process.memory_info()
        rss_diff = self.__get_memory_diff__(self.last_rss, rss)
        vms_diff = self.__get_memory_diff__(self.last_vms, vms)
        self.last_rss = rss
        self.last_vms = vms
        
        rss_str = self.__get_memory_str__(rss, readable, False)
        vms_str = self.__get_memory_str__(vms, readable, False)
        rss_diff_str = self.__get_memory_str__(rss_diff, readable, True)
        vms_diff_str = self.__get_memory_str__(vms_diff, readable, True)
        if rss_diff > 5 * BYTES_PER_MB:
            rss_diff_str += "**"
        if vms_diff > 10 * BYTES_PER_MB:
            vms_diff_str += "$$"
        print "memory_now@{}: rss: {} ({}), vms: {} ({})".format(tag, rss_str, rss_diff_str, vms_str, vms_diff_str)
        sys.stdout.flush()

    def memory_start(self):
        self.start_rss, self.start_vms = self.process.memory_info()

    def memory_end(self):
        self.end_rss, self.end_vms = self.process.memory_info()

    def memory_between(self, readable = True, tag = ""):
        rss = self.__get_memory_diff__(self.start_rss, self.end_rss)
        vms = self.__get_memory_diff__(self.start_vms, self.end_vms)
        rss = self.__get_memory_str__(rss, readable, False)
        vms = self.__get_memory_str__(vms, readable, False)
        print "memory_between@{}: rss: {}, vms: {}".format(tag, rss, vms)
        sys.stdout.flush()
    
    def __get_memory_diff__(self, start, end):
        return end - start

    def __get_signed_number__(self, number):
        if number >= 0:
            return "+" + str(number)
        else:
            return str(number)

    def __get_memory_str__(self, memory, readable, signed):
        minus = False
        if memory < 0:
            minus = True
            memory = -memory
        if readable:
            result = self.__get_readable_memory__(memory)
        else:
            result = str(memory)
        if minus:
            result = "-" + result
        else:
            if signed:
                result = "+" + result
        return result
    
    def __get_readable_memory__(self, bytes):
        if bytes < BYTES_PER_KB:
            result = str(bytes)
        elif bytes < BYTES_PER_MB:
            result = str(round(self.__bytes_to_kb__(bytes), 1)) + "K"
        elif bytes < BYTES_PER_GB:
            result = str(round(self.__bytes_to_mb__(bytes), 1)) + "M"
        elif bytes < BYTES_PER_TB:
            result = str(round(self.__bytes_to_gb__(bytes), 1)) + "G"
        else:
            result = str(round(self.__bytes_to_tb__(bytes), 1)) + "T"
        return result
        
    def __bytes_to_kb__(self, bytes):
        return bytes / float(BYTES_PER_KB)

    def __bytes_to_mb__(self, bytes):
        return bytes / float(BYTES_PER_MB)

    def __bytes_to_gb__(self, bytes):
        return bytes / float(BYTES_PER_GB)
    
    def __bytes_to_tb__(self, bytes):
        return bytes / float(BYTES_PER_TB)

