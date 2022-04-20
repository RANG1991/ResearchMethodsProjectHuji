import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep
from collections import defaultdict as dd


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


def repo_name(link):
    x = ''
    for i in range(len(link) - 1, -1, -1):
        if link[i] == '/':
            break
        x += link[i]
    return x[::-1]


def extract_repo(driver, repositories_links, repo_stars, repo):
    reposit = driver.find_elements_by_class_name('v-align-middle')
    stars = driver.find_elements_by_xpath('//*[@id="js-pjax-container"]/div/div'
                                          '[3]/div/ul/li/div[2]/div[2]')
    for i in range(len(reposit)):
        link = reposit[i].get_attribute('href')
        if link is not None:
            repositories_links.append(link)
    for i in range(len(repositories_links)):
        name = repo_name(repositories_links[i])
        repo_stars[name + '-master'] = stars[i].text
    lang = driver.find_elements_by_xpath('//*[@id="js-pjax-container"]/div/div'
                                         '[3]/div/ul/li/div[2]/div[1]')
    for i in range(len(lang)):
        pyt = lang[i].text
        if pyt is not None:
            temp.append(pyt)


def main():
    repo_code = dd(list)
    log_failures_file = open("failure.txt", 'a', encoding='utf-8')
    repo = []
    temp = []
    repo_stars = dd(str)
    options = Options()
    options.add_argument("--disable-notifications")
    username, password, driver_path = read_local_config_file("")
    driver = webdriver.Chrome(driver_path, chrome_options=options)
    login("https://github.com/login", driver, username, password)
    url = 'https://github.com/'
    num_pages = 100
    for z in range(num_pages + 1):
        driver.get(url + 'search?l=Python&o=desc&p=' + str(z) + '&q=Python&s=stars&type=Repositories')
        sleep(3)
        print("Item searched")
        extract_repo(driver)
    for i in range(0, len(repo)):
        repo_code[temp[i]].append(repo[i])
    log_failures_file.close()
    with open('result.json', 'w') as fp:
        json.dump(repo_stars, fp)
