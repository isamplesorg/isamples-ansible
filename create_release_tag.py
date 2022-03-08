from git import Repo
from git.refs.tag import TagReference
import click
import os.path
import re
import yaml

ISAMPLES_TAG_PREFIX = "ISAMPLES-"
TAG_PATTERN = re.compile(f"{ISAMPLES_TAG_PREFIX}(\\d+)")


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
        print(
            f"Release tagging is only supported on clean repositories.  Repository at path f{repo_path} is dirty.  Exiting."
        )
        exit(-1)
    return repo


def pick_latest_tag(docker_repo: Repo) -> str:
    max_tag_number = 0
    for tag in docker_repo.tags:
        tag_match = TAG_PATTERN.match(tag.name)
        if tag_match is not None:
            tag_number = int(tag_match.group(1))
            if tag_number >= max_tag_number:
                max_tag_number = tag_number + 1
    return f"{ISAMPLES_TAG_PREFIX}{max_tag_number}"


def write_vars_yaml(max_tag: str, ansible_repo: Repo):
    vars_path = "group_vars/all"
    with open(vars_path, "r") as yaml_file:
        yaml_vars = yaml.full_load(yaml_file)
    yaml_vars["latest_tag"] = max_tag
    with open("group_vars/all", "w") as writable_yaml_file:
        yaml.dump(yaml_vars, writable_yaml_file)
    ansible_repo.git.add(vars_path)
    ansible_repo.index.commit(f"Updated common_vars to tag {max_tag}")
    tag = ansible_repo.create_tag(
        max_tag, "main", f"Tagging {max_tag} for iSamples release.", True
    )
    print("Pushing isamples-ansible")
    ansible_repo.remotes.origin.push()
    ansible_repo.remotes.origin.push(tag)


def create_tag(repo: Repo, max_tag: str) -> TagReference:
    return repo.create_tag(
        max_tag, "develop", f"Tagging {max_tag} for iSamples release.", True
    )


@click.command()
@click.argument(
    "path",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, readable=True
    ),
)
def main(path: str):
    docker_repo = build_repo(path)
    isb_relative_path = "isb/isamples_inabox"
    isb_repo = build_repo(os.path.join(path, isb_relative_path))
    webui_relative_path = "isb/isamples_webui"
    webui_full_path = os.path.join(path, webui_relative_path)
    webui_repo = build_repo(webui_full_path)
    faceted_relative_path = "src/node_modules/solr-faceted-search-react"
    solr_faceted_search_repo = build_repo(
        os.path.join(webui_full_path, faceted_relative_path)
    )

    # Pick the tag number inside the docker repo and distribute to the submodules
    max_tag = pick_latest_tag(docker_repo)

    # Start by making a tag in solr_faceted_search, then propagate the submodule commit upward
    tag = create_tag(solr_faceted_search_repo, max_tag)
    checkout_develop(solr_faceted_search_repo)
    print("\nPushing solr-faceted-search")
    solr_faceted_search_repo.remotes.origin.push()
    solr_faceted_search_repo.remotes.origin.push(tag)

    # Now that we're done with solr-faceted-search, update the submodule commit in webui
    print("Updating the solr-faceted-search submodule commit in webui")
    checkout_develop(webui_repo)
    webui_repo.git.add(faceted_relative_path)
    webui_repo.index.commit(f"Updated solr-faceted-search-react submodule to {max_tag}")
    tag = create_tag(webui_repo, max_tag)
    print("Pushing isamples-webui")
    webui_repo.remotes.origin.push()
    webui_repo.remotes.origin.push(tag)

    checkout_develop(isb_repo)
    tag = create_tag(isb_repo, max_tag)
    print("Pushing isamples-inabox")
    isb_repo.remotes.origin.push()
    isb_repo.remotes.origin.push(tag)

    # Now that we're done with webui and isb, update the submodule commits for both in Docker
    checkout_develop(docker_repo)
    print("Updating the isamples_webui submodule commit in isamples-docker")
    docker_repo.git.add(webui_relative_path)
    docker_repo.index.commit(f"Updated isamples_webui submodule to {max_tag}")
    print("Updating the isamples_inabox submodule commit in isamples-docker")
    docker_repo.git.add(isb_relative_path)
    docker_repo.index.commit(f"Updated isamples_inabox submodule to {max_tag}")
    tag = create_tag(docker_repo, max_tag)
    docker_repo.remotes.origin.push()
    docker_repo.remotes.origin.push(tag)
    print("Pushing isamples-docker")
    print(f"Done writing tag {max_tag} for all repositories.")

    ansible_repo = Repo(".")
    write_vars_yaml(max_tag, ansible_repo)


if __name__ == "__main__":
    main()
