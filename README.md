My useful website

PERMISSIONS
All permissions are stored as a 64 bit integer.  Each permission for a section of the website consists of 2 bits.  The 2 bits correspond to read and write.  This means that 32 permissions can be stored for the whole website in one number.

FEDCBAzyxwvutsrqponmlkjihgfedcba

0 a = whole website (read access means can log in) (write access means can change account details (username, password...))
2 b = admin permissions
4 c = minecraft (read is view status) (write is stop start server)

GUNICORN SERVICE THING
move these files to /etc/systemd/system/

gunicorn.service:
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=joel
Group=joel
RuntimeDirectory=gunicorn
WorkingDirectory=/home/joel/website-deploy/venv
ExecStart=/home/joel/website-deploy/venv gunicorn website.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target

gunicorn.socket:
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
