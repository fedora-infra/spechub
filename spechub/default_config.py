#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import os
from datetime import timedelta


# Set the time after which the session expires
PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

# secret key used to generate unique csrf token
SECRET_KEY = '<insert here your own key>'

# url to the database server:
DB_URL = 'sqlite:////var/tmp/spechub.sqlite'

# The FAS group in which the admin of spechub are
ADMIN_GROUP = 'sysadmin-main'

# The email address to which the flask.log will send the errors (tracebacks)
EMAIL_ERROR = 'pingou@pingoured.fr'

# The URL at which the project is available.
APP_URL = 'https://fedorahosted.org/spechub/'

# The URL to use to clone the git repositories.
GIT_URL_SSH = 'git@pkgs.fedoraproject.org'
GIT_URL_GIT = 'git://pkgs.fedoraproject.org'


# Number of items displayed per page
ITEM_PER_PAGE = 120

# Folder containing to the git repos
GIT_FOLDER = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'repos'
)

# Folder containing the forks repos
FORK_FOLDER = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'forks'
)
