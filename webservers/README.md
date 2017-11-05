# Server configuration

This directory contains the config files for the server. It provides configuration for (i) celery, (ii) redis, (iii) gunicorn and (iv) nginx. All components can and should be run as systemd services. 

## Redis

The message queue is controled by redis which should be run first. Place the file `redis.server` in `/etc/systemd/system/` and run `sudo systemctl start redis`. Check its status with `systemctl status redis` to see if it's running.

## Celery

Next in line are the celery workers. For this we first copy the ennvironment config file `celeryd` to `/etc/default`. Next, we put `celery.service` in `/etc/systemd/system/` and start it using `sudo systemctl start celery`. Note that this might take a while, since we're **not** using concurrency by 14 different nodes. 

For monitoring the celery jobs, set up flower using `flower -A app.celery --prefix_url=flower`. View it at [https://asibot.nl/flower/](https://asibot.nl/flower/).

## Gunicorn

To launch the webservers, we first move the `weasimov.target` file and the `weasimov@.service` file to `/etc/systemd/system/`. Next, start the target file using `sudo systemctl start weasimov.target`. To launch different servers, we employ the template mechanism offered by systemd. For example, to start a server at port 5000, we execute: `sudo systemctl start weasimov@5000`. Do this for all servers listed in `/etc/nginx/sites-available/asibot`, i.e. 5000:5009.

## Nginx

Nginx is started and restarted with: `sudo systemctl start nginx`. 