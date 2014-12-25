set :user, 'mcdeploy'
role :app, [fetch(:user) + "@" + fetch(:server)]
role :web, [fetch(:user) + "@" + fetch(:server)]
role :db,  [fetch(:user) + "@" + fetch(:server)]
server fetch(:server), user: fetch(:user), roles: %w{web app}, my_property: :my_value
set :application, 'listener'
set :repo_url, 'git@github.com:huuep/listener2.git'
set :branch, 'listener-master'
set :deploy_to, "/home/mcdeploy/listener"
set :daemon_conf_dir, "#{fetch(:deploy_to)}/shared/daemon_conf"
set :bitcoin_dir,   -> { "/home/#{fetch(:user)}/.bitcoin" }
set :bitcoin_bin,   -> { "/usr/local/bin/bitcoind" }
set :bitcoin_pid,   -> { "#{fetch(:bitcoin_dir)}/bitcoind.pid" }
set :bitcoin_conf,  -> { "#{fetch(:bitcoin_dir)}/bitcoin.conf" }
set :redis_conf,    -> { "/etc/redis/redis.conf" } 
set :redis_conf_bak,-> { "/etc/redis/redis.conf.bak" }

namespace :deploy do
  after :starting, :setup_listener do
    on roles(:web) do
      invoke "listener:setup"
    end
  end

  after :published, :install_bitcoind do
    on roles(:app) do
      invoke "listener:install_bitcoind"
    end
  end
end
