import re
import concurrent.futures
import glob

MAP_REDUCE_FILTER_PATTERN = r"(map|reduce|filter)(.*?)lambda (.*?):"
FUNC_ARG_PATTERN = r"\((.*?)=lambda (.*?):(.*?)\)"
RET_VALUE_PATTERN = r"return lambda (.*?):"
ITER_PATTERN = ""
UNICODE_PATTERN = r"lambda (.*?):(.*?).encode"
EXCEPTION_PATTERN = r"lambda (.*?): future.set_exception"
ASYNC_TASKS_PATTERN = ""


def count_lambda_exp_single_file(python_filename):
    with open(python_filename, "r") as f:
        python_file_text = f.read()
        num_lambda_in_file = len(re.findall(r"lambda (.*?):", python_file_text))
        if num_lambda_in_file > 0:
            dict_types = count_types_of_lambda_expressions(python_file_text)
        return dict_types, num_lambda_in_file


def count_types_of_lambda_expressions(python_file_text):
    dict_types = {"map_reduce_filter": len(re.findall(MAP_REDUCE_FILTER_PATTERN, python_file_text)),
                  "func_arg": len(re.findall(FUNC_ARG_PATTERN, python_file_text)),
                  "ret_value": len(re.findall(RET_VALUE_PATTERN, python_file_text)),
                  "unicode": len(re.findall(UNICODE_PATTERN, python_file_text)),
                  "exception": len(re.findall(EXCEPTION_PATTERN, python_file_text))}
    return dict_types


def main():
    files = [f for f in glob.glob(r'./pythonReposForMethods/**/*.py', recursive=True)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_filename = {executor.submit(count_lambda_exp_single_file, filename): filename for filename in
                              files}
        for future in concurrent.futures.as_completed(future_to_filename):
            filename = future_to_filename[future]
            try:
                dict_types, num_lambda_in_file = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (filename, exc))
            else:
                if num_lambda_in_file > 0:
                    print('%r file contains %s lambda expressions' % (filename, dict_types))


if __name__ == '__main__':
    main()
