## Phoenix Pherf driver

Some automation around running the Phoenix Pherf tool on a remote host.

`run-pherf` is invoked locally and prepares a remote host to run the Pherf tests. `pherf-driver.py` runs on the remote host.

This tool creates a temporary directory for itself beneath `$TMPDIR` for your remote host, prefixed with `'pherf'`

### Usage

`./run-pherf <ssh_user> <hostname> <private_key> [<test_user>]`

* `ssh_user` (required) is the user to specify to SSH to the remote host
* `hostname` (required) is the address of the remote host
* `private_key` (required) is the path to the private key (the `-i` SSH option)
* `test_user` (optional) the name of the user to `su` to on the remote host before running the pherf tool

Examples:

SSH as "elserj" and run the test as "elserj"

  `./run-pherf elserj my-ec2-host ~/.ssh/my-ec2-host-keypair.pem`

SSH as "root" and run the test as the unprivileged "elserj"

  `./run-pherf root my-ec2-host ~/.ssh/my-ec2-host-keypair.pem elserj`
