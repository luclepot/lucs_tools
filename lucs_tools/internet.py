from lucs_tools.util.internet import *
from lucs_tools.util.internet import _base_util

class internet_util(_base_util):
    def __init__(
        self,
        driver_path=None,
        options=None
    ):
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


    def open_link(
        self,
        link
    ):
        self.driver.get(link)
        self.current_link = link

    def check_and_get_driver_path(
        self,
        driver_path
    ):
        if driver_path is None or not os.path.exists(driver_path):
            driver_path = self._select_default(
                '*{}*'.format(self.PLATFORM),
                '{}/default_webdrivers'.format(self.SUBMODULE_DATA_PATH)
            )
        return driver_path

    def get_elements_with_param_matching_spec(
        self,
        param,
        spec
    ):
        return self.driver.find_elements_by_xpath("//a[contains({}, '{}')]".format(param, spec))
        
    def get_element_with_param_matching_spec(
        self,
        param,
        spec
    ):
        return self.driver.find_element_by_xpath("//a[contains({}, '{}')]".format(param, spec))


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


class course_guide_util():
    '''
    umich course guide utility
    '''

    letter_to_gpa_plot = {
        'A+': 4.3, #for display purposes..
        'A': 4.0,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3.0,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2.0,
        'C-': 1.7,
        'D+': 1.3,
        'D': 1.0,
        'D-': 0.7,
        'E': 0.0,
        }
    letter_to_gpa_raw = dict(letter_to_gpa_plot)
    letter_to_gpa_raw['A+'] = 4.0

    def __init__(
        self,
        search_results_link,
        driver_path=None,
    ):  

        self.default_search_link = search_results_link
        self._internet_util = internet_util(
            driver_path,
            options=['--start-maximized' if platform_system() == 'Windows' else '--kiosk']            
            )
        self.searches = {}
        self.class_data = {}

    def _get_class_list_from_elements(
        self,
        elements,
    ):
        return map(lambda elt: ' '.join(elt.text.split()[0:2]), elements)

    def _get_full_class_list(
        self,
    ):
        class_list = []
        has_next = True

        while has_next:
            try: 
                next_button = self._internet_util.get_element_with_param_matching_spec('@id', 'contentMain_hlnkNextTop')
            except selenium.common.exceptions.NoSuchElementException:
                next_button = None
                has_next = False

            class_list += self._get_class_list_from_elements(
                self._internet_util.get_elements_with_param_matching_spec('@href', 'content=')
            )

            if has_next:
                next_button.click()
        
        return class_list

    def grab_classes_from_search_url(
        self,
        search_url=None,
    ):
        # open the mf course guide
        search_url = self.default_search_link if search_url is None else search_url
        
        print('opening ')
        if search_url not in self._internet_util.driver.current_url:
            self._internet_util.open_link(search_url)

        if 'show=' in search_url:
            search_url.replace(search_url[search_url.find('show='):].split('&')[0], 'show={}'.format(max_results))

        # add classes that resulted from search, if needed
        if search_url not in self.searches:
            self.searches[search_url] = {}
            self.searches[search_url] = self._get_full_class_list()

        return self.searches[search_url]


    def _get_class_stats(
        self,
        search_url=None,
        art_url='https://art.ai.umich.edu/course/EECS%20281/', # needs to be a restricted URL, to force user to login ;->
        max_timeout=120.,
        max_results=10000,
    ):

        classnames_to_search = self.grab_classes_from_search_url(
            search_url
        )
        
        classnames_to_scrape = [classname for classname in classnames_to_search if classname not in self.class_data]

        if len(classnames_to_scrape > 0):
            self._internet_util.open_link_with_timeout(
                art_url, 
                max_timeout
            )

        for classname in classnames_to_scrape:
            next_element = self._internet_util.driver.find_element_by_id('nav_search')
            next_element.click()
            next_element.send_keys(classname + '\n')
            self.class_data[classname] = self._get_barchart_data_from_open_page()

        return {classname: self.class_data[classname] for classname in self.searches[search_url]}


    def _get_barchart_data_from_open_page(
        self
    ):
        txt_data = self._internet_util.driver.find_element_by_id('barchart').text.split('\n')
        *data, = map(lambda x: 0. if x[0] == '<' else float(x.strip('%')), txt_data[txt_data.index('E') + 1:-1])
        data = np.asarray(data) / 100.
        data[data == 0.] = (1. - sum(data))/len(data[data == 0.])

        return data
