import re
import concurrent.futures
import glob
import os
import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path

# regexes for lambda usages patterns
MAP_REDUCE_FILTER_PATTERN = r"(map|reduce|filter)(.*?)lambda (.*?):"
FUNC_ARG_PATTERN = r"\((.*?)=lambda (.*?):(.*?)\)"
RET_VALUE_PATTERN = r"return lambda (.*?):"
ITER_PATTERN = r"lambda (.*?):(.*?)list|tuple|string|dict"
UNICODE_PATTERN = r"lambda (.*?):(.*?).encode"
EXCEPTION_PATTERN = r"lambda (.*?): future.set_exception"
ASYNC_TASKS_PATTERN = r"lambda (.*?):(.*?)async"


def process_lambda_exp_single_file(python_filename):
    """
    count the lambda expressions: appearances and usages in a single python file
    :param python_filename: the path of the file to be calculated
    :return: dict_types - a dictionary containing the types of the lambda expressions
    to the count of them
    num_lambdas_in_file - the total number of the lambda expressions in this file
    """
    with open(python_filename, "r", encoding="utf-8") as f:
        python_file_text = f.read()
        num_lambda_in_file = len(re.findall(r"lambda (.*?):", python_file_text))
        dict_types = {}
        if num_lambda_in_file > 0:
            dict_types = count_usages_of_lambda_expressions(python_file_text)
        return dict_types, num_lambda_in_file


def count_usages_of_lambda_expressions(python_file_text):
    """
    count the usages of lambda expressions per single python file
    :param python_file_text: the python file as string (text)
    :return: dict_type - the type of each lambda expression to its number in this
    specific file
    """
    dict_types = {"map_reduce_filter": len(re.findall(MAP_REDUCE_FILTER_PATTERN, python_file_text)),
                  "func_arg": len(re.findall(FUNC_ARG_PATTERN, python_file_text)),
                  "ret_value": len(re.findall(RET_VALUE_PATTERN, python_file_text)),
                  "unicode": len(re.findall(UNICODE_PATTERN, python_file_text)),
                  "exception": len(re.findall(EXCEPTION_PATTERN, python_file_text)),
                  "async": len(re.findall(ASYNC_TASKS_PATTERN, python_file_text)),
                  "iterators": len(re.findall(ITER_PATTERN, python_file_text))}
    return dict_types


def calc_average_num_lambda_per_file(all_files_dict_types):
    """
    calculates the average number of lambda usages per file over all the repositories
    :param all_files_dict_types: key=(file_name, repository_name), value = (dict. counts the different usages of lambda
                                 expression in that file, number of lambda appearances)
    :return: average number of lambda usages per file
    """
    lambda_count = 0
    for key in all_files_dict_types.keys():
        # the second element of the value of each key is the number of lambdas in a specific python file
        lambda_count += all_files_dict_types[key][1]
    return lambda_count / len(all_files_dict_types)


def calc_average_num_lambdas_per_repository(all_files_dict_types):
    """
    calculates the average number of lambda usages per repository
    :param all_files_dict_types: key=(file_name, repository_name), value = (dict. counts the different usages of lambda
                                 expression in that file, number of lambda appearances)
    :return: average number of lambda usages per repository
    """
    dict_lambda_count_per_repo = {}
    for key in all_files_dict_types.keys():
        # the second element of each key is the repository name
        # if the repository name is not in the keys of the dictionary, add it with a count of zero
        if key[1] not in dict_lambda_count_per_repo.keys():
            dict_lambda_count_per_repo[key[1]] = 0
            # the second element of the value of each key is the number
            # of lambdas in a specific python file
        dict_lambda_count_per_repo[key[1]] += all_files_dict_types[key][1]
    for key in dict_lambda_count_per_repo.keys():
        dict_lambda_count_per_repo[key] = dict_lambda_count_per_repo[key] \
                                          / len(dict_lambda_count_per_repo)
    return dict_lambda_count_per_repo


def get_repository_dir_name(path, start_loc_path, end_loc_path):
    """
    get the repository name (directory name) based on the full path of the python file
    :param end_loc_path:
    :param start_loc_path:
    :param path: full path of the python file
    :return: the directory (repository) name
    """
    path = os.path.normpath(path)
    split_path = path.split(os.sep)
    return "/".join(split_path[start_loc_path: end_loc_path + 1])


def calc_ratio_lambdas_repo_size(repos_parent_folder, all_files_dict_types):
    """
    calculate the lambdas ratio to the repository size in bytes
    :param repos_parent_folder: the parent folder of all the repositories folders
    :param all_files_dict_types: key=(file_name, repository_name), value = (dict. counts the different usages of lambda
                                 expression in that file, number of lambda appearances)
    :return:
    """
    dict_number_of_lambdas_per_repo = {}
    # make a dictionary with the number of lambdas in each repository
    for key in all_files_dict_types.keys():
        # the second element of each key is the repository name
        # if the repository name is not in the keys of the dictionary, add it with a count of zero
        repository_name = key[1]
        repository_path = key[2]
        if (repository_name, repository_path) not in dict_number_of_lambdas_per_repo.keys():
            dict_number_of_lambdas_per_repo[(repository_name, repository_path)] = 0
            # the second element of the value of each key is the number
            # of lambdas in a specific python file
        number_of_lambdas_in_file = all_files_dict_types[key][1]
        dict_number_of_lambdas_per_repo[(repository_name, repository_path)] += number_of_lambdas_in_file
    dict_lambdas_size_ratio_per_repo = {}
    for key in dict_number_of_lambdas_per_repo.keys():
        repository_name = key[0]
        repository_path = key[1]
        size_of_repo_bytes = sum(Path(f).stat().st_size for f in glob.glob("./{}/**/*.py".format(repository_path)))
        if size_of_repo_bytes == 0:
            print("the size of python files in bytes in this repository is zero. the repository path is:{}"
                  .format(repository_path))
            dict_lambdas_size_ratio_per_repo[repository_name] = (0, 0)
        else:
            dict_lambdas_size_ratio_per_repo[repository_name] = (dict_number_of_lambdas_per_repo[key]
                                                                 / size_of_repo_bytes, size_of_repo_bytes)
    return dict_lambdas_size_ratio_per_repo


def check_correlation_between_repos_props_and_lambda_exp(df_repos_props, all_files_dict_types, dict_ratio_lambdas_repo_size):
    """
    calculate correlation measurements with respect to the lambdas number in each repository
    :param dict_ratio_lambdas_repo_size:
    :param df_repos_props: the data frame containing all the repositories properties extracted from the github
    crawling
    :param all_files_dict_types: key=(file_name, repository_name), value = (dict. counts the different usages of lambda
                                 expression in that file, number of lambda appearances)
    :return:
    """
    # extract from the repository name in the data frame only the name (the name before this action is
    # all the path with slashes)
    df_repos_props["repo_name"] = df_repos_props["repo_name"].apply(func=get_repository_dir_name, args=(1, 1))
    # remove the percentage sign from the percentage and remain only with the number as float
    df_repos_props["percentage_python_lang"] = df_repos_props["percentage_python_lang"].apply(lambda x:
                                                                                              float(x.replace("%", "")))
    # if the letter 'k' exists (the number is in thousands), replace it with '000' and remove the dot
    # if exists
    df_repos_props["repo_number_of_stars"] = df_repos_props["repo_number_of_stars"].apply(lambda x:
                                                                                          float(x.replace(".", "")
                                                                                                .replace("k", "000")
                                                                                                if "k" in x else x))
    # if the letter 'k' exists (the number is in thousands), replace it with '000' and remove the dot
    # if exists
    df_repos_props["repo_number_of_forks"] = df_repos_props["repo_number_of_forks"].apply(lambda x:
                                                                                          float(x.replace(".", "")
                                                                                                .replace("k", "000")
                                                                                                if "k" in x else x))
    dict_lambda_count_per_repo = {}
    for key in all_files_dict_types.keys():
        # the second element of each key is the repository name
        # if the repository name is not in the keys of the dictionary, add it with a count of zero
        if key[1] not in dict_lambda_count_per_repo.keys():
            dict_lambda_count_per_repo[key[1]] = 0
            # the second element of the value of each key is the number
            # of lambdas in a specific python file
        dict_lambda_count_per_repo[key[1]] += all_files_dict_types[key][1]
    dict_lambda_count_per_repo_to_df = {"ratio_lambdas_size": [], "lambdas_number": [], "repo_name": []}
    for key in dict_lambda_count_per_repo.keys():
        dict_lambda_count_per_repo_to_df["repo_name"].append(key)
        dict_lambda_count_per_repo_to_df["lambdas_number"].append(int(dict_lambda_count_per_repo[key]))
        dict_lambda_count_per_repo_to_df["ratio_lambdas_size"].append(dict_ratio_lambdas_repo_size[key][1])
    df_lambdas = pd.DataFrame.from_dict(dict_lambda_count_per_repo_to_df)
    df_repos_props = df_repos_props.sort_values(by=["repo_name"])
    df_lambdas = df_lambdas.sort_values(by=["repo_name"])
    df_repos_props["repo_name"] = df_repos_props["repo_name"].apply(lambda x: x.lower())
    df_lambdas["repo_name"] = df_lambdas["repo_name"].apply(lambda x: x.lower())
    df_repos_props = df_repos_props.merge(df_lambdas, on="repo_name")
    df_repos_props.to_csv("df_repo_props_with_lambda_stat.csv")
    print(df_repos_props[["repo_number_of_stars", "lambdas_number"]].corr())
    print(df_repos_props[["repo_number_of_forks", "lambdas_number"]].corr())
    print(df_repos_props[["percentage_python_lang", "lambdas_number"]].corr())
    print(df_repos_props[["ratio_lambdas_size", "lambdas_number"]].corr())


def count_lambdas_in_all_repositories(repos_parent_folder):
    all_files_dict_types = {}
    # get all the python files from all the repositories downloaded
    files = [f for f in glob.glob(r'{}/**/*.py'.format(repos_parent_folder), recursive=True)]
    lambdas_counts_in_files = 0
    # initialize thread pool to do the calculation of the lambda statistics, in each of the files in parallel
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
                dict_types, num_lambda_in_file = future.result()
                all_files_dict_types[(filename, repository_name, repository_path)] = (dict_types, num_lambda_in_file)
            except Exception as exc:
                print('%r generated an exception: %s' % (filename, exc))
        # terminate all the futures and shutdown the thread pool
        for future in future_to_filename:
            future.cancel()
        executor.shutdown()
    return all_files_dict_types


def main():
    df_repos_props = pd.read_csv("./repos_props.csv")
    all_files_dict_types = count_lambdas_in_all_repositories("./pythonReposForMethods")
    ratio_lambdas_repo_size = calc_ratio_lambdas_repo_size("./pythonReposForMethods", all_files_dict_types)
    check_correlation_between_repos_props_and_lambda_exp(df_repos_props, all_files_dict_types, ratio_lambdas_repo_size)
    num_lambda_per_file = calc_average_num_lambda_per_file(all_files_dict_types)
    num_lambda_per_repository = calc_average_num_lambdas_per_repository(all_files_dict_types)
    print(num_lambda_per_file)
    print(num_lambda_per_repository)
    print(ratio_lambdas_repo_size)


if __name__ == '__main__':
    main()
