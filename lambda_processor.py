import re
import concurrent.futures
import glob
import os
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from enum import Enum
from pathlib import Path


NUM_REPOS_TO_PARSE = 600

PATTERNS = Enum('PATTERNS', 'MAP_REDUCE_FILTER_PATTERN FUNC_ARG_PATTERN RET_VALUE_PATTERN ITER_PATTERN UNICODE_PATTERN '
                            'EXCEPTION_PATTERN ASYNC_TASKS_PATTERN ALL_PATTERN CALLBACK_PATTERN '
                            'STRING_FORMATTING_PATTERN '
                            'ERROR_RAISING_PATTERN IN_OPERATOR_PATTERN INNER_LAMBDA_PATTERN '
                            'INDEXING_PATTERN NONE_PATTERN ARITHMETIC_OPERATIONS_PATTERN NONAME_VAR_PATTERN '
                            'BOOL_COND_PATTERN FUNCTION_CALL')

# regular expressions patterns for capturing lambdas' usages
PATTERNS_DICT = {
    PATTERNS.MAP_REDUCE_FILTER_PATTERN: "((map|reduce|filter)(.*?)lambda (.*?):)",
    PATTERNS.FUNC_ARG_PATTERN: "(\\((.*?)=lambda (.*?):(.*?)\\))",
    PATTERNS.RET_VALUE_PATTERN: "(return lambda (.*?):)",
    PATTERNS.ITER_PATTERN: "(lambda (.*?):(.*?)(list|tuple|string|dict))",
    PATTERNS.UNICODE_PATTERN: "(lambda (.*?):(.*?).encode)",
    PATTERNS.EXCEPTION_PATTERN: "(lambda (.*?): future.set_exception)",
    PATTERNS.ASYNC_TASKS_PATTERN: "(lambda (.*?):(.*?)async)",
    PATTERNS.ALL_PATTERN: "(lambda (.*?):)",
    PATTERNS.CALLBACK_PATTERN: r"([c|C]allback(.*?)lambda)",
    PATTERNS.STRING_FORMATTING_PATTERN: "(lambda([^\\(#\\,\\=\\[\\)]*?)str\\()",
    PATTERNS.ERROR_RAISING_PATTERN: "(lambda([^#\\(\\)\\.\\_\\,]*?)error)",
    PATTERNS.IN_OPERATOR_PATTERN: "(lambda\\s(\\w+):\\s+(in|isin)\\s)",
    PATTERNS.INNER_LAMBDA_PATTERN: "(lambda(.*?):(.*?)in lambda(.*?):)",
    PATTERNS.INDEXING_PATTERN: "(lambda\\s(\\w+):\\s?\\[)",
    PATTERNS.NONE_PATTERN: "(lambda(.*?):\\s?None)",
    PATTERNS.ARITHMETIC_OPERATIONS_PATTERN: "((.*?)lambda\\s(\\w+):([^\\(\'\"#\\)]*?)(\\w?)[\\+|\\/|\\*|\\-](\\w?))",
    PATTERNS.NONAME_VAR_PATTERN: "(lambda [\\*\\_]?_:)",
    PATTERNS.BOOL_COND_PATTERN: "(lambda\\s(\\w+):(\\s?(True|False)|([^\\(,\\)#]*?)(<|==|!=|>|<=|=<|=>|>=)))",
    PATTERNS.FUNCTION_CALL: r"(lambda\s*?(\w+)\s?\,?\s?(\w+)*?:(\s*?\w*?)[\(])"
}


def process_lambda_exp_single_file(python_filename):
    """
    count the number of lambda expressions occurrences and usages in a single python file
    :param python_filename: the path to the python file to be processed
    :return: dict_types - a dictionary containing the types of the lambda expressions
    as keys and their counts as values in this single file
    num_lambdas_in_file - the total number of the lambda expressions in this file
    num_of_code_lines - the number of lines of code in this file
    """
    print(f"processing file: {python_filename}")
    with open(python_filename, "r", encoding="utf-8") as f:
        python_file_text = f.read()
        num_lambda_in_file = len([x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.ALL_PATTERN], python_file_text)])
        dict_types = {}
        if num_lambda_in_file > 0:
            dict_types = count_usages_of_lambda_expressions(python_file_text)
        num_of_code_lines = calc_number_of_code_line_python_file(python_file_text)
        return dict_types, num_lambda_in_file, num_of_code_lines


def count_usages_of_lambda_expressions(python_file_text):
    """
    count the number of the usages of lambda expressions in a single python file
    :param python_file_text: the python file as string (text)
    :return: dict_types_to_counts - a dictionary containing the type of each lambda expression as key,
    and it's number in this python file as value
    """
    map_filter_reduce_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.MAP_REDUCE_FILTER_PATTERN],
                                                           python_file_text)]
    function_arguments_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.FUNC_ARG_PATTERN], python_file_text)]
    return_value_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.RET_VALUE_PATTERN], python_file_text)]
    unicode_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.UNICODE_PATTERN], python_file_text)]
    exception_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.EXCEPTION_PATTERN], python_file_text)]
    async_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.ASYNC_TASKS_PATTERN], python_file_text)]
    iterators_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.ITER_PATTERN], python_file_text)]
    callbacks_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.CALLBACK_PATTERN], python_file_text)]
    string_formatting_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.STRING_FORMATTING_PATTERN],
                                                           python_file_text)]
    error_raising_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.ERROR_RAISING_PATTERN], python_file_text)]
    in_operator_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.IN_OPERATOR_PATTERN], python_file_text)]
    indexing_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.INDEXING_PATTERN], python_file_text)]
    none_pattern_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.NONE_PATTERN], python_file_text)]
    arithmetic_operators_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.ARITHMETIC_OPERATIONS_PATTERN],
                                                              python_file_text)]
    noname_vars_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.NONAME_VAR_PATTERN], python_file_text)]
    boolean_conditions_find_all = [x[0] for x in re.findall(PATTERNS_DICT[PATTERNS.BOOL_COND_PATTERN], python_file_text)]
    dict_types_to_find_all_res = {
        "Map Reduce Filter": map_filter_reduce_find_all,
        "Function Arguments": function_arguments_find_all,
        "Return Statements": return_value_find_all,
        "Unicode Encoding Functions": unicode_find_all,
        "Exception handling": exception_find_all,
        "Asynchronous Functions": async_find_all,
        "Iterator": iterators_find_all,
        "Callbacks": callbacks_find_all,
        "String Formatting": string_formatting_find_all,
        "Error Raising": error_raising_find_all,
        "In Operator": in_operator_find_all,
        "Indexing": indexing_find_all,
        "Initializing Default Values": none_pattern_find_all,
        "Algebraic Operations": arithmetic_operators_find_all,
        "No Name Variables": noname_vars_find_all,
        "Boolean Conditions": boolean_conditions_find_all
    }
    dict_types_to_counts = {k: len(v) for k, v in dict_types_to_find_all_res.items()}
    return dict_types_to_counts


def calc_average_num_lambda_per_file(all_files_dict_types):
    """
    calculates the average number of lambda usages in a single file over all the repositories
    :param all_files_dict_types: a dictionary containing the following:
    key = (file_name, repository_name)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambdas in this python file)
    :return: average number of lambdas in a single file
    """
    lambda_count = 0
    for key in all_files_dict_types.keys():
        # the second element of each value is the number of lambdas in a single python file
        lambda_count += all_files_dict_types[key][1]
    # calculate the average over the number of all files (across all the repositories)
    return lambda_count / len(all_files_dict_types)


def calc_average_num_lambdas_per_repository(all_files_dict_types):
    """
    calculates the average number of lambda usages in a repository
    :param all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambdas in this python file)
    :return: average number of lambda usages in a repository and the total number of lambdas in all the
    repositories together
    """
    total_number_of_lambdas = 0
    list_of_repositories = []
    for filename, repo_name, repo_path in all_files_dict_types.keys():
        num_lambdas_in_file = all_files_dict_types[(filename, repo_name, repo_path)][1]
        total_number_of_lambdas += num_lambdas_in_file
        if repo_name not in list_of_repositories:
            list_of_repositories.append(repo_name)
    return total_number_of_lambdas / len(list_of_repositories), total_number_of_lambdas


def get_repository_dir_name(path, start_loc_path, end_loc_path):
    """
    get the repository name (directory name) based on the full path of a python file inside it
    :param start_loc_path: the start index of the repository name in the path
    :param end_loc_path: the end index of the repository name in the path
    :param path: full path of a python file
    :return: the directory (repository) name
    """
    path = os.path.normpath(path)
    split_path = path.split(os.sep)
    # add 1 to get the full name
    return "/".join(split_path[start_loc_path: end_loc_path + 1])


def calc_number_of_code_line_python_file(python_file_text):
    """
    calculate the number of code lines (non-empty and non comment lines) in a single python file
    :param python_file_text: the python file as string (text)
    :return: the number of lines of code in this python file
    """
    lines_of_code = re.findall(r"[^#](.+?)\n", python_file_text)
    return len(lines_of_code)


def calc_ratio_num_lambdas_repo_size(all_files_dict_types):
    """
    calculate ratio between the number of lambdas to the number of code lines in a repository
    :param all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    :return: dict_num_lambdas_num_code_lines_per_repo
    """
    dict_num_lambdas_num_code_lines_per_repo = {}
    # make a dictionary with the number of lambdas and the number of lines of code in each repository
    for filename, repository_name, repository_path in all_files_dict_types.keys():
        # if the repository name is not in the keys of the dictionary - add it with a count of zero
        if (repository_name, repository_path) not in dict_num_lambdas_num_code_lines_per_repo.keys():
            dict_num_lambdas_num_code_lines_per_repo[(repository_name, repository_path)] = [0.0, 0.0]
        # the second element of the value is the number of lambdas in a specific python file
        number_of_lambdas_in_file = all_files_dict_types[(filename, repository_name, repository_path)][1]
        # the third element of the value is the number of lines of code in a specific python file
        num_of_code_lines_in_file = all_files_dict_types[(filename, repository_name, repository_path)][2]
        dict_num_lambdas_num_code_lines_per_repo[(repository_name, repository_path)][0] += number_of_lambdas_in_file
        dict_num_lambdas_num_code_lines_per_repo[(repository_name, repository_path)][1] += num_of_code_lines_in_file
    return dict_num_lambdas_num_code_lines_per_repo


def calc_correlation_between_repos_props_and_lambda_exp(df_repos_props,
                                                        dict_num_lambdas_num_code_lines_per_repo):
    """
    calculate correlation measurements with respect to the lambdas number in each repository
    :param dict_num_lambdas_num_code_lines_per_repo: dictionary containing the following:
    key = (repository name)
    value = (ratio of the number of lambdas and the repository size, size of the repository in bytes)
    :param df_repos_props: the data frame containing all the repositories properties extracted from the GitHub
    crawling
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    """
    # extract from the repository path in the data frame only the repository name
    df_repos_props["repo_name"] = df_repos_props["repo_name"].apply(func=get_repository_dir_name, args=(1, 1))
    # remove the percentage sign and remain only with the number as float
    df_repos_props["percentage_python_lang"] = df_repos_props["percentage_python_lang"].apply(lambda x:
                                                                                              float(x.replace("%", "")))
    # if the letter 'k' exists (the number is in thousands), replace it with '000' and remove the decimal point
    df_repos_props["repo_number_of_stars"] = df_repos_props["repo_number_of_stars"].apply(lambda x:
                                                                                          float(x.replace(".", "")
                                                                                                .replace("k", "000")
                                                                                                if "k" in x else x))
    # if the letter 'k' exists (the number is in thousands), replace it with '000' and remove the decimal point
    df_repos_props["repo_number_of_forks"] = df_repos_props["repo_number_of_forks"].apply(lambda x:
                                                                                          float(x.replace(".", "")
                                                                                                .replace("k", "000")
                                                                                                if "k" in x else x))
    dict_lambda_count_per_repo_to_df = {"number_of_code_lines_in_repo": [], "lambdas_number": [], "repo_name": []}
    for repository_name, repository_path in dict_num_lambdas_num_code_lines_per_repo.keys():
        dict_lambda_count_per_repo_to_df["repo_name"].append(repository_name)
        num_lambdas_in_repository = int(dict_num_lambdas_num_code_lines_per_repo[(repository_name, repository_path)][0])
        num_lines_of_code_in_repository = int(
            dict_num_lambdas_num_code_lines_per_repo[(repository_name, repository_path)][1])
        dict_lambda_count_per_repo_to_df["lambdas_number"].append(num_lambdas_in_repository if
                                                                  num_lambdas_in_repository > 0 else 0)
        dict_lambda_count_per_repo_to_df["number_of_code_lines_in_repo"].append(num_lines_of_code_in_repository)
    df_lambdas = pd.DataFrame.from_dict(dict_lambda_count_per_repo_to_df)
    df_repos_props = df_repos_props.sort_values(by=["repo_name"])
    df_lambdas = df_lambdas.sort_values(by=["repo_name"])
    df_repos_props["repo_name"] = df_repos_props["repo_name"].apply(lambda x: x.lower())
    df_lambdas["repo_name"] = df_lambdas["repo_name"].apply(lambda x: x.lower())
    df_repos_props = df_repos_props.merge(df_lambdas, on="repo_name")
    df_repos_props.to_csv("df_repo_props_with_lambda_stat.csv")
    df_repos_props = df_repos_props.rename(columns={"repo_number_of_stars": "#Stars of repo",
                                                    "lambdas_number": "#lambdas",
                                                    "repo_number_of_forks": "#Forks of repo",
                                                    "percentage_python_lang": "Python percent",
                                                    "number_of_code_lines_in_repo": "# Code lines"})
    # number of stars
    print("the correlation between the number of stars and the number of lambdas is:\n"
          "{}".format(
        df_repos_props[["#Stars of repo", "#lambdas"]].corr()))
    df_repos_props[["#Stars of repo", "#lambdas"]].plot.scatter(
        x="#lambdas", y="#Stars of repo")
    plt.tight_layout()
    plt.savefig("./plots/stars_lambdas.png")
    # number of forks
    print("the correlation between the number of forks and the number of lambdas is:\n"
          "{}".format(
        df_repos_props[["#Forks of repo", "#lambdas"]].corr()))
    df_repos_props[["#Forks of repo", "#lambdas"]].plot.scatter(
        x="#lambdas", y="#Forks of repo")
    plt.tight_layout()
    plt.savefig("./plots/forks_lambdas.png")
    # percentage of python programming language
    print("the correlation between the Python percent and the number of lambdas is:\n"
          "{}".format(
        df_repos_props[["Python percent", "#lambdas"]].corr()))
    df_repos_props[["Python percent", "#lambdas"]].plot.scatter(
        x="#lambdas", y="Python percent")
    plt.tight_layout()
    plt.savefig("./plots/python_perc_lambdas.png")
    # number of lines of code
    print("the correlation between the ratio of the repository size and the number of lambdas is:\n"
          "{}".format(
        df_repos_props[["# Code lines", "#lambdas"]].corr()))
    df_repos_props[["# Code lines", "#lambdas"]].plot.scatter(
        x="#lambdas", y="# Code lines")
    plt.tight_layout()
    plt.savefig("./plots/code_lines_lambdas.png")
    plt.clf()


def plot_bar_plots_lambdas_types(all_files_dict_types):
    """
    :param all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    """
    dict_types_accumulated_sum = {}
    for filename, repository_name, repository_path in all_files_dict_types.keys():
        dict_types, num_lambdas_in_file, num_lines_of_code = all_files_dict_types[
            (filename, repository_name, repository_path)]
        for type_name in dict_types.keys():
            if type_name not in dict_types_accumulated_sum.keys():
                dict_types_accumulated_sum[type_name] = 0
            dict_types_accumulated_sum[type_name] += dict_types[type_name]
    plt.bar(range(len(dict_types_accumulated_sum)), list(dict_types_accumulated_sum.values()), align='center')
    plt.yticks(np.arange(min(dict_types_accumulated_sum.values()), max(dict_types_accumulated_sum.values()) + 1,
                         100),
               rotation=45)
    plt.xticks(range(len(dict_types_accumulated_sum)), list(dict_types_accumulated_sum.keys()), rotation=80,
               fontsize=9)
    plt.tight_layout()
    plt.savefig("./plots/bar_plot.png")
    plt.clf()


def plot_CDF_number_of_lambdas_ratio(ratio_lambdas_repo_size):
    num_lambdas_ratio_list = []
    for repository_name in ratio_lambdas_repo_size.keys():
        num_lambdas_in_repo = ratio_lambdas_repo_size[repository_name][0]
        num_lines_of_code_in_repo = ratio_lambdas_repo_size[repository_name][1]
        if num_lines_of_code_in_repo == 0:
            num_lambdas_ratio_list.append(0.0)
        else:
            num_lambdas_ratio_list.append(num_lambdas_in_repo / num_lines_of_code_in_repo)
    lambdas_ratio_np = np.array(num_lambdas_ratio_list)
    values, base = np.histogram(lambdas_ratio_np, bins=1000)
    # evaluate the cumulative
    cumulative = np.cumsum(values)
    cumulative = (cumulative - np.min(cumulative)) / np.max(cumulative)
    # plot the cumulative function
    plt.plot(base[:-1], cumulative, c='blue')
    plt.xlabel('Lambdas / Repo code lines')
    plt.grid()
    plt.savefig("./plots/CDF.png")


def count_number_of_repos_containing_lambdas(all_files_dict_types):
    """
    count the number of repositories containing lambda expressions
    :param all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    :return: the number of repositories containing lambda expressions
    """
    list_repos_containing_lambdas = []
    for filename, repository_name, repository_path in all_files_dict_types:
        dict_types, num_lambda_in_file, num_of_code_lines = all_files_dict_types[
            (filename, repository_name, repository_path)]
        if repository_name not in list_repos_containing_lambdas:
            if num_lambda_in_file > 0:
                list_repos_containing_lambdas.append(repository_name)
    return len(list_repos_containing_lambdas)


def count_maximum_number_of_lambdas_per_file(all_files_dict_types):
    max_num_lambdas = 0
    name_of_file_with_max = ""
    for filename, repository_name, repository_path in all_files_dict_types:
        dict_types, num_lambda_in_file, num_of_code_lines = all_files_dict_types[
            (filename, repository_name, repository_path)]
        if max_num_lambdas < num_lambda_in_file:
            max_num_lambdas = num_lambda_in_file
            name_of_file_with_max = filename
    print(name_of_file_with_max)
    return max_num_lambdas


def calc_ratio_total_lambdas_total_lines_of_code(all_files_dict_types):
    num_total_lambdas = 0
    num_total_lines_of_code = 0
    for filename, repository_name, repository_path in all_files_dict_types:
        dict_types, num_lambda_in_file, num_of_code_lines = all_files_dict_types[
            (filename, repository_name, repository_path)]
        num_total_lambdas += num_lambda_in_file
        num_total_lines_of_code += num_of_code_lines
    return num_total_lambdas / num_total_lines_of_code


def process_all_python_files_in_parallel(repos_parent_folder):
    """
    process all the python files in all the repositories in parallel to get the number of lambdas in each
    python file. save the results into dictionary.
    :param repos_parent_folder: the parent folder of all the repositories downloaded after the scraping
    :return: all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    """
    all_files_dict_types = {}
    # get all the python files from all the repositories
    repos_folders = [folder for folder in glob.glob(r'{}/*'.format(repos_parent_folder))]
    repos_folders = repos_folders[:NUM_REPOS_TO_PARSE]
    files = [(filename, get_repository_dir_name(filename, 1, 1), get_repository_dir_name(filename, 0, 1))
             for repo_folder in repos_folders
             for filename in glob.glob(r'{}/**/*.py'.format(repo_folder))]
    lambdas_counts_in_files = 0
    # initialize a thread pool to do the calculation of the lambda statistics in each of the python
    # files in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        # construct a dictionary of future to filename and repository name
        future_to_filename = \
            {
                executor.submit(process_lambda_exp_single_file, filename):
                    (filename, repository_name, repository_path) for filename, repository_name, repository_path in files
            }
        # for each of the futures, check if it finished and then take
        # the dictionary of lambdas statistics and merge it into the large dictionary
        for future in concurrent.futures.as_completed(future_to_filename):
            filename, repository_name, repository_path = future_to_filename[future]
            try:
                dict_types, num_lambda_in_file, num_of_code_lines = future.result()
                all_files_dict_types[(filename, repository_name, repository_path)] = (dict_types, num_lambda_in_file,
                                                                                      num_of_code_lines)
            except Exception as exc:
                print('%r generated an exception: %s' % (filename, exc))
        # terminate all the futures and shutdown the thread pool
        for future in future_to_filename:
            future.cancel()
        executor.shutdown()
    return all_files_dict_types


def main():
    # create the folder of the plots if it doesn't exist
    Path("./plots").mkdir(exist_ok=True)
    # read the containing the metadata of each repository
    df_repos_props = pd.read_csv("./repos_props.csv")
    # process all the .py files in each repository
    all_files_dict_types = process_all_python_files_in_parallel("./pythonReposForMethods")
    num_of_repos_containing_lambdas = count_number_of_repos_containing_lambdas(all_files_dict_types)
    max_num_lambdas_in_file = count_maximum_number_of_lambdas_per_file(all_files_dict_types)
    dict_num_lambdas_num_code_lines_per_repo = calc_ratio_num_lambdas_repo_size(all_files_dict_types)
    calc_correlation_between_repos_props_and_lambda_exp(df_repos_props, dict_num_lambdas_num_code_lines_per_repo)
    avg_num_lambda_per_file = calc_average_num_lambda_per_file(all_files_dict_types)
    avg_num_lambda_per_repository, total_num_lambda_per_repository = calc_average_num_lambdas_per_repository(
        all_files_dict_types)
    ration_total_lambdas_total_code_lines = calc_ratio_total_lambdas_total_lines_of_code(all_files_dict_types)
    print("the average number of lambdas per file: {}".format(avg_num_lambda_per_file))
    print("the average number of lambdas per repository: {}".format(avg_num_lambda_per_repository))
    print("the ratio of lambdas and the repository size: {}".format(dict_num_lambdas_num_code_lines_per_repo))
    print("the number of repositories containing lambda is: {}".format(num_of_repos_containing_lambdas))
    print("the maximum number lambdas in a single file is: {}".format(max_num_lambdas_in_file))
    print("the total number of lambdas in all the repositories: {}".format(total_num_lambda_per_repository))
    print("the ration between the number of lambdas and the number of code lines is: {}".format(
        ration_total_lambdas_total_code_lines))
    plot_bar_plots_lambdas_types(all_files_dict_types)
    plot_CDF_number_of_lambdas_ratio(dict_num_lambdas_num_code_lines_per_repo)


if __name__ == '__main__':
    main()
