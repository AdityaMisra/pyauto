import unittest

from selenium.common.exceptions import NoSuchElementException

from test_pyauto_settings import *
from test_base import TestBaseAdmin, TestBaseFrontEnd


class TestBannerRandomization(unittest.TestCase, TestBaseAdmin, TestBaseFrontEnd):
    """
    1. open the admin
    2. Go to banner group
    3. select the appropriate slide group
    4. update the orders of the slides
        a) copy the order of the slide group for Bangalore DC-4
        b) copy the caption1 and caption2
    5. Activate the slide group
    6. save the slide group
    7. save the banner group
    8. clear the cache
    9. open the frontend
    10. Go to Bangalore DC-4
    11. Get the image url (or) the captions in the sequence save it to a list
    12. compare the order and the sequence of the captions in the list ---- When order is None sequence should change after couple of refreshes.

    """

    def __init__(self, methodName='runTest'):
        super(TestBannerRandomization, self).__init__(methodName)
        self.admin_url = admin_url_from_settings
        self.redacted_site_url = redacted_site_url_from_settings

    def setUp(self):
        super(TestBannerRandomization, self).setUp()
        self._initialize()

    def test_banner_slide_fixed_position(self):

        self.admin_login()

        banner_type_id = setting_banner_type_id
        slide_group_id = setting_slide_group_id
        # {dc_id: slide_priority}
        dc_id_and_priority_dict = setting_dc_id_and_priority_dict

        banner_dc2_slide_order, caption = \
            self._configuring_slide_priority_for_a_slide_group_and_activating_banner_group(banner_type_id,
                                                                                           slide_group_id,
                                                                                           dc_id_and_priority_dict)
        if not banner_dc2_slide_order or not caption:
            return

        print("Slide_BLR_DC2_priority- {}\n, Selected Slide's Caption- {}\n".format(banner_dc2_slide_order,
                                                                                    caption))

        caption_list = self._test_verify_banner_position_in_frontend()
        caption_list_new_line_string = '\n'.join(caption_list)
        print("Caption Names from front_end - {}".format(caption_list_new_line_string))

        caption_real_position = caption_list.index(caption) + 1
        print("Slide's position in front end - {}".format(caption_real_position))

        try:
            self.assertEqual(int(caption_real_position), int(banner_dc2_slide_order))
            self.print_test_success()
        except AssertionError:
            self.print_test_failure()

    def test_banner_slide_random_position(self):

        self.admin_login()

        banner_type_id = setting_banner_type_id
        slide_group_id = setting_slide_group_id
        # {dc_id: slide_priority}
        dc_id_and_priority_dict = setting_random_dc_id_and_priority_dict

        banner_dc2_slide_order, caption = \
            self._configuring_slide_priority_for_a_slide_group_and_activating_banner_group(banner_type_id,
                                                                                           slide_group_id,
                                                                                           dc_id_and_priority_dict)

        print("Slide_BLR_DC2_priority- {}\n, Selected Slide's Caption- {}\n".format(banner_dc2_slide_order,
                                                                                    caption))

        caption_list = self._test_verify_banner_position_in_frontend()

        caption_list_new_line_string = '\n'.join(caption_list)
        print("First time - Caption Names from front_end - {}".format(caption_list_new_line_string))

        caption_real_position = caption_list.index(caption) + 1
        randomness = False

        # check atleast 10 times before raising the issue ;)
        for idx in xrange(10):
            caption_list = self._test_verify_banner_position_in_frontend()
            caption_real_position_tmp = caption_list.index(caption) + 1

            try:
                self.assertNotEqual(caption_real_position, caption_real_position_tmp)
                self.print_test_success()
                randomness = True
                break
            except AssertionError:
                pass

        self.assertTrue(randomness)

    def _test_verify_banner_position_in_frontend(self):
        caption_list = []

        self.redacted_site_skip_and_explore_to_a_given_city()

        self.redirect_to_cl_page(category_slug='household')

        list_of_banner_captions = self.driver.find_element_by_id('carousel-custom-dots')

        for each_caption_text in list_of_banner_captions.find_elements_by_class_name('owl-dot'):
            # replace the \n with - between caption1 and caption2 and remove extra spaces
            sanitized_caption_text = each_caption_text.text.replace('\n', '-').replace(' ', '')
            caption_list.append(sanitized_caption_text)

        return caption_list

    def _configuring_slide_priority_for_a_slide_group_and_activating_banner_group(self, banner_type_id,
                                                                                  slide_group_id,
                                                                                  dc_id_and_priority_dict):

        # redirect to banner_group of type cl-top-banner
        self.driver.get(self.admin_url + 'saul/bannergroup/?banner_type__id__exact=' + str(banner_type_id))

        # click on household banner group
        self.driver.find_element_by_link_text('Household - cl-top-banner').click()

        # select a slide group
        slide_group_url = self.admin_url + 'saul/slidegroup/' + str(slide_group_id) + '/'

        clicked_on_slide_group = False
        for each_anchor in self.driver.find_elements_by_xpath(".//a"):
            if each_anchor.get_attribute('href') == slide_group_url:
                each_anchor.click()
                clicked_on_slide_group = True
                break

        if not clicked_on_slide_group:
            print('Slide group with id -{} does not exists in the selected banner group'.format(slide_group_id))
        # returns all the li tags for dc
        # driver.find_elements_by_xpath('//form/table/tbody/tr[3]/td[2]/ul/li')

        # Checks the check_box in slide_group and sets a value in text box for a dc
        self._set_slide_order_check_box_and_slide_order_text_box_for_dcs(dc_id_and_priority_dict)

        # verify the slide's priority only for Bangalore DC2
        banner_dc2_slide_order = self.driver.find_element_by_name('dc_102_banner_slide_order').get_attribute('value')

        # Read the captions of the slide group
        caption1 = self.driver.find_element_by_id('caption').get_attribute('value')
        caption2 = self.driver.find_element_by_id('caption2').get_attribute('value')

        caption = '{}-{}'.format(caption1, caption2)
        caption = caption.replace(' ', '')

        # slide group should be active
        self.check_a_check_box_element('id_active')

        # set valid date_to for the slide group
        self._set_appropriate_from_date_and_to_date_for_a_slide_group()

        # save SlideGroup
        self.driver.find_element_by_tag_name('form').submit()

        # read the success or error message
        type_of_message = self.verify_the_error_or_success_message()

        if type_of_message != 'success':
            print('Error Message - SlideGroup save failed.')
            self.assertEqual(type_of_message, 'success')
            return None, None

        # save BannerGroup
        self.driver.find_element_by_tag_name('form').submit()

        self.refresh_composite_cache()

        return banner_dc2_slide_order, caption

    def _set_appropriate_from_date_and_to_date_for_a_slide_group(self):
        import datetime

        date_to = self.driver.find_element_by_id('date_to').get_attribute('value')
        date_to_obj = datetime.datetime.strptime(date_to, '%m/%d/%Y').date()
        today = datetime.datetime.today().date()

        # end date validation
        if today > date_to_obj:
            self.driver.find_element_by_id('date_to').clear()
            self.driver.find_element_by_id('date_to').send_keys(today.strftime('%m/%d/%Y'))

        # from data validation
        date_from = self.driver.find_element_by_id('date_from').get_attribute('value')
        if not date_from:
            self.driver.find_element_by_id('date_to').send_keys(today.strftime('%m/%d/%Y'))

    def _set_slide_order_check_box_and_slide_order_text_box_for_dcs(self, dc_id_and_priority_dict):

        for each_dc_id, slide_priority in dc_id_and_priority_dict.items():
            dc_check_box_id = 'dc_{}'.format(each_dc_id)
            dc_banner_slide_order_text_box_name = 'dc_{}_banner_slide_order'.format(each_dc_id)

            self.check_a_check_box_element(dc_check_box_id)

            self.clear_and_set_a_value_in_a_text_box_using_element_name(dc_banner_slide_order_text_box_name,
                                                                        slide_priority)
