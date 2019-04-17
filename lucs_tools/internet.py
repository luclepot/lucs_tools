import selenium.webdriver
import os
from platform import system as platform_system
from glob import glob as glob_glob
from time import time as time_time
import json 
import logging
from lucs_tools.logs import get_logger, set_loglevel

class exceptions:
    class NoMatchingWebDriver(Exception):
        code = 1
    class MultipleMatchingWebDrivers(Exception):
        code = 2

def select_default_webdriver(
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

def grab_json(
    name,
    path='',
):
    if path=='' or path=='pwd':
        datafile_path = '{}.json'.format(name)
    else:
        datafile_path = '{}/{}.json'.format(path, name)
    if os.path.exists(datafile_path):
        with open(datafile_path, 'r') as f:
            return json.load(f)
    return {}

def dump_json(
    data,
    name,
    path='',
):
    if path=='' or path=='pwd':
        datafile_path = '{}.json'.format(name)
    else:
        datafile_path = '{}/{}.json'.format(path, name)
    with open(datafile_path, 'w+') as f:
        json.dump(data, f)

class offline_internet_base_util:
    """
    seperate utility class comtaining the offline component of the internet base utility class
    useful for giving offline functionality to internet-related scraping utilities. 
    """
    
    SUBMODULE_NAME = __file__.replace('.py', '').split('/')[-1].split('\\')[-1]
    SUBMODULE_DATA_PATH = '{}/data/{}'.format(os.path.dirname(os.path.abspath(__file__)), SUBMODULE_NAME)
    PLATFORM = platform_system().lower()

    def __init__(
        self,
        data_path=None,
        loglevel=20,
    ):

        self.DATA_PATH = self.SUBMODULE_DATA_PATH if data_path is None else data_path

        self.metrics = {}
        self.known_cookies = {}

        self.log = get_logger(__name__)
        set_loglevel(loglevel, __name__) 

    def add_metric(
        self,
        param, 
        spec,
        name,
        function,
    ):
        self.metrics[name] = tuple((param, spec, name, function))

    def load_cookies(
        self,
        cookiename='',
        cookiepath=None,
    ):
        if cookiepath is None:
            cookiepath = self.DATA_PATH
        return grab_json('{}.cookiemonster'.format(cookiename), cookiepath)

    def clear_cookies(
        self,
        cookiename='',
        cookiepath=None,
    ):
        if cookiepath is None:
            cookiepath = self.DATA_PATH
        os.remove('{}/{}.cookiemonster'.format(cookiepath, cookiename))
        self.log.debug('cleared cookie \'{}/{}.cookiemonster\''.format(cookiepath, cookiename))

class internet_base_util(offline_internet_base_util):
    """
    fully online internet related base utility!!
    """
    def __init__(
        self,
        driver_path=None,
        data_path=None,
        options=None,
        loglevel=20,
    ):
        super().__init__(
            data_path,
            loglevel,
        )

        self.driver_path = self.check_and_get_driver_path(driver_path)
        if options is not None:
            chrome_options = selenium.webdriver.ChromeOptions()
            for argument in options:
                chrome_options.add_argument(argument)
            self.driver = selenium.webdriver.Chrome(
                chrome_options=chrome_options,
                executable_path=self.driver_path
            )
        else:
            self.driver = selenium.webdriver.Chrome(
                executable_path=self.driver_path
            )

    ### DRIVER HANDLING

    def check_and_get_driver_path(
        self,
        driver_path
    ):
        if driver_path is None or not os.path.exists(driver_path):
            driver_path = select_default_webdriver(
                '*{}*'.format(self.PLATFORM),
                '{}/default_webdrivers'.format(self.SUBMODULE_DATA_PATH)
            )
        return driver_path

    ### METRICS

    def get_data_from_named_metric(
        self,
        named_metric,
    ):
        param, spec, name, function = self.metrics[named_metric]
        return self.get_data_from_metric(
            param, 
            spec, 
            function
        )

    def get_data_from_metric(
        self,
        param, 
        spec,
        process_func,
    ):
        self.log.debug('grabbing metric {} = {}'.format(param, spec))
        try:
            elts = self.get_elements_with_param_matching_spec(param, spec)
            self.log.debug("grabbed {}".format(len(elts)))
            if len(elts) > 0:
                # return process_func(elts[0])
                self.log.debug('attempting to process and return elts')
                return process_func(elts)
            else:
                raise selenium.common.exceptions.NoSuchElementException
        except:
            self.log.debug('finding/processing metric failed, returning None')
            return None

    ### LINK HANDLING

    def open_link(
        self,
        link
    ):
        self.log.debug('opening link {}'.format(link))
        self.driver.get(link)
        self.current_link = link

    def open_link_with_timeout(
        self,
        link,
        max_timeout=120.
    ):
        # attempt to move to link
        self.open_link(link)
        t0 = time_time() 
        timeout = time_time() - t0
        while link not in self.driver.current_url and timeout < max_timeout:
            timeout = time_time() - t0
        
        # make sure we didn't just time out, and actually made it to art
        if timeout >= max_timeout:
            raise TimeoutError('Login period exceeded the given timeout period of {} seconds! Be quicker, or raise the timeout limit.'.format(max_timeout))
        
        return 0

    ### ELEMENT GRABBING ETC. 

    def get_elements_with_param_matching_spec(
        self,
        param,
        spec
    ):
        att_str = 'find_elements_by_{}'.format(param)
        if hasattr(self.driver, att_str):
            return getattr(self.driver, 'find_elements_by_{}'.format(param))(spec)
        return self.driver.find_elements_by_xpath("//a[contains(@{}, '{}')]".format(param, spec))
        
    def get_element_with_param_matching_spec(
        self,
        param,
        spec
    ):
        if hasattr(self.driver, 'find_element_by_{}'.format(param)):
            return getattr(self.driver, 'find_element_by_{}'.format(param))(spec)
        return self.driver.find_element_by_xpath("//a[contains({}, '{}')]".format(param, spec))

    ### COOKIES

    def write_cookies(
        self,
        cookiename='',
        cookiepath=None,
    ):
        if cookiepath is None:
            cookiepath = self.DATA_PATH
        dump_json(self.driver.get_cookies(), '{}.cookiemonster'.format(cookiename), cookiepath)
        self.log.debug('wrote cookies!')

    def add_cookies(
        self,
        cookiename='',
        cookiepath=None,
    ):
        for cookie in self.load_cookies(cookiename, cookiepath):
            self.driver.add_cookie(cookie)

class autodiff(internet_base_util):

    def diff(
        self,
        f1,
        f2,
    ):
        assert(all(map(os.path.exists, [f1, f2])))
        try:
            if 'diffchecker.com' not in self.driver.current_url:
                self.open_link('https://www.diffchecker.com/')
            inputs = self.get_elements_with_param_matching_spec('class_name', 'diff-input-text')
            texts = open(f1).read(), open(f2).read()
            
            for finput, ftext in zip(inputs, texts):
                finput.click()
                finput = self.driver.switch_to_active_element()
                finput.clear()
                finput.send_keys(ftext)
            self.get_element_with_param_matching_spec('class_name', 'jsx-1908705389').click()

        except Exception as e:
            for elt in str(e).split('\n'):
                self.log.error(elt)
            self.log.error('an error was caught. aborting diff')

    def diff_multiple(
        self,
        f1_list,
        f2_list,
    ):
        assert(all(map(lambda x: isinstance(x, list), [f1_list, f2_list])))
        for f1, f2 in zip(f1_list, f2_list):
            self.diff(f1, f2)
