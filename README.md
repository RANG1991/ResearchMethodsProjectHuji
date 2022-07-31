# 	Lambda-expressions in Python: Crawling & Processing

This project crawls the top Python projects from github and analyzes the usages of Lambda expressions among them: 
Statistics, Types of usages and correlations with the repositories meta-data<br/>

The project is composed of 2 components:
  1. **Github Crawler** - Scrapes github top Python projects:<br/> 
      a. Python projects, meaning the projects which Python is the majority programming language of them. 
        the primary language for each GitHub repository is determined according to the largest total size of files with the corresponding extension - in our case .py
        [Reference](https://stackoverflow.com/questions/5318580/how-does-github-figure-out-a-projects-language)  
        In addition, the crawling is performed according the the settings defined in the file: config.json (Minimum of Python percentage, Whether to consider forked repositories, Number of repositories to process etc.)<br/>
        **_Note_:** As default, the Crawler won't scrape a repository which was forked from other repository.<br/>
      b. **Top** projects, meaning projects with highest rank of github-stars.<br/><br/>
   2. **Lambda-expressions Processor** - Produces statistics about the frequency of Lambda-expressions appearance,
                                      The different usages of them and the correlation to the repository's meta-data 
                                      such as size, number of github stars, number of forks, the percentage of Python 
                                      programming language etc.


**Project report**

Please find the paper named "Lambda Functions - Project Report" which contains a review of our Project: 
Background, The Research Question, Methodologies, Results, Discussion and Threats to validity
[Link](https://docs.google.com/document/d/1EvzsI9q-CPdfmiSDcerMIAtsMmOo_xp4CHxX99KSBhY/edit?usp=sharing)  (requires permission)<br/> 

**Configuration**<br/> 
The configuration file influences the settings of the execution, it contains the following adjustable parameters:<br/> 
  *"username"* - Your GitHub email<br/> 
  *"password"* - Your GitHub password<br/> 
  *"driver_p"* - The location (full path) of the chromedriver of selenium (chromedriver.exe)<br/> 
  *"min_python_percentage"* - The minimum required percentage of python language in a repository<br/> 
  *"allow_forked_repos"* - True or False - whether you want to include forked repositories or not<br/> 
  *"number_repositories_to_process"* - The number of repositories you want to process<br/> 
  *"number_pages_to_crawl"* -  The number of GitHub search pages you want to crawl (currently in each page there are 10 repositories)<br/> 

**Github References**

>Previous Work: [https://github.com/muvvasandeep/empirical-lambda-python](https://github.com/muvvasandeep/empirical-lambda-python)

>Selenium github repository: [https://github.com/SeleniumHQ/selenium](https://github.com/SeleniumHQ/selenium)

>Selenium Downloads page: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)


**Installation:**

**Creating and activating a virtual anaconda environment:**
```
Run the following two commands in the anaconda prompt (after installing anaconda):

1. conda create -n <env_name> python=3.8
(wait until the environment will be created successfully)

2. conda activate <env_name>
```

**Python packages requirements**


Detailed in the file: *requirements.txt*<br>
To install the required packages use the following command inside the environment you created:

```
pip install -r <path_to_requirements>
```

**Code Segments** 
```
> github_crawler.py

Logging in to Github using the credentials mentioned in the configuration file. In that file, there are additional 
search parameters which define the repositories for minning 

> lambda_processor.py

Analyzes the usages of Lambda-expressions in the mined repositories. Produces Statistical results

```

**Run the code**
<br>After installing all the requirements using pip and putting your username, password and the correct path of the selenium driver in the config.json file, you can run the script as follows:
```
python github_crawler.py
```

**Demo Recording:**
https://drive.google.com/file/d/1sIXnxwydKS2LCG59CEegkbuSL2_laCZZ/view?usp=sharing
