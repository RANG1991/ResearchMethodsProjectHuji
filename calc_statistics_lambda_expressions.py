import re
import concurrent.futures
import glob
import os

MAP_REDUCE_FILTER_PATTERN = r"(map|reduce|filter)(.*?)lambda (.*?):"
FUNC_ARG_PATTERN = r"\((.*?)=lambda (.*?):(.*?)\)"
RET_VALUE_PATTERN = r"return lambda (.*?):"
ITER_PATTERN = r"lambda (.*?):(.*?)list|tuple|string|dict"
UNICODE_PATTERN = r"lambda (.*?):(.*?).encode"
EXCEPTION_PATTERN = r"lambda (.*?): future.set_exception"
ASYNC_TASKS_PATTERN = r"lambda (.*?):(.*?)async"


def count_lambda_exp_single_file(python_filename):
    with open(python_filename, "r") as f:
        python_file_text = f.read()
        num_lambda_in_file = len(re.findall(r"lambda (.*?):", python_file_text))
        dict_types = {}
        if num_lambda_in_file > 0:
            dict_types = count_types_of_lambda_expressions(python_file_text)
        return dict_types, num_lambda_in_file


def count_types_of_lambda_expressions(python_file_text):
    dict_types = {"map_reduce_filter": len(re.findall(MAP_REDUCE_FILTER_PATTERN, python_file_text)),
                  "func_arg": len(re.findall(FUNC_ARG_PATTERN, python_file_text)),
                  "ret_value": len(re.findall(RET_VALUE_PATTERN, python_file_text)),
                  "unicode": len(re.findall(UNICODE_PATTERN, python_file_text)),
                  "exception": len(re.findall(EXCEPTION_PATTERN, python_file_text)),
                  "async": len(re.findall(ASYNC_TASKS_PATTERN, python_file_text)),
                  "iterators": len(re.findall(ITER_PATTERN, python_file_text))}
    return dict_types


def get_repository_dir_name(path):
    path = os.path.normpath(path)
    split_path = path.split(os.sep)
    return split_path[1]


def main():
    all_files_dict_types = {}
    files = [f for f in glob.glob(r'./pythonReposForMethods/**/*.py', recursive=True)]
    lambdas_counts_in_files = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_filename = \
        {
            executor.submit(count_lambda_exp_single_file, filename):
                (filename, get_repository_dir_name(filename)) for filename in files
        }
        for future in concurrent.futures.as_completed(future_to_filename):
            filename, repository_name = future_to_filename[future]
            try:
                dict_types, num_lambda_in_file = future.result()
                if not len(all_files_dict_types):
                    all_files_dict_types.update(dict_types)
                else:
                    for key in dict_types.keys():
                        all_files_dict_types[key] += dict_types[key]
            except Exception as exc:
                print('%r generated an exception: %s' % (filename, exc))
            else:
                if num_lambda_in_file > 0:
                    print('done counting lambdas for file %r in repository %r ' % (filename, repository_name))
                    lambdas_counts_in_files += 1
                    if lambdas_counts_in_files > 1000:
                        break
        print(all_files_dict_types)
        for future in future_to_filename:
            future.cancel()
        executor.shutdown()


if __name__ == '__main__':
    main()
