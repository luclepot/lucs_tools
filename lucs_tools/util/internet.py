import selenium.webdriver
import os
from platform import system as platform_system
from glob import glob as glob_glob
from enum import Enum
from time import time as time_time
import numpy as np

class exceptions:
    class NoMatchingWebDriver(Exception):
        code = 1
    class MultipleMatchingWebDrivers(Exception):
        code = 2


class _base_util:
    SUBMODULE_NAME = __file__.replace('.py', '').split('/')[-1].split('\\')[-1]
    SUBMODULE_DATA_PATH = '{}/data/{}'.format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), SUBMODULE_NAME)
    PLATFORM = platform_system().lower()

    def _select_default(
        self,
        search_criteria,
        search_path,
        ignore_duplicates=False
    ):
        matching_webdrivers = glob_glob('{}/{}'.format(search_path, search_criteria))
        
        if len(matching_webdrivers) == 0:
            raise exceptions.NoMatchingWebDriver
        elif len(matching_webdrivers) > 1 and not ignore_duplicates:
            raise exceptions.MultipleMatchingWebDrivers    
        return matching_webdrivers[0]