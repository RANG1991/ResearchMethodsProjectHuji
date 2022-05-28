# 	Lambda-expressions in Python: Crawling & Analysis

This project crawls Python projects from github and analyze the usages of Lambda expressions among them: 
Statistics, Types of usages and correlations with the repositories meta-data
The project is composed of 2 components:
    1) Github Crawler - Scrapes github top Python projects.
                        a) **Python** projects, meaning projects which Python is the majority programming language of them. 
                        The major language is determined according to the largest total size of files with the 
                        corresponding extension - in our case .py
                        [Reference] (https://stackoverflow.com/questions/5318580/how-does-github-figure-out-a-projects-language)
                        The minimum rate of the Python programming language as a part of the project as well as the 
                        number of the repositories are configured in file: config.json
                        **_Note_:** The Crawler won't scrape a repository which was forked from other repository
                        b) **Top** projects, meaning projects with highest rank of github-stars
    2) Lambda-expressions Processor - Produces statistics about the frequency of Lambda-expressions appearance,
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


**Requirements**

Detailed in the file: requirements.txt

For installation-
```
pip install -r <path_to>requirements.txt
```
**Code Segments and Arguments** 
```
> github_crawler.py

Logging in to Github using the credentials mentioned in the configuration file. In that file, there are additional 
search parameters which define the repositories for minning 

> lambda_processor.py

Analyzes the usages of Lambda-expressions in the mined repositories. Produces Statistical results

```

**Activating the virtual env.**
```
//TO-DO: Complete
```

**Run the code**
```
python3 //TO-DO: Complete
```

** Demo Recording:** 
Zoom:
//TO-DO: Add link