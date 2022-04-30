import re
import concurrent.futures
import glob


def count_lambda_exp_single_file(python_filename):
    with open(python_filename, "r") as f:
        python_file = f.read()
        return len(re.findall(r"lambda (.*?):", python_file))


def main():
    files = [f for f in glob.glob(r'C:\Users\Admin\PycharmProjects\pythonReposForMethods/**/*.py', recursive=True)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_filename = {executor.submit(count_lambda_exp_single_file, filename): filename for filename in
                              files}
        for future in concurrent.futures.as_completed(future_to_filename):
            filename = future_to_filename[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (filename, exc))
            else:
                if data > 0:
                    print('%r file contains %d lambda expressions' % (filename, data))


if __name__ == '__main__':
    main()
