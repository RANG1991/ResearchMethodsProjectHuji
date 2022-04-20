import pandas as pd


def main():
    df_repos = pd.read_csv("./repos_props.csv")
    df_repos["repo_is_forked"] = df_repos["repo_is_forked"].map({'TRUE': True, 'FALSE': False})
    df_repos = df_repos[df_repos["repo_is_forked"] is False]
    df_repos_links = df_repos["repo_link"].tolist()
    repos_links = " ".join(df_repos_links)
    with open("./clone_all_python_repos.bat", "w") as f:
        f.write("git clone {}".format(repos_links))


if __name__ == '__main__':
    main()
