from selenium import webdriver

from test_pyauto_settings import *


class TestBase(object):
    def _initialize(self):

        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def _tear_down(self):
        self.driver.close()

    @staticmethod
    def print_test_failure():
        print("*********************************************************************\n" +
              "There is an issue. Don't panic. Please contact the nearest developer.\n" +
              "*********************************************************************\n")

    @staticmethod
    def print_test_success():
        print("*************************\n" +
              "Hurray..!! Test passed :)\n" +
              "*************************\n")

    def check_a_check_box_element(self, element_id):
        if self.driver.find_element_by_id(element_id).get_attribute('checked') != 'true':
            self.driver.find_element_by_id(element_id).click()

    def clear_and_set_a_value_in_a_text_box_using_element_name(self, element_name, value):
        self.driver.find_element_by_name(element_name).clear()
        if value:
            self.driver.find_element_by_name(element_name).send_keys(value)


class TestBaseAdmin(TestBase):
    def __init__(self, admin_url=admin_url_from_settings):
        super(TestBaseAdmin, self).__init__()
        self.admin_url = admin_url

    def admin_login(self, user_name='********', password='********'):
        self.driver.get(self.admin_url)

        # fill in credentials
        user_name_element = self.driver.find_element_by_id('id_username')
        password_element = self.driver.find_element_by_id('id_password')

        user_name_element.send_keys(user_name)
        password_element.send_keys(password)

        self.driver.find_element_by_class_name('submit-row').find_element_by_tag_name('input').click()

    def refresh_composite_cache(self):
        self.driver.get(self.admin_url)

        for each_element in self.driver.find_element_by_id('admin-tools-module').find_elements_by_tag_name('a'):
            if each_element.get_attribute('href') == '{}cache/'.format(admin_url_without_nginx_authentication):
                each_element.click()

        # click on the Refresh composite cache button
        self.driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr/td[3]/form/input[2]').click()

    def verify_the_error_or_success_message(self):
        """
            < ul class ="messagelist" >
                < li class ="error" > Please enter a valid display order < / li >
                < li class ="error" > Error while saving slide group < / li >
            < / ul >

            < ul class ="messagelist" >
                < li class ="success" > Report will be generated and emailed at address: abc@redacted.com </ li >
            < / ul >
        """
        type_of_message = None
        ul_element = self.driver.find_element_by_class_name("messagelist")
        list_of_li_elements = ul_element.find_elements_by_tag_name('li')

        for each_li_element in list_of_li_elements:
            type_of_message = each_li_element.get_attribute('class')
            print("Type of message -{}".format(type_of_message))
            print(each_li_element.text)

        return type_of_message


class TestBaseFrontEnd(TestBase):
    def __init__(self, redacted_site_url=redacted_site_url_from_settings):
        super(TestBaseFrontEnd, self).__init__()
        self.redacted_site_url = redacted_site_url

    def redacted_site_skip_and_explore_to_a_given_city(self, city_name=skip_and_explore_city_name):
        self.driver.get(self.redacted_site_url)
        tmp_city_name = '{},'.format(city_name)
        for each_city_element in self.driver.find_elements_by_xpath('//*[@id="choose-city-form"]/div[2]/div/a'):
            if each_city_element.text == tmp_city_name:
                each_city_element.click()
                break

    def redirect_to_cl_page(self, category_slug):
        """
        To open - https://www.bigbasket.com/cl/household/
        category_slug = "household"

        :param category_slug:
        :return:
        """
        self.driver.get('{}cl/{}/'.format(self.redacted_site_url, category_slug))

    def redirect_to_pc_page(self, slash_separated_categories_slug):
        """
        To open - https://www.redacted.com/pc/branded-foods/jams-spreads/
        slash_separated_categories_slug = "branded-foods/jams-spreads"

        To open - https://www.redacted.com/pc/meat/seafood/canned-seafood/
        slash_separated_categories_slug = "meat/seafood/canned-seafood"

        :param slash_separated_categories_slug:
        :return:
        """
        self.driver.get('{}pc/{}/'.format(self.redacted_site_url, slash_separated_categories_slug))
