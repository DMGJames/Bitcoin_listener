namespace :listener_pusher do
  desc "Install listener_pusher packages. Note: this will overwrite all other cron jobs!!"
  task :setup => [:install_dependencies, \
                  :add_cron_job, \
                  :upload_hostname_file, \
                  :link_hostname_file]
  
  task :install_dependencies do
    on roles(:all) do |host|
      uptime = capture(:uptime)
      info "Uptime: #{uptime}"
      sudo "apt-get -q -y install mysql-client"
      sudo "apt-get -q -y install python-pip"
      sudo "apt-get -q -y install python-mysqldb"
      sudo "apt-get -q -y install libmysqlclient-dev"
      execute "cd #{fetch(:deploy_to)}/current && sudo pip install -r requirement.txt"
      execute "rm -rf #{fetch(:deploy_to)}/current/bitnodes"
      execute "cd #{fetch(:deploy_to)}/current && git clone git@github.com:yutelin/bitnodes.git"
      begin
        execute "cd #{fetch(:deploy_to)}/current/geoip && ./update.sh"
      rescue Exception => e
        info "Exception on running ./update.sh. Ignored"
      end
    end
  end

  task :add_cron_job do
    on roles(:all) do |host|
      cron_job = "0 18 * * 1 cd #{fetch(:deploy_to)}/current/geoip/ && ./update.sh"
      config = ""
      begin
        config = capture(%Q{crontab -l 2>&1}).split "\n"
      rescue Exception => e
        info "Exception on execute crontab -l"
      end
      info "Current cron jobs:#{config}"
      unless config.include? cron_job
        execute %Q{echo "#{cron_job}" | crontab -}
      end
    end
  end

  task :upload_hostname_file do
    on roles(:all) do |host|
      upload_file "shared/HOSTNAME.erb", "#{shared_path}/HOSTNAME"
    end
  end

  task :link_hostname_file do
    on roles(:all) do |host|
      execute "cd /home/mcdeploy/listener_pusher/current && " \
              "ln -s #{shared_path}/HOSTNAME HOSTNAME"
    end
  end

  task :run_node_pusher_daemon do
    on roles(:all) do |host|
      execute "mkdir -p #{fetch(:daemon_conf_dir)}"
      conf_path = "#{fetch(:daemon_conf_dir)}/node_pusher.conf"
      upload! "config/daemon_conf/node_pusher.conf", conf_path
      sudo "mv #{conf_path} /etc/init/node_pusher.conf"
      sudo "initctl reload-configuration"
      execute "cd #{fetch(:deploy_to)}/current && python node_pusher_daemon_runner.py restart prod"
    end
  end

  task :run_transaction_pusher_daemon do
    on roles(:all) do |host|
      execute "mkdir -p #{fetch(:daemon_conf_dir)}"
      conf_path = "#{fetch(:daemon_conf_dir)}/transaction_pusher.conf"
      upload! "config/daemon_conf/transaction_pusher.conf", conf_path
      sudo "mv #{conf_path} /etc/init/transaction_pusher.conf"
      sudo "initctl reload-configuration"
      execute "cd #{fetch(:deploy_to)}/current && python transaction_pusher_daemon_runner.py restart prod"
    end
  end

  task :run_node_pinger_daemon do
    on roles(:all) do |host|
      execute "mkdir -p #{fetch(:daemon_conf_dir)}"
      conf_path = "#{fetch(:daemon_conf_dir)}/node_pinger.conf"
      upload! "config/daemon_conf/node_pinger.conf", conf_path
      sudo "mv #{conf_path} /etc/init/node_pinger.conf"
      sudo "initctl reload-configuration"
      execute "cd #{fetch(:deploy_to)}/current && python node_pinger_daemon_runner.py restart prod"
    end
  end

  desc "Add transaction post process cron job. Note: this will overwrite all other cron jobs!!"
  task :add_tx_post_cron_job do
    on roles(:all) do |host|
      cron_job = "*/10 * * * * cd #{fetch(:deploy_to)}/current/ && tx/transaction_post_process.py prod >> #{fetch(:deploy_to)}/current/tx_post_process.log"
      config = ""
      begin
        config = capture(%Q{crontab -l 2>&1}).split "\n"
      rescue Exception => e
        info "Exception on execute crontab -l"
      end
      info "Current cron jobs:#{config}"
      unless config.include? cron_job
        execute %Q{echo "#{cron_job}" | crontab -}
      end
    end
  end

  desc "Add transaction vin vout pusher cron job. Note: this will overwrite all other cron jobs!!"
  task :add_tx_vin_vout_pusher_cron_job do
    on roles(:all) do |host|
      cron_job = "*/15 * * * * cd #{fetch(:deploy_to)}/current/ && tx/transaction_vin_vout_pusher.py prod >> #{fetch(:deploy_to)}/current/tx_vin_vout_pusher.log"
      config = ""
      begin
        config = capture(%Q{crontab -l 2>&1}).split "\n"
      rescue Exception => e
        info "Exception on execute crontab -l"
      end
      info "Current cron jobs:#{config}"
      unless config.include? cron_job
        execute %Q{echo "#{cron_job}" | crontab -}
      end
    end
  end
end

def upload_file(from, to)
  [
    "lib/capistrano/templates/#{from}",
    File.expand_path("../../templates/#{from}", __FILE__)
  ].each do |path|
    if File.file?(path)
      info "Found #{path}"
      erb = File.read(path)
      upload! StringIO.new(ERB.new(erb, nil, '-').result(binding)), to
      break
    else
      warn "#{path} doesn't exist"
    end
  end
end