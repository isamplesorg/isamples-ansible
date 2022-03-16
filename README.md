# isamples-ansible
Repository for iSamples [Ansible](https://docs.ansible.com) scripts.  As of this writing, there are two main Ansible playbooks, one for deploying iSamples to existing servers and one for configuring the iSamples software stack on a new server.

## Configuring the iSamples ansible python virtual environment
Ansible is based on python, and python is best managed by using virtual environments.  iSamples manages its python dependencies using [poetry](https://python-poetry.org), so it's assumed you have that installed and know how to use python virtual environments.
Step by step:
* Create a virtualenv:
`mkvirtualenv isamples-ansible`
* Or if the virtualenv already exists:
`workon isamples-ansible`
* Install dependencies using poetry
`poetry install`
* Make sure it works:
`ansible all -m ping --ask-pass`

## Deploying iSamples releases to an existing server
The first ansible playbook is used to push iSamples releases to one or more existing servers.  The list of server groups to deploy to is contained in the `hosts` [inventory](https://docs.ansible.com/ansible/2.5/user_guide/intro_inventory.html) file.

### Making and pushing a release tag
Before you run the Ansible playbook, you'll want to make a new tag, as we only deploy iSamples releases off the develop branch using a custom tagger script.

* Have your iSamples Docker git repo checked out with all the submodules somewhere, then use that directory as the path argument to the python tagger script:
`python create_release_tag.py <PATH>`

When you run this, it will update the ansible `group_vars/all` file with the latest tag.  Ansible reads this to know which tag to check out on the target server.

### Pushing a release to a host group:
After you've made a new tag, you can push it to one of the host groups by running the `site.yml` Ansible playbook.

* The host groups are defined in the `hosts` file, and you can specify the group under the limit parameter e.g.:
`ansible-playbook site.yml -i hosts -u <ssh_user> -K --limit 'isc'`
In that example, we chose the `isc` group, which will push to the iSamples Central host group.  The options are as follows:
  * *-i* specifies the inventory file to use
  * *-u* specifies the ssh user for the remote host (Ansible runs all communication over ssh)
  * *-K* specifies to prompt for the credentials on the command-line.  The deploy script runs many tasks as root via `sudo`, so the ssh user will need sudo privileges.
  * *--limit 'isc'* specifies to limit the host inventory to the `isc` host group
* References:  
  * https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
  * https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html

### Host dependencies:
* The directory where we check out the project may need to have been manually initialized with git lfs (mars needed manual intervention, hyde did not)
* `sudo apt install acl/focal` -- the acl package is required for ansible to function properly on the remote host

## Configuring a new iSamples host
The other ansible playbook is used to configure a new iSamples host with all the host dependencies.  These instructions assume a virtual machine created and running on a local Mac, but there's no reason this ansible playbook couldn't be run on a remote linux server  anywhere.

### A note on templates
There are files checked into the repository with the `.template` extension.  These files must be copied to another file in the same location on the filesystem with the `.template` extension omitted, e.g.
`cp cloud-init.yaml.template cloud-init.yaml`
After you copy the file, open it with your favorite text editor and customize before running the playbook.  There are three such files in this repository:

* `cloud-init.yaml.template` -- specifies details for virtual machine creation, mainly account credentials on the virtual machine
* `group_vars/virtual_machines.template` -- specifies details for the https setup with certbot.  You'll need to have configured DNS beforehand, and ensure that port 80 of the IP that resolves the DNS is open for traffic and responding before running certbot.
* `multipass-hosts.yml.template` -- specifies details about where the virtual machine is located and which ssh account should be used to hit the VM

### Setting up a multipass VM for ansible to run against
Multipass is a very handy program for installing and configuring a Linux VM on a Mac host.  You can read about multipass here: https://multipass.run

* Install multipass: `brew install --cask multipass`
* Copy the `cloud-init.yaml.template` file to `cloud-init.yaml`, then insert your user account name, public key, and plaintext password contents into the file.
* Create a test VM: `multipass launch --name isamples-test --cloud-init cloud-init.yaml --disk 20G --mem 8G`.  Tweak parameters accordingly, but those settings do allow the iSamples software stack to come up as of 3/16/22.
* To verify the VM is working as expected, ssh to the VM by using the IP address -- you can obtain it by running `multipass info isamples-test` (or by looking at localhost if you're running with VirtualBox) ![Image of virtualbox ssh port config](virtualbox_ssh_port_mapping.png)
* Copy `multipass-hosts.yml.template` to `multipass-hosts.yml` and insert the relevant values.
* Verify you can ping the host with ansible: `ansible -i ./multipass-hosts.yml isamplesvm -m ping`
* Run the host configuration playbook: `ansible-playbook configure_isamples_server.yml -i ./multipass-hosts.yml -K`

### Virtualbox for port forwarding
In order to get port forwarding to work on the Mac, you need to install [https://www.virtualbox.org][virtualbox] and tell multipass to use it for networking.

* `sudo multipass set local.driver=virtualbox`
* You can then configure port forwarding as described on this page: https://multipass.run/docs/using-virtualbox-in-multipass-macos
* Note that you won't get a standard IP address the way you do with hyperkit -- you'll need to launch VirtualBox, see which port is forwarded, and include that port in `multipass-hosts.yml`.  Since the port is forwarded, you can just set the host to localhost. ![Image of virtualbox ssh port config](virtualbox_port_mapping.png)
