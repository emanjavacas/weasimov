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


BOTS = ('Robot Ik', 'I. Nescimov', 'G. Revimov', 'A. Dante', 
        'R. Giphart', 'I. Asimov', 'K. Hembot', 'I. Robhart')


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
        self.url = url
        self.debug = debug
        self.driver = driver
        self.signed_in = False
        self.fnames = glob.glob(datadir + '/*.txt')

    def launch_browser(self):
        self.browser = splinter.Browser(driver_name=self.driver, headless=not self.debug)
        self.browser.visit(self.url)

    def sign_up(self):
        username = random_email_address()
        password = random_string()
        self.browser.fill_form(
            {"username": username, "password": password})
        self.browser.find_by_text("start")[0].click()
        self.username, self.password = username, password
        self.signed_in = True

    def sign_in(self):
        self.browser.fill_form({"username": self.username, "password": self.password})
        self.browser.click_link_by_id("login-button")
        self.signed_in = True

    def sign_out(self):
        if not self.signed_in:
            raise ValueError("Must be signed in to sign out.")
        self.browser.find_link_by_href("logout").click()
        self.browser.quit()

    @property
    def editor(self):
        return self.browser.find_by_css(".notranslate.public-DraftEditor-content")[0]

    def type_text(self):
        self.editor.type(random_text(self.fnames))

    def generate_text(self):
        try:
            self.browser.find_by_text(random.choice(BOTS))[0].click()
        except splinter.exceptions.ElementDoesNotExist:
            return None
        start_time = time.time()
        self.browser.find_by_text("genereer suggesties")[0].click()
        disabled = len(self.browser.find_by_css(".genereer.disabled")) > 0
        while disabled:
            time.sleep(1)
            disabled = len(self.browser.find_by_css(".genereer.disabled")) > 0
        return time.time() - start_time

    def clear_text(self):
        self.editor.clear()

    def insert_suggestion(self):
        checks = list(self.browser.find_by_css(".suggestie"))[:3]
        if checks:
            random.choice(checks).click()

    def play(self, n_actions=10, sign_out_p=0.01, type_p=0.3, select_p=0.7):
        generation_times = []
        if not self.signed_in:
            self.launch_browser()
            self.sign_up()
        for _ in range(n_actions):
            if random.random() < sign_out_p:
                self.sign_out()
                return generation_times
            if random.random() < type_p:
                try:
                    self.type_text()
                except splinter.exceptions.ElementDoesNotExist:
                    continue
            else:
                generation_times.append(self.generate_text())
                if random.random() < select_p:
                    self.insert_suggestion()
            time.sleep(random.randint(0, 10))
        return generation_times


def simulate(url, n_agents=5, driver='phantomjs', datadir='data/novels', debug=False):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_agents) as executor:
        jobs = [executor.submit(Agent(url=url, driver=driver, datadir=datadir, debug=debug).play)
                for i in range(n_agents)]
        generation_times = sum([job.result() for job in concurrent.futures.as_completed(jobs)], [])
    return generation_times


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://localhost:5555')
    parser.add_argument('--agents', type=int, default=5)
    parser.add_argument('--driver', default='phantomjs', choices=['chrome', 'firefox'])
    parser.add_argument('--datadir', default='data/novels')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    generation_times = simulate(args.url, n_agents=args.agents, driver=args.driver, datadir=args.datadir, debug=args.debug)
    with open(f"experiment.a{args.agents}.{time.time()}.txt", 'w') as out:
        for generation_time in generation_times:
            out.write(f'{generation_time}\n')
    
