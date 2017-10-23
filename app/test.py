import argparse
import concurrent.futures
import json
import glob
import random
import string
import time

import numpy
import splinter

from selenium.webdriver.remote.errorhandler import ElementNotVisibleException


BOTS = 'IA AD IN RI GR RG IR KH'.split()


def random_string(min_length=4, max_length=10):
    return ''.join(
        random.choice(string.ascii_lowercase)
        for _ in range(random.randint(min_length, max_length)))


def random_username():
    return random_string().title()


def random_email_address(username=None):
    if username is None:
        username = random_username()
    return f'{username}@{random_string()}.{random_string(min_length=2, max_length=3)}'


def random_text(fnames, min_length=25):
    fname = random.choice(fnames)
    with open(fname) as infile:
        lines = infile.readlines()
    text = None
    while not text:
        line = random.choice(lines)
        if len(line) >= min_length:
            text = line
    return text.strip()


class Agent:

    def __init__(self, url, datadir='data/novels', driver='chrome', debug=False):
        self.browser = splinter.Browser(driver_name=driver, headless=not debug)
        self.browser.visit(url)
        self.signed_in = False
        self.fnames = glob.glob(datadir + '/*.txt')

    def sign_up(self):
        self.browser.click_link_by_text("registreer")
        username = random_username()
        password = random_string()
        self.browser.fill_form(
            {"username": username, "password": password, "cpassword": password})
        self.browser.click_link_by_id("register-button")
        self.username, self.password = username, password

    def sign_in(self):
        self.browser.fill_form({"username": self.username, "password": self.password})
        self.browser.click_link_by_id("login-button")
        self.signed_in = True

    def sign_out(self):
        if not self.signed_in:
            raise ValueError("Must be signed in to sign out.")
        self.browser.find_link_by_href("logout").click() # TODO FIX
        self.browser.quit()

    @property
    def editor(self):
        return self.browser.find_by_css(".notranslate.public-DraftEditor-content")[0]

    def type_text(self):
        self.editor.type(random_text(self.fnames))

    def generate_text(self):
        self.browser.find_by_text(random.choice(BOTS))[0].click()
        has_refresh_button = self.browser.find_by_id("refresh-button")
        while not has_refresh_button:
            time.sleep(1)
            has_refresh_button = self.browser.find_by_id("refresh-button")

    def clear_text(self):
        self.editor.clear()

    def insert_suggestion(self):
        checks = list(self.browser.find_by_css(".fa.fa-check"))[:3]
        random.choice(checks).click()

    def discard_suggestion(self):
        closes = list(self.browser.find_by_css(".fa.fa-close"))
        random.choice(closes).click()

    def play(self, n_actions=10, sign_out_p=0.01, type_p=0.3, select_p=0.7, discard_p=0.1):
        if not self.signed_in:
            self.sign_up()
            self.sign_in()
        for _ in range(n_actions):
            if random.random() < sign_out_p:
                self.sign_out()
                return True
            if random.random() < type_p:
                self.type_text()
            else:
                self.generate_text()
                if random.random() < select_p:
                    self.insert_suggestion()
                if random.random() < discard_p:
                    self.discard_suggestion()
            time.sleep(random.randint(0, 10))
        return True


def simulate(url, n_agents=5, driver='phantomjs', debug=False):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_agents) as executor:
        for i in range(n_agents):
            executor.submit(Agent(url=url, driver=driver, debug=debug).play)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://localhost:5555')
    parser.add_argument('--agents', type=int, default=5)
    parser.add_argument(
        '--driver', default='phantomjs',
        choices=['chrome', 'firefox', 'phantomjs', 'zope.testbrowser', 'django'])
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    simulate(args.url, n_agents=args.agents, driver=args.driver, debug=args.debug)
