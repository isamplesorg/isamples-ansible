from git import Repo
from git.refs.tag import TagReference
import click
import os.path
import yaml

from utils import checkout_branch, build_repo, pick_latest_tag, ISamplesRepos, WEBUI_RELATIVE_PATH, ISB_RELATIVE_PATH, \
    ELEVATE_RELATIVE_PATH


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


def create_tag(repo: Repo, max_tag: str, branch: str = "develop") -> TagReference:
    return repo.create_tag(
        max_tag, branch, f"Tagging {max_tag} from branch {branch} for iSamples release.", True
    )


@click.command()
@click.argument(
    "path",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, readable=True
    ),
)
def main(path: str):
    isamples_repos = ISamplesRepos(path)
    docker_repo = isamples_repos.docker_repo
    isb_repo = isamples_repos.isb_repo
    elevate_repo = isamples_repos.elevate_repo
    webui_repo = isamples_repos.webui_repo

    # Pick the tag number inside the docker repo and distribute to the submodules
    max_tag = pick_latest_tag(docker_repo, True)

    checkout_branch(webui_repo, "gh-pages")
    # webui_repo.git.add(faceted_relative_path)
    # webui_repo.index.commit(f"Updated solr-faceted-search-react submodule to {max_tag}")
    tag = create_tag(webui_repo, max_tag, "gh-pages")
    print("Pushing isamples-webui")
    webui_repo.remotes.origin.push()
    webui_repo.remotes.origin.push(tag)

    checkout_branch(isb_repo)
    tag = create_tag(isb_repo, max_tag)
    print("Pushing isamples-inabox")
    isb_repo.remotes.origin.push()
    isb_repo.remotes.origin.push(tag)
    
    checkout_branch(elevate_repo)
    tag = create_tag(elevate_repo, max_tag)
    print("Pushing elevate")
    elevate_repo.remotes.origin.push()
    elevate_repo.remotes.origin.push(tag)

    # Now that we're done with webui and isb, update the submodule commits for both in Docker
    checkout_branch(docker_repo)
    print("Updating the isamples_webui submodule commit in isamples-docker")
    docker_repo.git.add(WEBUI_RELATIVE_PATH)
    docker_repo.index.commit(f"Updated isamples_webui submodule to {max_tag}")
    print("Updating the isamples_inabox submodule commit in isamples-docker")
    docker_repo.git.add(ISB_RELATIVE_PATH)
    docker_repo.index.commit(f"Updated isamples_inabox submodule to {max_tag}")
    print("Updating the elevate submodule commit in isamples-docker")
    docker_repo.git.add(ELEVATE_RELATIVE_PATH)
    docker_repo.index.commit(f"Updated elevate submodule to {max_tag}")    
    tag = create_tag(docker_repo, max_tag)
    docker_repo.remotes.origin.push()
    docker_repo.remotes.origin.push(tag)
    print("Pushing isamples-docker")
    print(f"Done writing tag {max_tag} for all repositories.")

    ansible_repo = Repo(".")
    write_vars_yaml(max_tag, ansible_repo)


if __name__ == "__main__":
    main()
