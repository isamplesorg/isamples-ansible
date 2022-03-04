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
  
## Pushing a release to a host group:
* The host groups are defined in the `hosts` file, and you can specify the group under the limit parameter e.g.:
`ansible-playbook site.yml -i hosts -u <ssh_user> -K --limit 'isc'`
* References:  
  ** https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
  ** https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html
  
### Host dependencies:
* The directory where we check out the project may need to have been manually initialized with git lfs (mars needed manual intervention, hyde did not)
* `sudo apt install acl/focal`