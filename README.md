# isamples-ansible
Repository for iSamples Ansible scripts

## Getting started
* Create a virtualenv:
`mkvirtualenv isamples-ansible`
* Or if the virtualenv already exists:
`workon isamples-ansible`
* Install dependencies using poetry
`poetry install`
* Make sure it works:
`ansible all -m ping --ask-pass`

## Making and pushing a release tag
* Have your iSamples Docker git repo checked out with all the submodules somewhere, then:
`python create_release_tag.py <PATH>`
  
## Pushing a release to mars.cyverse.org:
`ansible-playbook site.yml -i hosts -u <user> -K`