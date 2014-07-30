'''
Created on Jul 30, 2014

@author: yutelin
'''

##### Set environment #####
import os
from os.path import sys
def set_env():
    # 1. Append current file directory as path
    file_dir = os.path.dirname(os.path.realpath(__file__))
    #sys.path.append(file_dir)
    sys.path.append(file_dir+"/../")
    print sys.path
set_env()
########################################################################
from models import AddressTag
from common import set_session
import csv
import re
import json

class AddressTagParser:
    def __init__(self, session, csv_file, txt_file):
        self.session = session
        self.csv_file = csv_file
        self.txt_file = txt_file
        
    def parse(self):
        items = []
        #1. Parse
        with open(self.csv_file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                open_address = self.__array_to_address_tag__(row)
                if open_address: items.append(open_address)
        
        #2. Parse txt file
        lines = [line.strip() for line in open(self.txt_file)]
        for line in lines:
            open_address = self.__line_to_address_tag__(line)
            if open_address: items.append(open_address)
        
        #3. Update
        print "Address size:", len(items)
        for item in items:
            print "Add:", item.__dict__
            try:
                self.session.merge(item)
                self.session.commit()
            except Exception, e:
                self.session.rollback()
                print "Exception on parse:", e
        
        
         
    def __array_to_address_tag__(self, data, source = 'bitcointalk'):
        result = None
        if data and len(data) == 3:
            try:
                user_id = int(data[0])
                tag = data[1]
                m = re.search("[13][a-km-zA-HJ-NP-Z0-9]{26,33}$", data[2])
                address = m.group(0)
                link = None
                if source == 'bitcointalk':
                    link = "https://bitcointalk.org/index.php?action=profile;u=%s" % (user_id)
                result = AddressTag(user_id = user_id, 
                                    tag = tag, 
                                    address = address, 
                                    source = source,
                                    link = link)
            except Exception, e:
                print "Exception on __array_to_address_tag__", data,  e
        return result

    def __line_to_address_tag__(self, line):
        result = None
        address_dict = json.loads(line)
        try:
            result = AddressTag(tag = address_dict.get('tag'),
                                link = address_dict.get('tag_link'),
                                verified = address_dict.get('verified'),
                                address = address_dict.get('addr'))
        except Exception, e:
            print "Exception on __line_to_address_tag__", line, e
        return result
        
env_setting = 'local'
if __name__ == '__main__':
    env_setting = sys.argv[1]
    csv_file = sys.argv[2]
    txt_file = sys.argv[3]
    print "Environment:" , env_setting, csv_file
    session = set_session(env_setting=env_setting)
    parser = AddressTagParser(session, csv_file, txt_file)
    parser.parse()
    print "Done!"