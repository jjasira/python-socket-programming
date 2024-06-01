# python-socket-programming
This is a project for a job application

# CONFIGURATION
the default configurations for the server.py and client.py are in the config.ini file. Adjustments should be made there for options such as the REREAD_ON_QUERY and linuxpath.
This can be altered to the user's liking.

# INSTALLATION GUIDE USING systemmd(DAEMON)
Use systemmd to run the script
It should come installed, if not, run the following command

    sudo apt-get install -y systemd

To check which version of systemd you have run:

    systemd --version

sudo nano /etc/systemd/system/myserver.service (name of the service which is myserver in this case)

    [Unit]
    Description=My test service
    After=multi-user.target
    [Service]
    Type=simple
    Restart=always
    ExecStart=/usr/bin/python3 /home/<username>/server.py
    [Install]
    WantedBy=multi-user.target

Insert the username in your OS where <username> is written. The ExecStart flag takes in the command that you want to run. So basically the first argument is the python path (in my case it’s python3) and the second argument is the path to the script that needs to be executed. Restart flag is set to always because I want to restart my service if the server gets restarted

Now we need to reload the daemon.

    sudo systemctl daemon-reload

Let’s enable our service so that it doesn’t get disabled if the server restarts.
    
    sudo systemctl enable myserver.service

And now let’ start our service.

    sudo systemctl start myserver.service


There are several commands you can do to start, stop, restart, and check status.

To stop the service.
    sudo systemctl stop name_of_your_service

To restart.
    sudo systemctl restart name_of_your_service

To check status.
    sudo systemctl status name_of_your_service