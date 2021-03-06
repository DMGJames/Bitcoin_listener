'''
Created on Jun 11, 2014

@author: yutelin
'''
import pygeoip
from decimal import Decimal
from constants import ATTRIBUTE_COUNTRY_CODE, ATTRIBUTE_LATITUDE, ATTRIBUTE_LONGITUDE,\
    ATTRIBUTE_TIME_ZONE, ATTRIBUTE_CITY, FILENAME_GEO_CITY, FILENAME_GEO_CITY_V6,\
    FILENAME_GEO_ASN, FILENAME_GEO_ASN_V6, ATTRIBUTE_COUNTRY, ATTRIBUTE_ASN, ATTRIBUTE_ORG,\
    ATTRIBUTE_HOSTNAME, ATTRIBUTE_USER_AGENT, ATTRIBUTE_VERSION, ATTRIBUTE_START_HEIGHT
import socket
import logging
from bitnodes.protocol import Connection, ProtocolError
import os
file_dir = os.path.dirname(os.path.realpath(__file__))

GEOIP4 = pygeoip.GeoIP(os.path.join(file_dir, FILENAME_GEO_CITY), pygeoip.MMAP_CACHE)
GEOIP6 = pygeoip.GeoIP(os.path.join(file_dir, FILENAME_GEO_CITY_V6), pygeoip.MMAP_CACHE)
ASN4 = pygeoip.GeoIP(os.path.join(file_dir, FILENAME_GEO_ASN), pygeoip.MMAP_CACHE)
ASN6 = pygeoip.GeoIP(os.path.join(file_dir, FILENAME_GEO_ASN_V6), pygeoip.MMAP_CACHE)

def __get_raw_geoip__(address):
    """
    Resolves GeoIP data for the specified address using MaxMind databases.
    (Modified from Bitnodes code)
    """
    city = None
    country = None
    latitude = None
    longitude = None
    timezone = None
    asn = None
    org = None

    geoip_record = None
    prec = Decimal('.000001')
    if ":" in address:
        geoip_record = GEOIP6.record_by_addr(address)
    else:
        geoip_record = GEOIP4.record_by_addr(address)
    if geoip_record:
        city = geoip_record[ATTRIBUTE_CITY]
        country = geoip_record[ATTRIBUTE_COUNTRY_CODE]
        latitude = float(Decimal(geoip_record[ATTRIBUTE_LATITUDE]).quantize(prec))
        longitude = float(Decimal(geoip_record[ATTRIBUTE_LONGITUDE]).quantize(prec))
        timezone = geoip_record[ATTRIBUTE_TIME_ZONE]

    asn_record = None
    if ":" in address:
        asn_record = ASN6.org_by_addr(address)
    else:
        asn_record = ASN4.org_by_addr(address)
    if asn_record:
        data = asn_record.split(" ", 1)
        asn = data[0]
        if len(data) > 1:
            org = data[1]

    return {ATTRIBUTE_CITY: city, ATTRIBUTE_COUNTRY: country, ATTRIBUTE_LATITUDE: latitude, 
            ATTRIBUTE_LONGITUDE: longitude, ATTRIBUTE_TIME_ZONE: timezone, 
            ATTRIBUTE_ASN: asn, ATTRIBUTE_ORG: org}
    
def __get_raw_hostname__(address):
    """
    Resolves hostname for the specified address using reverse DNS resolution.
    (Modified from Bitnodes code)
    """
    hostname = address
    try:
        hostname = socket.gethostbyaddr(address)[0]
    except (socket.gaierror, socket.herror) as err:
        logging.debug("{}: {}".format(address, err))
    return {ATTRIBUTE_HOSTNAME: hostname}


def __get_bitcoin_node_info__(address, port):
    connection = Connection((address, port))
    user_agent = None
    version = None
    start_height = None

    try:
        connection.open()
        handshake_msgs = connection.handshake()
        if handshake_msgs and len(handshake_msgs) > 1:
            user_agent = handshake_msgs[0].get(ATTRIBUTE_USER_AGENT)
            version =  handshake_msgs[0].get(ATTRIBUTE_VERSION)
            start_height = handshake_msgs[0].get(ATTRIBUTE_START_HEIGHT) 
    except (ProtocolError, socket.error) as err:
        logging.debug("Closing {} ({})".format(connection.to_addr, err))
        connection.close()

    return {ATTRIBUTE_USER_AGENT : user_agent, ATTRIBUTE_VERSION: version, ATTRIBUTE_START_HEIGHT:  start_height}

def get_node_info(address, port):
    geo_data = __get_raw_geoip__(address = address)
    host_data = __get_raw_hostname__(address = address)
    node_data = __get_bitcoin_node_info__(address = address, port = port)
    return dict(geo_data.items() + host_data.items() + node_data.items())