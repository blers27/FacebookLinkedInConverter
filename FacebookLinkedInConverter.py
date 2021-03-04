from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class FacebookCrawler:
   
    #launch browser and login
    def __init__(self, login, password):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

        self.login(login, password)
		
        self.get_friends()

    def login(self, login, password):
		friends_url = f'https://www.facebook.com/{login}/friends'
        self.driver.get(friends_url)

        # wait for the login page to load
        self.wait.until(EC.visibility_of_element_located((By.ID, "email")))

        # enters email and password, then clicks
        self.driver.find_element_by_id('email').send_keys(login)
        self.driver.find_element_by_id('pass').send_keys(password)
        self.driver.find_element_by_id('loginbutton').click()

    def _get_friends_list(self):
        #finds css selector that contains friend's name
        return self.driver.find_elements_by_css_selector("div > div:nth-child(1) > a[role='link'] > span")

    def get_friends(self):
        # continuous scroll until no more new friends loaded
        num_of_loaded_friends = len(self._get_friends_list())
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                self.wait.until(lambda driver: len(self._get_friends_list()) > num_of_loaded_friends)
                num_of_loaded_friends = len(self._get_friends_list())
            except TimeoutException:
                break  # no more friends loaded

        return [friend.text for friend in self._get_friends_list()]

    #need to filter raw list
    def friend_filter(self):
        self.driver.quit()
        unfiltered = [n for n in self.get_friends() if n]
        nonum = re.compile(r'^[^0-9]')
        #removes elements that "friends" that start with a number
        return [n for n in unfiltered if nonum.match(n)]


class LinkedInLookup:
    login_url = 'https://www.linkedin.com/'

    #launch browser and login
    def __init__(self, login, password):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.login(login, password)

    def login(self, login, password):
        self.driver.get(self.login_url)

        # wait for the login box to load
        self.wait.until(EC.visibility_of_element_located((By.ID, "session_key")))

        # send login and password, then clicks sign in button
        self.driver.find_element_by_id('session_key').send_keys(login)
        self.driver.find_element_by_id('session_password').send_keys(password)
        self.driver.find_element_by_class_name('sign-in-form__submit-button').click()

    #searches friend by using parameter embedded into the URL
    def searchfriend(self, friend):
        #self.driver.find_element_by_class('search-global-typeahead__input always-show-placeholder').send_keys(friend)
        self.driver.execute_script(f"window.open('https://www.linkedin.com/search/results/all/?keywords={friend}')")



if __name__ == '__main__':
    #launches browser, logs in, goes to friend list
    crawler = FacebookCrawler(login='FACEBOOK_EMAIL', password='FACEBOOK_PASSWORD')

    #scrapes your friend list
    friendlist= crawler.friend_filter()

    #goes to Linkedin, signs in, then searches friendlist
    lookup = LinkedInLookup(login='LINKEDIN_EMAIL', password='LINKEDIN_PASSWORD')

	#warning: the code below will open 800 tabs if you have 800 friends.
    for friend in friendlist:
        try:
            lookup.searchfriend(friend)
        except:
            print(f'{friend} failed!')

    #quits browser
    driver.quit()
