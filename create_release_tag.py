from git import Repo
import click
import os.path
import re

ISAMPLES_TAG_PREFIX = "ISAMPLES-"
TAG_PATTERN = re.compile(f"{ISAMPLES_TAG_PREFIX}\(\\d+\)")


def checkout_develop(repo: Repo):
    git = repo.git
    git.checkout("develop")
    git.pull()


def build_repo(repo_path: str) -> Repo:
    repo = Repo(repo_path)
    print(f"\n#####\nProcessing repository: {repo.remotes.origin.url}")
    origin = repo.remotes.origin
    print(f"Fetching origin for repo {repo_path}")
    origin.fetch()
    print(f"Checking out develop branch in repo {repo_path}")
    checkout_develop(repo)
    assert not repo.bare
    if repo.is_dirty(untracked_files=False, submodules=False):
        print(f"Release tagging is only supported on clean repositories.  Repository at path f{repo_path} is dirty.  Exiting.")
        exit(-1)
    return repo


def pick_latest_tag(docker_repo: Repo) -> str:
    max_tag_number = 0
    for tag in docker_repo.tags:
        tag_match = TAG_PATTERN.match(tag.name)
        if tag_match is not None:
            tag_number = int(tag_match.group(1))
            if tag_number > max_tag_number:
                max_tag_number = tag_number
    return f"{ISAMPLES_TAG_PREFIX}{max_tag_number}"


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True),
)
def main(path: str):
    docker_repo = build_repo(path)
    isb_repo = build_repo(os.path.join(path, "isb/isamples_inabox"))
    webui_relative_path = "isb/isamples_webui"
    webui_full_path = os.path.join(path, webui_relative_path)
    webui_repo = build_repo(webui_full_path)
    faceted_relative_path = "src/node_modules/solr-faceted-search-react"
    solr_faceted_search_repo = build_repo(os.path.join(webui_full_path, faceted_relative_path))

    # Pick the tag number inside the docker repo and distribute to the submodules
    max_tag = pick_latest_tag(docker_repo)
    print("repo not dirty")
    # Start by making a tag in solr_faceted_search, then propagate the submodule commit upward
    solr_faceted_search_repo.create_tag(max_tag, "develop", f"Tagging {max_tag} for iSamples release.", True)
    checkout_develop(solr_faceted_search_repo)
    print("Pushing solr-faceted-search")
    solr_faceted_search_repo.remotes.origin.push()

    # Now that we're done with solr-faceted-search, update the submodule commit in webui
    print("\n\nUpdating the solr-faceted-search submodule commit in webui")
    checkout_develop(webui_repo)
    webui_repo.git.add(faceted_relative_path)
    webui_repo.index.commit(f"Updated solr-faceted-search-react submodule to {max_tag}")
    webui_repo.create_tag(max_tag, "develop", f"Tagging {max_tag} for iSamples release.", True)
    print("Pushing webui")
    webui_repo.remotes.origin.push()

    checkout_develop(isb_repo)
    isb_repo.create_tag(max_tag, "develop", f"")

    # Now that we're done with webui, update the submodule commit in root
    checkout_develop(docker_repo)
    docker_repo.git.add(webui_relative_path)
    docker_repo.index.commit(f"Updated isamples-webui submodule to {max_tag}")




if __name__ == "__main__":
    main()
