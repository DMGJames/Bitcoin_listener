namespace :listener do
  ######################################## Setup listener environment ########################################
  desc "Install all listener package"
  task :setup => [:apt_get_update, :install_gcc, :install_redis, :install_bitcoind_dependencies]

  desc "Udpate apt-get"
  task :apt_get_update do
    on roles(:all) do |host|
      uptime = capture(:uptime)
      info "Uptime: #{uptime}"
      sudo "apt-get update"
    end
  end

  desc "Install gcc"
  task :install_gcc do
    on roles(:all) do |host|
      uptime = capture(:uptime)
      info "Uptime: #{uptime}"
      sudo "apt-get -q -y install make"
      sudo "apt-get -q -y install gcc"
      sudo "apt-get -q -y install git"
    end
  end

  desc "Install redis"
  task :install_redis do
    on roles(:all) do |host|
      uptime = capture(:uptime)
      info "Uptime: #{uptime}"
      sudo "sudo apt-get -q -y install redis-server"
      info "Update /etc/redis/redis.conf"
      execute "echo 'aof-rewrite-incremental-fsync yes' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'requirepass teammaicoin' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'maxclients 50000' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'maxmemory 32212254720' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'maxmemory-policy volatile-ttl' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'appendfsync no' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'activerehashing no' | sudo tee -a /etc/redis/redis.conf"
      execute "echo 'hz 30' | sudo tee -a /etc/redis/redis.conf"
      sudo "/etc/init.d/redis-server restart"
      sudo "ln -s /usr/bin/redis-cli /usr/local/bin" unless test("[ -e /usr/local/bin/redis-cli ]")
    end
  end
  
  desc "Install bitcoind dependencies"
  task :install_bitcoind_dependencies do
    on roles(:app) do |host|
      #execute "echo 'deb http://ftp.de.debian.org/debian squeeze main' | sudo tee -a /etc/apt/sources.list"
      sudo "apt-get -y update"
      sudo "apt-get -y upgrade"
        sudo "apt-get install -y build-essential"
        sudo "apt-get install -y libtool autotools-dev autoconf"
        sudo "apt-get install -y libssl-dev"
        sudo "apt-get install -y libboost-dev"
        sudo "apt-get install -y libboost-all-dev"
        sudo "add-apt-repository -y ppa:bitcoin/bitcoin"
        sudo "apt-get -y update"
        sudo "apt-get install -y libdb4.8-dev"
        sudo "apt-get install -y libdb4.8++-dev"

      #sudo "apt-get -q -y install build-essential"
      # sudo "apt-get -q -y install libtool autotools-dev autoconf"
      # sudo "apt-get -q -y install libssl-dev"
      # sudo "apt-get -q -y install libboost-all-dev"
      # sudo "apt-get -q -y install libdb4.8-dev --force-yes"
      # sudo "apt-get -q -y install libdb4.8++-dev --force-yes"
      # sudo "apt-get -q -y install libboost1.55-dev"
      # sudo "apt-get -q -y install libboost1.55-all-dev"
      # sudo "apt-get -q -y install libminiupnpc-dev"
      sudo "apt-get -q -y install pkg-config"
    end
  end

  ######################################## Install Bitcoind ########################################
  desc "Install bitcoin"
  task :install_bitcoind => [:build_bitcoind, :set_bitcoind_config,:run_bitcoind_daemon]

  desc "Build bitcoind"
  task :build_bitcoind do
    on roles(:app) do
      info "Build bitcoind"
      execute "cd /home/mcdeploy/listener/current && ./autogen.sh"
      execute "cd /home/mcdeploy/listener/current && ./configure"
      execute "cd /home/mcdeploy/listener/current && make && sudo make install"
    end
  end

  desc "Set bitcoind config file"
  task :set_bitcoind_config do
    on roles(:app) do |host|
      info "Check #{fetch(:bitcoin_dir)}"
      execute "mkdir #{fetch(:bitcoin_dir)}" unless test("[ -e #{fetch(:bitcoin_dir)} ]")
      unless test("[ -e #{fetch(:bitcoin_conf)} ]")
        execute "echo 'rpcuser=bitcoinrpc' >> #{fetch(:bitcoin_conf)}"
        execute "echo 'rpcpassword=151500d4d1a4750911109bf57928ec93' >> #{fetch(:bitcoin_conf)}"
      end
    end  
  end

  desc "Start bitcoind daemon"
  task :run_bitcoind_daemon do 
    on roles(:app) do |host|
      execute "mkdir -p #{fetch(:daemon_conf_dir)}"
      conf_path = "#{fetch(:daemon_conf_dir)}/bitcoind.conf"
      upload! "config/daemon_conf/bitcoind.conf", conf_path
      sudo "mv #{conf_path} /etc/init/bitcoind.conf"
      sudo "initctl reload-configuration"
      execute "#{fetch(:bitcoin_bin)} -daemon"
    end  
  end

end
