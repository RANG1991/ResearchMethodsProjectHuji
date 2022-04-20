import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pandas as pd


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


def get_forks_props_from_repo(driver, repo_link):
    driver.get(repo_link)
    num_forks = driver.find_element_by_xpath('//li//*[text()[contains(.,"Fork")]]').text.replace("Fork ", "")
    is_forked = True
    try:
        driver.find_element_by_xpath('//*[text()[contains(.,"forked from")]]')
    except NoSuchElementException:
        is_forked = False
    return num_forks, is_forked


def get_all_repositories_props_in_page(driver):
    curr_page_repos_props = {}
    repos_elements = driver.find_elements_by_xpath('//li[@class="repo-list-item hx_hit-repo d-flex '
                                                   'flex-justify-start py-4 public source"]')
    for element in repos_elements:
        repo_full_name = element.find_element_by_xpath('.//a[@class="v-align-middle"]').text
        repo_link = element.find_element_by_xpath('.//a[@class="v-align-middle"]').get_attribute("href")
        repo_num_stars = element.find_element_by_xpath('.//a[@class="Link--muted"]').text
        curr_page_repos_props[repo_full_name] = [repo_link, repo_num_stars]
        sleep(1)
    for repo_name in curr_page_repos_props.keys():
        repo_link = curr_page_repos_props[repo_name][0]
        num_forks, is_forked = get_forks_props_from_repo(driver, repo_link)
        curr_page_repos_props[repo_name].append(num_forks)
        curr_page_repos_props[repo_name].append(is_forked)
        sleep(1)
    return curr_page_repos_props


def main():
    repos_props = {}
    options = Options()
    options.add_argument("--disable-notifications")
    options.headless = True
    username, password, driver_path = read_local_config_file("./config.json")
    driver = webdriver.Chrome(driver_path, chrome_options=options)
    login("https://github.com/login", driver, username, password)
    main_url = 'https://github.com/'
    num_pages = 100
    try:
        for page_index in range(num_pages):
            driver.get(main_url + 'search?l=Python&o=desc&p=' + str(page_index + 1) +
                       '&q=Python&s=stars&type=Repositories')
            sleep(3)
            print("Item searched")
            curr_page_repos_props = get_all_repositories_props_in_page(driver)
            repos_props.update(curr_page_repos_props)
    finally:
        dict_for_df = {"repo_name": [], "repo_link": [], "repo_number_of_stars": [],
                       "repo_number_of_forks": [], "repo_is_forked": []}
        for key in repos_props.keys():
            dict_for_df["repo_name"].append(key)
            dict_for_df["repo_link"].append(repos_props[key][0])
            dict_for_df["repo_number_of_stars"].append(repos_props[key][1])
            dict_for_df["repo_number_of_forks"].append(repos_props[key][2])
            dict_for_df["repo_is_forked"].append(repos_props[key][3])
        df = pd.DataFrame.from_dict(dict_for_df).set_index("repo_name")
        df.to_csv("repos_props.csv")


if __name__ == "__main__":
    main()
