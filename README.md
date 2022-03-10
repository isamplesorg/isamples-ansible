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
* Have your iSamples Docker git repo checked out with all the submodules somewhere, then use that directory as the path argument to the python script:
`python create_release_tag.py <PATH>`
  
## Pushing a release to a host group:
* The host groups are defined in the `hosts` file, and you can specify the group under the limit parameter e.g.:
`ansible-playbook site.yml -i hosts -u <ssh_user> -K --limit 'isc'`
* References:  
  ** https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
  ** https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html
  
### Host dependencies:
* The directory where we check out the project may need to have been manually initialized with git lfs (mars needed manual intervention, hyde did not)
* `sudo apt install acl/focal` -- the acl package is required for ansible to function properly on the remote host

## Setting up a multipass VM for ansible to customize
You can read about multipass here: https://multipass.run

* Install multipass: `brew install --cask multipass`
* Copy the `cloud-init.yaml.template` file to `cloud-init.yaml`, then insert your user account name, public key, and plaintext password contents into the file.
* Create a test VM: `multipass launch --name isamples-test --cloud-init cloud-init.yaml --disk 20G --mem 8G`
* To verify the VM is working as expected, ssh to the VM by using the IP address -- you can obtain it by running `multipass info isamples-test`
* Copy `multipass-hosts.yml.template` to `multipass-hosts.yml` and insert the relevant values.
* Verify you can ping the host with ansible: `ansible -i ./multipass-hosts.yml multipassvm1 -m ping`
* Run the host configuration playbook: `ansible-playbook configure_isamples_server.yml -i ./multipass-hosts.yml -K`