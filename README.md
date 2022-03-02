# isamples-ansible
Repository for iSamples Ansible scripts

## Getting started
* Create a virtualenv:
`mkvirtualenv isamples-ansible`
* Or if the virtualenv already exists:
`workon isamples-ansible`
* Install ansible using pip:
`python -m pip install ansible`
* Make sure it works:
`ansible all -m ping --ask-pass`

## Running the script
`ansible-playbook site.yml -i hosts -u <user> -K`