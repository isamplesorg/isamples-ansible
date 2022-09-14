import os.path
import re

from git import Repo


ISAMPLES_TAG_PREFIX = "ISAMPLES-"
TAG_PATTERN = re.compile(f"{ISAMPLES_TAG_PREFIX}(\\d+)")

ISB_RELATIVE_PATH = "isb/isamples_inabox"
ELEVATE_RELATIVE_PATH = "isb/elevate"
WEBUI_RELATIVE_PATH = "isb/isamples_webui"


class ISamplesRepos:
    def __init__(self, path: str):
        self.docker_repo = build_repo(path)
        self.isb_repo = build_repo(os.path.join(path, ISB_RELATIVE_PATH))
        self.elevate_repo = build_repo(os.path.join(path, ELEVATE_RELATIVE_PATH))
        webui_full_path = os.path.join(path, WEBUI_RELATIVE_PATH)
        self.webui_repo = build_repo(webui_full_path, "gh-pages")


def checkout_branch(repo: Repo, branch: str = "develop"):
    git = repo.git
    git.checkout(branch)
    git.pull()


def build_repo(repo_path: str, branch: str = "develop") -> Repo:
    repo = Repo(repo_path)
    print(f"\n#####\nProcessing repository: {repo.remotes.origin.url}")
    origin = repo.remotes.origin
    print(f"Fetching origin for repo {repo_path}")
    origin.fetch()
    print(f"Checking out {branch} branch in repo {repo_path}")
    checkout_branch(repo, branch)
    assert not repo.bare
    if repo.is_dirty(untracked_files=False, submodules=False):
        print(
            f"Release tagging is only supported on clean repositories.  Repository at path f{repo_path} is dirty.  Exiting."
        )
        exit(-1)
    return repo


def pick_latest_tag(docker_repo: Repo, increment: bool) -> str:
    max_tag_number = 0
    for tag in docker_repo.tags:
        tag_match = TAG_PATTERN.match(tag.name)
        if tag_match is not None:
            tag_number = int(tag_match.group(1))
            if tag_number >= max_tag_number:
                max_tag_number = tag_number + 1
    if increment is False:
        max_tag_number -= 1
    return f"{ISAMPLES_TAG_PREFIX}{max_tag_number}"