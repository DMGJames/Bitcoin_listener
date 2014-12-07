set :server, '54.179.183.108'

set :user, 'mcdeploy'
role :app, [fetch(:user) + "@" + fetch(:server)]
role :web, [fetch(:user) + "@" + fetch(:server)]
role :db,  [fetch(:user) + "@" + fetch(:server)]
server fetch(:server), user: fetch(:user), roles: %w{web app}, my_property: :my_value
set :repo_url, 'git@github.com:huuep/listener_pusher.git'
set :branch, 'master'
set :deploy_to, "/home/mcdeploy/listener_pusher"
set :daemon_conf_dir, "#{fetch(:deploy_to)}/shared/daemon_conf"

set :application, 'listener_pusher'

namespace :deploy do
  after :published, :install_daemon do
    on roles(:app) do
      invoke("listener_pusher:setup")
    end
  end
end

