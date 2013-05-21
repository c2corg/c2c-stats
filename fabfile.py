# -*- coding: utf-8 -*- #

import os
from fabric.api import local, task, cd, run, sudo, env

env.hosts = ['c2cstats']
env.use_ssh_config = True


@task
def update():
    "Update the code on the server with git"

    with cd('/usr/src/c2c-stats'):
        sudo('git pull', user='c2corg')
        sudo('service gunicorn restart')


@task
def puppet():
    "Update the config and virtualenv with puppet"
    sudo('puppet agent -t')


@task
def cache():
    "Empty the cache"
    sudo('find /var/lib/c2cstats/cache/ -type f -delete')


@task
def all():
    update()
    puppet()
    cache()
