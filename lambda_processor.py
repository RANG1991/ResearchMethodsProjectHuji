import re
import concurrent.futures
import glob
import os
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

# regular expressions for lambda usages patterns
MAP_REDUCE_FILTER_PATTERN = r"((map|reduce|filter)(.*?)lambda (.*?):)"
FUNC_ARG_PATTERN = r"(\((.*?)=lambda (.*?):(.*?)\))"
RET_VALUE_PATTERN = r"(return lambda (.*?):)"
ITER_PATTERN = r"(lambda (.*?):(.*?)(list|tuple|string|dict))"
UNICODE_PATTERN = r"(lambda (.*?):(.*?).encode)"
EXCEPTION_PATTERN = r"(lambda (.*?): future.set_exception)"
ASYNC_TASKS_PATTERN = r"(lambda (.*?):(.*?)async)"


def process_lambda_exp_single_file(python_filename):
    """
    count the lambda expressions' number of appearances and usages in a single python file
    :param python_filename: the path of the python file to be processed
    :return: dict_types - a dictionary containing the types of the lambda expressions
    as keys and their counts as values
    num_lambdas_in_file - the total number of the lambda expressions in this file
    """
    with open(python_filename, "r", encoding="utf-8") as f:
        python_file_text = f.read()
        num_lambda_in_file = len(re.findall(r"lambda (.*?):", python_file_text))
        dict_types = {}
        if num_lambda_in_file > 0:
            dict_types = count_usages_of_lambda_expressions(python_file_text)
        num_of_code_lines = calc_number_of_code_line_python_file(python_file_text)
        return dict_types, num_lambda_in_file, num_of_code_lines


def count_usages_of_lambda_expressions(python_file_text):
    """
    count the number of the various usages of lambda expressions in a single python file
    :param python_file_text: the python file as string (text)
    :return: dict_type - a dictionary containing the type of each lambda expression as key and its number in this
    python file as value
    """
    dict_types = {"map_reduce_filter": len(re.findall(MAP_REDUCE_FILTER_PATTERN, python_file_text)),
                  "func_arg": len(re.findall(FUNC_ARG_PATTERN, python_file_text)),
                  "ret_value": len(re.findall(RET_VALUE_PATTERN, python_file_text)),
                  "unicode": len(re.findall(UNICODE_PATTERN, python_file_text)),
                  "exception": len(re.findall(EXCEPTION_PATTERN, python_file_text)),
                  "async": len(re.findall(ASYNC_TASKS_PATTERN, python_file_text)),
                  "iterators": len(re.findall(ITER_PATTERN, python_file_text))}
    # if dict_types["map_reduce_filter"] > 0:
    #     print("\n".join([finding[0] for finding in re.findall(MAP_REDUCE_FILTER_PATTERN, python_file_text)]))
    return dict_types


def calc_average_num_lambda_per_file(all_files_dict_types):
    """
    calculates the average number of lambda usages in a single file file over all the repositories
    :param all_files_dict_types: a dictionary containing the following:
    key = (file_name, repository_name)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    :return: average number of lambda usages in a single file
    """
    lambda_count = 0
    for key in all_files_dict_types.keys():
        # the second element of each value is the number of lambdas in a specific python file
        lambda_count += all_files_dict_types[key][1]
    return lambda_count / len(all_files_dict_types)


def calc_average_num_lambdas_per_repository(all_files_dict_types):
    """
    calculates the average number of lambda usages in a repository
    :param all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    :return: average number of lambda usages in a repository
    """
    dict_lambda_count_per_repo = {}
    for filename, repo_name, repo_path in all_files_dict_types.keys():
        # if the repository name is not a key - add it with a count of zero
        if repo_name not in dict_lambda_count_per_repo.keys():
            dict_lambda_count_per_repo[repo_name] = 0
        num_lambdas_in_file = all_files_dict_types[(filename, repo_name, repo_path)][1]
        dict_lambda_count_per_repo[repo_name] += num_lambdas_in_file
        # divide the number of lambdas in each repository by the total number of repositories
    for repo_name in dict_lambda_count_per_repo.keys():
        dict_lambda_count_per_repo[repo_name] /= len(dict_lambda_count_per_repo)
    return dict_lambda_count_per_repo


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
    lines_of_code = re.findall(r"^[^#](.+?)\n", python_file_text)
    return len(lines_of_code)


def calc_ratio_num_lambdas_repo_size(all_files_dict_types):
    """
    calculate the lambdas ratio to the repository size in bytes
    :param all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    :return: dict_lambdas_size_ratio_per_repo
    """
    dict_number_of_lambdas_per_repo = {}
    # make a dictionary with the number of lambdas in each repository
    for filename, repository_name, repository_path in all_files_dict_types.keys():
        # if the repository name is not in the keys of the dictionary - add it with a count of zero
        if (repository_name, repository_path) not in dict_number_of_lambdas_per_repo.keys():
            dict_number_of_lambdas_per_repo[(repository_name, repository_path)] = [0.0, 0.0]
            # the second element of the value is the number of lambdas in a specific python file
        number_of_lambdas_in_file = all_files_dict_types[(filename, repository_name, repository_path)][1]
        num_of_code_lines = all_files_dict_types[(filename, repository_name, repository_path)][1]
        dict_number_of_lambdas_per_repo[(repository_name, repository_path)][0] += number_of_lambdas_in_file
        dict_number_of_lambdas_per_repo[(repository_name, repository_path)][1] += num_of_code_lines
    dict_lambdas_size_ratio_per_repo = {}
    for repository_name, repository_path in dict_number_of_lambdas_per_repo.keys():
        number_of_lambdas_in_file, num_of_code_lines = dict_number_of_lambdas_per_repo[(repository_name, repository_path)]
        if num_of_code_lines == 0:
            dict_lambdas_size_ratio_per_repo[repository_name] = 0.0
        else:
            dict_lambdas_size_ratio_per_repo[repository_name] = number_of_lambdas_in_file / num_of_code_lines
    return dict_lambdas_size_ratio_per_repo


def check_correlation_between_repos_props_and_lambda_exp(df_repos_props, all_files_dict_types,
                                                         dict_ratio_lambdas_repo_size):
    """
    calculate correlation measurements with respect to the lambdas number in each repository
    :param dict_ratio_lambdas_repo_size: dictionary containing the following:
    key = (repository name)
    value = (ratio of the number of lambdas and the repository size, size of the repository in bytes)
    :param df_repos_props: the data frame containing all the repositories properties extracted from the github
    crawling
    :param all_files_dict_types: a dictionary containing the following:
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
    dict_lambda_count_per_repo = {}
    for filename, repository_name, repository_path in all_files_dict_types.keys():
        # if the repository name is not in the keys of the dictionary - add it with a count of zero
        if repository_name not in dict_lambda_count_per_repo.keys():
            dict_lambda_count_per_repo[repository_name] = 0
            # the second element of the value is the number of lambdas in a specific python file
        number_of_lambdas = all_files_dict_types[(filename, repository_name, repository_path)][1]
        dict_lambda_count_per_repo[repository_name] += number_of_lambdas
    dict_lambda_count_per_repo_to_df = {"ratio_lambdas_size": [], "lambdas_number": [], "repo_name": []}
    for key in dict_lambda_count_per_repo.keys():
        dict_lambda_count_per_repo_to_df["repo_name"].append(key)
        dict_lambda_count_per_repo_to_df["lambdas_number"].append(int(dict_lambda_count_per_repo[key]))
        dict_lambda_count_per_repo_to_df["ratio_lambdas_size"].append(dict_ratio_lambdas_repo_size[key])
    df_lambdas = pd.DataFrame.from_dict(dict_lambda_count_per_repo_to_df)
    df_repos_props = df_repos_props.sort_values(by=["repo_name"])
    df_lambdas = df_lambdas.sort_values(by=["repo_name"])
    df_repos_props["repo_name"] = df_repos_props["repo_name"].apply(lambda x: x.lower())
    df_lambdas["repo_name"] = df_lambdas["repo_name"].apply(lambda x: x.lower())
    df_repos_props = df_repos_props.merge(df_lambdas, on="repo_name")
    df_repos_props.to_csv("df_repo_props_with_lambda_stat.csv")
    print("the correlation between the number of stars and the number of lambdas is:\n"
          "{}".format(df_repos_props[["repo_number_of_stars", "lambdas_number"]].corr()))
    print("the correlation between the number of forks and the number of lambdas is:\n"
          "{}".format(df_repos_props[["repo_number_of_forks", "lambdas_number"]].corr()))
    print("the correlation between the percentage of the python language and the number of lambdas is:\n"
          "{}".format(df_repos_props[["percentage_python_lang", "lambdas_number"]].corr()))
    print("the correlation between the ratio of the repository size and the number of lambdas is:\n"
          "{}".format(df_repos_props[["ratio_lambdas_size", "lambdas_number"]].corr()))


def process_all_python_files_in_parallel(repos_parent_folder):
    """
    process all the python files in all the repositories in parallel to get the number of lambdas in each
    python file. save the results into dictionary
    :param repos_parent_folder: the parent folder of all the repositories downloaded after the scraping
    :return: all_files_dict_types: a dictionary containing the following:
    key = (filename, repository name, repository path)
    value = (dictionary containing the counts of the various usages of lambda expression in this python file,
    the number of lambda appearances)
    """
    all_files_dict_types = {}
    # get all the python files from all the repositories
    files = [f for f in glob.glob(r'{}/**/*.py'.format(repos_parent_folder), recursive=True)]
    lambdas_counts_in_files = 0
    # initialize a thread pool to do the calculation of the lambda statistics in each of the python
    # files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # construct a dictionary of future to filename and repository name
        future_to_filename = \
            {
                executor.submit(process_lambda_exp_single_file, filename):
                    (filename,
                     get_repository_dir_name(filename, 1, 1),
                     get_repository_dir_name(filename, 0, 1)) for filename in files
            }
        # for each of the futures, check if it finished and then take
        # the dictionary of lambdas statistics and merge it into the large dictionary
        for future in concurrent.futures.as_completed(future_to_filename):
            filename, repository_name, repository_path = future_to_filename[future]
            try:
                dict_types, num_lambda_in_file, num_of_code_lines = future.result()
                all_files_dict_types[(filename, repository_name, repository_path)] = (dict_types, num_lambda_in_file,
                                                                                      num_of_code_lines)
            except Exception:
                pass
                # print('%r generated an exception: %s' % (filename, exc))
        # terminate all the futures and shutdown the thread pool
        for future in future_to_filename:
            future.cancel()
        executor.shutdown()
    return all_files_dict_types


def plot_bar_plots_lambdas_types(all_files_dict_types):
    """

    :param all_files_dict_types:
    :return:
    """
    dict_types_accumulated_sum = {}
    for filename, repository_name, repository_path in all_files_dict_types.keys():
        dict_types, num_lambdas_in_file, num_lines_of_code = all_files_dict_types[(filename, repository_name, repository_path)]
        for type_name in dict_types.keys():
            if type_name not in dict_types_accumulated_sum.keys():
                dict_types_accumulated_sum[type_name] = 0
            dict_types_accumulated_sum[type_name] += dict_types[type_name]
    plt.bar(range(len(dict_types_accumulated_sum)), list(dict_types_accumulated_sum.values()), align='center')
    plt.yticks(np.arange(min(dict_types_accumulated_sum.values()), max(dict_types_accumulated_sum.values()) + 1, 100))
    plt.xticks(range(len(dict_types_accumulated_sum)), list(dict_types_accumulated_sum.keys()), rotation=45)
    plt.show()


def plot_CDF_number_of_lambdas_ratio(ratio_lambdas_repo_size):
    num_lambdas_ratio_list = []
    for repository_name in ratio_lambdas_repo_size.keys():
        num_lambdas_ratio_repository = ratio_lambdas_repo_size[repository_name]
        num_lambdas_ratio_list.append(num_lambdas_ratio_repository)
    lambdas_ratio_np = np.array(num_lambdas_ratio_list)
    lambdas_ratio_np_sorted = np.sort(lambdas_ratio_np)
    p = 1. * np.arange(len(lambdas_ratio_np)) / (len(lambdas_ratio_np) - 1)
    plt.plot(lambdas_ratio_np_sorted, p)
    plt.title("CDF - ratio between number of lambdas and the repository size")
    plt.xlabel('Ratio')
    plt.ylabel('Proportion of <= repositories')
    plt.show()


def main():
    df_repos_props = pd.read_csv("./repos_props.csv")
    all_files_dict_types = process_all_python_files_in_parallel("./pythonReposForMethods")
    ratio_lambdas_repo_size = calc_ratio_num_lambdas_repo_size(all_files_dict_types)
    check_correlation_between_repos_props_and_lambda_exp(df_repos_props, all_files_dict_types, ratio_lambdas_repo_size)
    avg_num_lambda_per_file = calc_average_num_lambda_per_file(all_files_dict_types)
    avg_num_lambda_per_repository = calc_average_num_lambdas_per_repository(all_files_dict_types)
    print("the average number of lambdas per file: {}".format(avg_num_lambda_per_file))
    print("the average number of lambdas per repository: {}".format(avg_num_lambda_per_repository))
    print("the ratio of lambdas and the repository size: {}".format(ratio_lambdas_repo_size))
    plot_bar_plots_lambdas_types(all_files_dict_types)
    plot_CDF_number_of_lambdas_ratio(ratio_lambdas_repo_size)


if __name__ == '__main__':
    main()
