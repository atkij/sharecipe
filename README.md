# Sharecipe
An online recipe sharing website

> **Note:**
> There are no release yet, so to get a wheel: clone the repository; create virtual environment with `python3 -m venv venv`; activate and install dependencies; execute `python3 -m build` to get wheel in `dist` folder.

## Requirements
* python3
* nginx

## Installation

1. Create a folder named `sharecipe-deploy` in your home folder.
2. Create a python virtual environment with `python3 -m venv venv` and activate with `. venv/bin/activate`.  Download latest wheel release to folder and install with `pip install sharecipe-x.x.x-py2.py3-none-any.whl`.
3. Execute `flask --app sharecipe init-db` to initialise database.
4. Create the following files on your system: `/etc/systemd/system/sharecipe.service`, `/etc/systemd/system/sharecipe.socket` and `/etc/nginx/sites-available/sharecipe`.  If you are running a different version of python, ensure you change `python3.9` in the nginx config to your version.
    ```service
    [Unit]
    Description=sharecipe gunicorn daemon
    Requires=sharecipe.socket
    After=network.target
    
    [Service]
    Type=notify
    User=<user>
    Group=<user>
    RuntimeDirectory=gunicorn
    WorkingDirectory=/home/<user>/website-deploy/venv
    ExecStart=/home/<user>/sharecipe-deploy/venv gunicorn sharecipe.wsgi
    ExecReload=/bin/kill -s HUP $MAINPID
    KillMode=mixed
    TimeoutStopSec=5
    PrivateTmp=true
    
    [Install]
    WantedBy=multi-user.target
    ```
    ```service
    [Unit]
    Description=sharecipe socket
    
    [Socket]
    ListenStream=/run/sharecipe.sock
    SocketUser=www-data
    
    [Install]
    WantedBy=sockets.target
    ```
    ```nginx
    upstream app_server {
    	server unix:/run/sharecipe.sock fail_timeout=0;
    }
    
    server {
    	listen 80;
    	client_max_body_size 4G;
    
    	server_name _;
    
    	keepalive_timeout 5;
    
    	root /home/<user>/sharecipe-deploy/venv/lib/python3.9/site-packages/website/static;
    
    	location / {
    		try_files $uri @proxy_to_app;
    	}
    
    	location @proxy_to_app {
    		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    		proxy_set_header X-Forwarded-Proto $scheme;
    		proxy_set_header Host $http_host;
    		proxy_redirect off;
    		proxy_pass http://app_server;
    	}
    
    	error_page 500 502 503 504 /500.html;
    	location = /500.html {
    		root /home/<user>/sharecipe-deploy/venv/lib/python3.9/site-packages/website/static;
    	}
    }
    ```
5. Enable the service with `systemctl enable --now sharecipe.service` and restart nginx with `systemctl restart nginx`.
6. View website at [locahost](localhost).
