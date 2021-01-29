""" Loads program configuration from a file called "screenshot_compare.ini" into a config object.

Instance then passed to functions as required.


Adapted from https://pastebin.com/MjHfm1PT

http://docs.python.org/library/configparser.html

"""

import datetime
import json
import logging
import os.path
import sys

try:
    import configparser  # Python 3
except ImportError:
    import ConfigParser as configparser  # Python 2



def load_config():
    # 'Safe' is preferred, according to docs
    config = configparser.SafeConfigParser()
    config.read('screenshot_compare.ini')

    # Settings for read_seed.py
    sect = 'read_seed'
    globals()['seed_list'] = config.get(sect, 'seed_list')
    globals()['current_urls_csv'] = config.get(sect, 'current_urls_csv')    
    globals()['collection_id'] = config.get(sect, 'collection_id')
    globals()['name'] = config.get(sect, 'name')
    globals()['sort'] = config.getboolean(sect, 'sort')
    
    sect = 'create_archive_urls'
    globals()['archive_urls_csv'] = config.get(sect, 'archive_urls_csv')
    globals()['banner'] = config.getboolean(sect, 'banner')
    
    sect = 'current_screenshot'
    globals()['current_index_csv'] = config.get(sect, 'current_index_csv')
    globals()['current_pics_dir'] = config.get(sect, 'current_pics_dir')
    globals()['c_method'] = config.getint(sect, 'method')
    globals()['c_screen_height'] = config.getint(sect, 'c_screen_height')
    globals()['c_screen width'] = config.getint(sect, 'c_screen_width')
    globals()['c_timeout'] = config.getint(sect, 'c_timeout')
    globals()['c_keep_cookies'] = config.get(sect, 'c_keep_cookies')
    globals()['c_chrome_args'] = config.get(sect, 'c_chrome_args')
    globals()['c_range_min'] = config.getint(sect, 'c_range_min')
    globals()['c_range_max'] = config.getint(sect, 'c_range_max')
    
    sect = 'archive_screenshot'
    globals()['archive_pics_dir'] = config.get(sect, 'archive_pics_dir')
    globals()['archive_index_csv'] = config.get(sect, 'archive_index_csv')
    globals()['a_method'] = config.getint(sect, 'a_method')
    globals()['a_screen_height'] = config.getint(sect, 'a_screen_height')
    globals()['a_screen_width'] = config.getint(sect, 'a_screen_width')
    globals()['a_timeout'] = config.getint(sect, 'a_timeout')
    globals()['a_keep_cookies'] = config.get(sect, 'a_keep_cookies')
    globals()['a_chrome_args'] = config.get(sect, 'a_chrome_args')
    globals()['a_range_min'] = config.getint(sect, 'a_range_min')
    globals()['a_range_max'] = config.getint(sect, 'a_range_max')
    

    sect = 'get_file_names'
    globals()['file_names_csv'] = config.get(sect, 'file_names_csv')
    globals()['print'] = config.getboolean(sect, 'print')
    
    sect = 'calculate_similarity'
    globals()['ssim'] = config.getboolean(sect, 'ssim')
    globals()['mse'] = config.getboolean(sect, 'mse')
    globals()['vector'] = config.getboolean(sect, 'vector')
    globals()['scores_file_csv'] = config.get(sect, 'scores_file_csv')
    globals()['similarity_print'] = config.getboolean(sect, 'similarity_print')
    
    
