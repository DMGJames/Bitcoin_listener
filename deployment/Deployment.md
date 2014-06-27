# Common Setup
1. Create EC2 instance.
1. `remote@machine $ sudo adduser mcdeploy ` 
1. `sudo vim /etc/sudoers` 
1. Add this: `mcdeploy    ALL=(ALL) NOPASSWD: ALL` 
1. `su mcdeploy; cd; mkdir .ssh`
1. `vi .ssh/authorized_keys` and add your public key


# Install listener (bitcoind)
1. Install code and build

	`cap listener deploy`


# Install listener_pusher
1. Install cdoe
	
	`cap listener_pusher deploy`
1. Install node_pusher daemon (optional)

	`cap listener_pusher listener_pusher:run_node_pusher_daemon`
1. Install transaction_pusher daemon (optional)

	`cap listener_pusher listener_pusher:run_transaction_pusher_daemon`
1. Install node_pinger daemon (optoinal)

	`cap listener_pusher listener_pusher:run_node_pinger_daemon`