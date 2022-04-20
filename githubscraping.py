import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep


def read_local_config_file(filename):
    with open(filename, "r") as f:
        json_file = json.load(f)
        username = json_file["username"]
        password = json_file["password"]
        driver_path = json_file["driver_p"]
        return username, password, driver_path


def login(login_url, driver, username, password):
    driver.get(login_url)
    print("Opened github")
    sleep(1)
    username_box = driver.find_element_by_id('login_field')
    username_box.send_keys(username)
    print("Email Id entered")
    sleep(1)
    password_box = driver.find_element_by_id('password')
    password_box.send_keys(password)
    print("Password entered")
    login_box = driver.find_element_by_class_name('btn-block')
    login_box.click()
    sleep(3)


def get_repository_props(repository_name):


def get_all_repositories_props_in_page(driver):


def main():
    repos_props = {}
    options = Options()
    options.add_argument("--disable-notifications")
    username, password, driver_path = read_local_config_file("./config.json")
    driver = webdriver.Chrome(driver_path, chrome_options=options)
    login("https://github.com/login", driver, username, password)
    main_url = 'https://github.com/'
    num_pages = 100
    for page_index in range(num_pages + 1):
        driver.get(main_url + 'search?l=Python&o=desc&p=' + str(page_index) + '&q=Python&s=stars&type=Repositories')
        sleep(3)
        print("Item searched")
        get_all_repositories_props_in_page(driver)
