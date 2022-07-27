# 	Lambda-expressions in Python: Crawling & Processing

This project crawls Python projects from github and analyze the usages of Lambda expressions among them: 
Statistics, Types of usages and correlations with the repositories meta-data
The project is composed of 2 components:
  1. Github Crawler - Scrapes github top Python projects:<br/> 
      a. **Python** projects, meaning projects which Python is the majority programming language of them. 
        The major language is determined according to the largest total size of files with the 
        corresponding extension - in our case
        [Reference] (https://stackoverflow.com/questions/5318580/how-does-github-figure-out-a-projects-language)  
        The minimum rate of the Python programming language as a part of the project as well as the 
        number of the repositories are configured in file: config.json
        **_Note_:** The Crawler won't scrape a repository which was forked from other repository.<br/>
      b. **Top** projects, meaning projects with highest rank of github-stars.<br/><br/>
   2. Lambda-expressions Processor - Produces statistics about the frequency of Lambda-expressions appearance,
                                      The different usages of them and the correlation to the repository's meta-data 
                                      such as size, number of github stars, number of forks, the percentage of Python 
                                      programming language etc.


**Project report**
```angular2html
Please find the paper named "Lambda Functions - Project Report" which contains a review of our Project: 
Background, The Research Question, Methodologies, Results, Discussion and Threats to validity
[Link (requires permission)] (https://docs.google.com/document/d/1EvzsI9q-CPdfmiSDcerMIAtsMmOo_xp4CHxX99KSBhY/edit?usp=sharing) 

```

**Github References**

>Previous Work: [https://github.com/muvvasandeep/empirical-lambda-python](https://github.com/muvvasandeep/empirical-lambda-python)

>Selenium github repository: [https://github.com/SeleniumHQ/selenium](https://github.com/SeleniumHQ/selenium)


**Installation:**

**Creating and activating a virtual anaconda environment:**
```
Run the following two commands in the anaconda prompt (after installing anaconda):

1. conda create -n <env_name> python=3.7
(wait until the environment will be created successfully)

2. conda activate <env_name>
```

**Python packages requirements**


Detailed in the file: requirements.txt.<br>
To install the required packages use the following command inside the environment you created:

```
pip install -r <path_to_requirements>
```

**Code Segments and Arguments** 
```
> github_crawler.py

Logging in to Github using the credentials mentioned in the configuration file. In that file, there are additional 
search parameters which define the repositories for minning 

> lambda_processor.py

Analyzes the usages of Lambda-expressions in the mined repositories. Produces Statistical results

```

**Run the code**
<br>after installing all the requirements using pip and putting your username, password and the correct path of the selenium driver in the config.json file, you can run the script as follows:
```
python github_crawler.py
```

**Demo Recording:**
https://drive.google.com/file/d/1sIXnxwydKS2LCG59CEegkbuSL2_laCZZ/view?usp=sharing
