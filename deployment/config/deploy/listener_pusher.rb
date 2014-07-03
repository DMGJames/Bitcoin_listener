role :app, %w{mcdeploy@54.179.69.232}
role :web, %w{mcdeploy@54.179.69.232}
role :db,  %w{mcdeploy@54.179.69.232}

server '54.179.69.232', user: 'mcdeploy', roles: %w{web app}, my_property: :my_value

set :repo_url, 'git@github.com:huuep/listener_pusher.git'
set :branch, 'master'
set :deploy_to, "/home/mcdeploy/listener_pusher"
set :daemon_conf_dir, "#{fetch(:deploy_to)}/shared/daemon_conf"

set :application, 'listener_pusher'
set :user, "mcdeploy"

namespace :deploy do
  after :published, :install_daemon do
    on roles(:app) do
      invoke("listener_pusher:setup")
    end
  end
end

