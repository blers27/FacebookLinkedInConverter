#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:56:43 2021

@author: bleron
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd


class ConnectionInfo:
    login_url = 'https://www.linkedin.com/'

    # launch browser and login
    def __init__(self, login, password):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.login(login, password)
        # self.getConnectionInfo()

    def login(self, login, password):
        self.driver.get(self.login_url)

        # wait for the login box to load
        self.wait.until(EC.visibility_of_element_located(
            (By.ID, "session_key")))

        # send login and password, then clicks sign in button
        self.driver.find_element_by_id('session_key').send_keys(login)
        self.driver.find_element_by_id('session_password').send_keys(password)
        self.driver.find_element_by_class_name(
            'sign-in-form__submit-button').click()

    # searches friend by using parameter embedded into the URL
    def getConnectionInfo(self):
        self.driver.get(
            'https://www.linkedin.com/mynetwork/invite-connect/connections/')

        # continuous scroll until no more new connections loaded
        while True:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            sleep(1)
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            sleep(5)

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        names = [name.text.strip() for name in soup.findAll(
            class_='mn-connection-card__name t-16 t-black t-bold')]
        occupations = [occ.text.strip() for occ in soup.findAll(
            class_="mn-connection-card__occupation t-14 t-black--light t-normal")]

        return list(zip(names, occupations))

    def browserQuit(self):
        self.driver.quit()


if __name__ == '__main__':
    login = ConnectionInfo('USERNAME', 'PASSWORD')

    connections = login.getConnectionInfo()

    login.browserQuit()

    df = pd.DataFrame(connections, columns=['Name', 'Occupation'])
    df.to_csv('Connections.csv')
