import datetime
import re
import sys

import dateutil.parser
from github.Repository import Repository


def request(message: str) -> str:
    input_var = input('What is the required '.join(message))
    return input_var


def __get_repo(repo_name: str, org_name: str) -> Repository:
    import configparser
    from github import Github, UnknownObjectException, GithubException, BadCredentialsException

    config = configparser.ConfigParser()
    config.read('config.ini')

    github_config = config['Github']

    org = org_name if org_name else github_config.get('Organization')
    access_token = github_config.get('AccessToken')

    try:
        g = Github(access_token)
        repo_container = g.get_organization(org) if org else g
        return repo_container.get_repo(repo_name)
    except UnknownObjectException:
        sys.exit(f'Repository "{repo_name}" was not found{" in " + org if org else ""}!')
    except BadCredentialsException:
        sys.exit('Unauthorized: You need to provide a valid AccessToken. Please add it on config.ini file.')
    except GithubException as ex:
        sys.exit(ex.data)


def __confirm_execute() -> bool:
    response = input(
        "Are you completely sure you want to execute this? The removal of branches cannot be undone! (y/n) ")
    return response == 'y'


def delete_branches(repo_name: str,
                    org_name: str = "",
                    age: int = 60,
                    ignore_pattern: str = "^((stream/.*/)?release/.*|master)",
                    quiet: bool = False,
                    dry_run: bool = False) -> None:
    if not __confirm_execute():
        sys.exit(0)

    repo = __get_repo(repo_name, org_name)
    pattern = re.compile(ignore_pattern)

    today = datetime.date.today()

    for branch in list(repo.get_branches()):
        if branch.protected or pattern.match(branch.name):
            print(f'Ignoring: {branch.name}')
            continue

        author_object = branch.commit.raw_data['commit']['author']
        author_name = author_object['name']
        last_commit = dateutil.parser.parse(author_object['date']).date()
        delta = today - last_commit

        if delta.days > age:
            if not quiet:
                print(f'Branch - name: {branch.name}, age: {delta.days}, last commit: {author_name}')
            if not dry_run:
                repo.get_git_ref(f'heads/{branch.name}').delete()
