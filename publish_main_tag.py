from typing import Optional

import click
from git import Repo, TagReference

from utils import ISamplesRepos, pick_latest_tag

MAIN_TAG_NAME = "ISAMPLES-MAIN"


def _cut_tag_and_push(source_tag: str, target_repo: Repo) -> TagReference:
    commit_msg = f"Moving {MAIN_TAG_NAME} to point to {source_tag} for release"
    target_repo.delete_tag(MAIN_TAG_NAME)
    target_repo.remotes.origin.push(f":{MAIN_TAG_NAME}")
    tag = target_repo.create_tag(MAIN_TAG_NAME, source_tag, commit_msg, True)
    target_repo.remotes.origin.push()
    target_repo.remotes.origin.push(tag)
    return tag


@click.command()
@click.argument(
    "path",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, readable=True
    ),
)
@click.option(
    "--source_tag",
    default=None
)
def main(path: str, source_tag: Optional[str]):
    isamples_repos = ISamplesRepos(path)
    if source_tag is None:
        source_tag = pick_latest_tag(isamples_repos.docker_repo, False)
    print(f"Cutting new {MAIN_TAG_NAME} from {source_tag} in all iSamples Repos")
    print("Cutting tag and pushing isamples-docker")
    _cut_tag_and_push(source_tag, isamples_repos.docker_repo)
    print("Cutting tag and pushing isamples-inabox")
    _cut_tag_and_push(source_tag, isamples_repos.isb_repo)
    print("Cutting tag and pushing isamples-webui")
    _cut_tag_and_push(source_tag, isamples_repos.webui_repo)
    print("Success.")

if __name__ == "__main__":
    main()
