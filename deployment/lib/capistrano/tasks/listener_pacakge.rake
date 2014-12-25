namespace :listener do
  ######################################## Setup listener environment ########################################
  desc "Install all listener package"
  task :setup => [:stop_bitcoind, \
                  :apt_get_update, \
                  :install_gcc, \
                  :install_redis, \
                  :install_bitcoind_dependencies, \
                  :install_redis3m, \
                  :set_ld_library_path]

  desc "Stop bitcoind if it is running"
  task :stop_bitcoind do
    on roles(:app) do |host|
      info "Stop bitcoind"
      #1. Check pid existence
      info fetch(:bitcoin_pid)
      if remote_file_exists?(fetch(:bitcoin_pid))
        info "Found pid file. Stop bitcoind"
        execute "#{fetch(:bitcoin_bin)} stop"
      else
        info "Doesn't found pid file: skip"
      end
    end
  end

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
      #1. Backup old redis.conf
      if remote_file_exists?(fetch(:redis_conf)) && !remote_file_exists?(fetch(:redis_conf_bak))
        sudo "cp #{fetch(:redis_conf)} #{fetch(:redis_conf_bak)}"
      end
      #2. Install redis
      sudo "sudo apt-get -q -y install redis-server"

      #3. Upload redis.conf
      info "Update /etc/redis/redis.conf"
      execute "mkdir -p #{fetch(:daemon_conf_dir)}"
      conf_path = "#{fetch(:daemon_conf_dir)}/redis.conf"
      upload! "config/daemon_conf/redis.conf", conf_path
      sudo "mv #{conf_path} #{fetch(:redis_conf)}"

      #4. Restart redis
      info "Start redis"
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

  desc "Install redis3m"
  task :install_redis3m do
    on roles(:app) do |host|
      sudo "apt-get install libmsgpack-dev libboost-thread-dev libboost-date-time-dev libboost-test-dev libboost-filesystem-dev libboost-system-dev libhiredis-dev cmake build-essential"
      execute "git clone git@github.com:wpwlee/redis3m.git"
      execute "cd /home/mcdeploy/redis3m && " \
              "cmake . && make && sudo make install"
      execute "rm -rf redis3m"
    end
  end

  desc "Set LD_LIBRARY_PATH"
  task :set_ld_library_path do
    on roles(:app) do |host|
      upload! "lib/capistrano/templates/ld_library_path.sh", "/tmp"
      sudo "mv /tmp/ld_library_path.sh /etc/profile.d"
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
      #1. Upload bitcoind
      conf_path = "#{fetch(:daemon_conf_dir)}/bitcoind.conf"
      upload! "config/daemon_conf/bitcoind.conf", conf_path
      sudo "mv #{conf_path} #{fetch(:bitcoin_conf)}"
    end  
  end

  desc "Start bitcoind daemon"
  task :run_bitcoind_daemon do 
    on roles(:app) do |host|
      execute "mkdir -p #{fetch(:daemon_conf_dir)}"
      conf_path = "#{fetch(:daemon_conf_dir)}/bitcoind_daemon.conf"
      upload! "config/daemon_conf/bitcoind_daemon.conf", conf_path
      sudo "mv #{conf_path} /etc/init/bitcoind.conf"
      sudo "initctl reload-configuration"
      execute "#{fetch(:bitcoin_bin)} -daemon"
    end  
  end

end

def remote_file_exists?(path)
  if test("[ -f #{path} ]")
    return true
  else
    return false
  end
end