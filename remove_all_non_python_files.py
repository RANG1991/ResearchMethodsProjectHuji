import os


def main():
    for path, subdirs, files in os.walk(r"C:\Users\Admin\PycharmProjects\pythonReposForMethods"):
        for name in files:
            try:
                file_ext = os.path.splitext(os.path.join(path, name))[1]
                # if file_ext != ".py":
                # os.remove(os.path.join(path, name))
            except PermissionError as e:
                print(e)


if __name__ == "__main__":
    main()
