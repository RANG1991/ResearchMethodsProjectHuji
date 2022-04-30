import pandas as pd


def main():
    df_repos = pd.read_csv("./repos_props.csv")
    df_repos = df_repos[df_repos["repo_is_forked"] == False]
    df_repos = df_repos[df_repos["percentage_python_lang"] >= 60]
    df_repos_links = df_repos["repo_link"].tolist()
    with open("../pythonReposForMethods/clone_all_python_repos.sh", "w") as f:
        for i in range(100):
            f.write("git clone {}\n".format(df_repos_links[i]))


if __name__ == '__main__':
    main()
