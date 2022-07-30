import src
import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import pandas as pd
from subprocess import Popen
import pathlib
import os


def read_local_config_file(filename):
    """
    read the local configuration file containing the credentials and the
    path of the selenium driver
    :param filename: path of the local configuration file
    :return: credentials and path of the selenium driver
    """
    with open(filename, "r") as f:
        json_file = json.load(f)
        username = json_file["username"]
        password = json_file["password"]
        driver_path = json_file["driver_p"]
        python_perc = json_file["requested_python_percentage"]
        allow_forked = json_file["allow_forked_repos"]
        num_repos_to_parse = json_file["number_repositories_to_process"]
        num_pages_to_crawl = json_file["number_pages_to_crawl"]
        return username, password, driver_path, python_perc, allow_forked, num_repos_to_parse, num_pages_to_crawl


def github_login(login_url, driver, username, password):
    """
    login to GitHub using the given credentials
    :param password:
    :param username:
    :param login_url: the URL to log in to
    :param driver: the instance of the selenium driver
    """
    driver.get(login_url)
    print("Opened github")
    sleep(1)
    username_box = driver.find_element(by=By.ID, value='login_field')
    username_box.send_keys(username)
    print("Email Id entered")
    sleep(1)
    password_box = driver.find_element(by=By.ID, value='password')
    password_box.send_keys(password)
    print("Password entered")
    login_box = driver.find_element(by=By.CLASS_NAME, value='btn-block')
    login_box.click()
    sleep(3)


def get_python_lang_percentage(driver):
    perc = driver.find_element(by=By.XPATH,
                               value='//*[contains(@data-ga-click,"Repository, language stats search click, '
                                     'location:repo overview")]//*[text()[contains(.,"Python")]] '
                                     '/following-sibling::span[1]').text
    return perc


def get_forks_props_from_repo(driver):
    """
    provide the number of forks from the repository and whether the repository
    is a fork of another repository
    :param driver: instance of the driver
    :return: number of forks and if it's a fork of another repository
    """
    num_forks = driver.find_element(by=By.XPATH, value='//li//*[text()[contains(.,"Fork")]]').text.replace("Fork ", "")
    is_forked = True
    try:
        driver.find_element(by=By.XPATH, value='//*[text()[contains(.,"forked from")]]')
    except NoSuchElementException:
        is_forked = False
    return num_forks, is_forked


def get_all_repositories_props_in_page(driver):
    """
    given one result page of the search in GitHub, parse the page to
    get all the properties of the repositories in this page:
    1. the repository's URL
    2. the number of start the repository has
    3. the number of forks from the repository
    4. whether this repository is a fork of another one
    :param driver: the instance of the selenium driver
    :return: dictionary with the name of the repository as key and the properties
    as a list of values
    """
    curr_page_repos_props = {}
    repos_elements = driver.find_elements(by=By.XPATH, value='//li[@class="repo-list-item hx_hit-repo d-flex '
                                                             'flex-justify-start py-4 public source"]')
    # Iterates over the result repositories that appear on the current result-page
    for element in repos_elements:
        repo_full_name = element.find_element(by=By.XPATH, value='.//a[@class="v-align-middle"]').text
        repo_link = element.find_element(by=By.XPATH, value='.//a[@class="v-align-middle"]').get_attribute("href")
        repo_num_stars = element.find_element(by=By.XPATH, value='.//a[@class="Link--muted"]').text
        curr_page_repos_props[repo_full_name] = [repo_link, repo_num_stars]
        sleep(1)

    # Extract details from each repository
    for repo_name in curr_page_repos_props.keys():
        repo_link = curr_page_repos_props[repo_name][0]
        driver.get(repo_link)
        num_forks, is_forked = get_forks_props_from_repo(driver)
        perc = get_python_lang_percentage(driver)
        curr_page_repos_props[repo_name].append(num_forks)
        curr_page_repos_props[repo_name].append(is_forked)
        curr_page_repos_props[repo_name].append(perc)
        sleep(1)
    return curr_page_repos_props


def github_crawling(root_path):
    # selenium configuration
    repos_props = {}
    options = Options()
    options.add_argument("--disable-notifications")
    options.headless = True

    # get the credentials from the configuration file
    username, password, driver_path, _, _, _, num_pages_to_crawl = read_local_config_file(f"{root_path}/config.json")
    driver = webdriver.Chrome(driver_path, chrome_options=options)
    github_login("https://github.com/login", driver, username, password)
    main_url = 'https://github.com/'

    # number of results' pages crawl (each page contains 10 repositories)
    try:
        # Iterates over all the result-pages
        for page_index in range(num_pages_to_crawl):
            # this is our query for GitHub's search - python a primary language,
            # the repositories with most stars (path parameters)
            driver.get(main_url + 'search?l=Python&o=desc&p=' + str(page_index + 1) +
                       '&q=Python&s=stars&type=Repositories')
            sleep(3)
            print("Item searched")
            curr_page_repos_props = get_all_repositories_props_in_page(driver)
            repos_props.update(curr_page_repos_props)
    finally:
        # Organizes the data in a dictionary which is exported to a repos_props.csv file
        dict_for_df = {"repo_name": [], "repo_link": [], "repo_number_of_stars": [],
                       "repo_number_of_forks": [], "repo_is_forked": [],
                       "percentage_python_lang": []}
        for key in repos_props.keys():
            dict_for_df["repo_name"].append(key)
            dict_for_df["repo_link"].append(repos_props[key][0])
            dict_for_df["repo_number_of_stars"].append(repos_props[key][1])
            dict_for_df["repo_number_of_forks"].append(repos_props[key][2])
            dict_for_df["repo_is_forked"].append(repos_props[key][3])
            dict_for_df["percentage_python_lang"].append(repos_props[key][4])
        df = pd.DataFrame.from_dict(dict_for_df).set_index("repo_name")
        df.to_csv(f"{root_path}/repos_props.csv")


def create_cloning_script(repos_folder_path, root_path):
    df_repos = pd.read_csv(f"{root_path}/repos_props.csv")
    _, _, _, python_perc, allow_forked, _, _ = read_local_config_file(f"{root_path}/config.json")
    if not allow_forked:
        df_repos = df_repos[df_repos["repo_is_forked"] == False]
    df_repos["percentage_python_lang"] = df_repos["percentage_python_lang"].apply(lambda x: float(x.replace("%", "")))
    if 0 < python_perc <= 100:
        df_repos = df_repos[df_repos["percentage_python_lang"] >= python_perc]
    df_repos_links = df_repos["repo_link"].tolist()
    script_file_path = f"{repos_folder_path}/clone_all_python_repos.bat"
    with open(script_file_path, "w") as f:
        for i in range(len(df_repos_links)):
            f.write("git clone {}\n".format(df_repos_links[i]))


def remove_all_non_python_files(repos_folder_path):
    for path, subdirs, files in os.walk(repos_folder_path):
        for name in files:
            try:
                file_ext = os.path.splitext(os.path.join(path, name))[1]
                if file_ext != ".py":
                    os.remove(os.path.join(path, name))
            except PermissionError as e:
                print(e)


if __name__ == "__main__":
    root_path = pathlib.Path(__file__).parent.parent.resolve()
    github_crawling(root_path)
    repos_folder_path = f"{root_path}/pythonReposForMethods"
    # create the folder for the repositories if it doesn't exist
    pathlib.Path(repos_folder_path).mkdir(exist_ok=True)
    create_cloning_script(repos_folder_path, root_path)
    # run the scripts using subprocess module
    script_file_path = f"{repos_folder_path}/clone_all_python_repos.bat"
    p = Popen([script_file_path], cwd=repos_folder_path)
    stdout, stderr = p.communicate()
    p.wait()
    remove_all_non_python_files(repos_folder_path)
    src.lambda_processor.main()
