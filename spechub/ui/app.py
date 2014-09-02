#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import flask
import os
import re
from math import ceil

import pygit2
from sqlalchemy.exc import SQLAlchemyError
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.lexers.text import DiffLexer
from pygments.formatters import HtmlFormatter


import spechub.exceptions
import spechub.lib
import spechub.ui.forms
from spechub import (APP, SESSION, LOG, __get_file_in_tree, cla_required,
                    #generate_gitolite_acls, generate_gitolite_key,
                    #generate_authorized_key_file
                    )


def chunks(item_list, chunks_size):
    """ Yield successive n-sized chunks from item_list.
    """
    for i in xrange(0, len(item_list), chunks_size):
        yield item_list[i: i + chunks_size]


### Application


@APP.route('/')
def index():
    """ Front page of the application.
    """
    page = flask.request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    limit = APP.config['ITEM_PER_PAGE']
    start = limit * (page - 1)

    repos = sorted(os.listdir(APP.config['GIT_FOLDER']))[start:(start + limit)]
    repos = [repo.replace('.git', '') for repo in repos]

    num_repos = len(os.listdir(APP.config['GIT_FOLDER']))

    total_page = int(ceil(num_repos / float(limit)))

    return flask.render_template(
        'index.html',
        repos=chunks(repos, 5),
        total_page=total_page,
        page=page,
    )

@APP.route('/search')
@APP.route('/search/<term>')
def search(term='*'):
    """ Search for one or more repos according to the pattern given.
    """
    term = flask.request.args.get('term', term)
    page = flask.request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    pattern = re.compile(term.replace('*', '.*'))

    limit = APP.config['ITEM_PER_PAGE']
    start = limit * (page - 1)

    repos = sorted(os.listdir(APP.config['GIT_FOLDER']))
    repos = [
        repo.replace('.git', '')
        for repo in repos
        if re.match(pattern ,repo)
    ]

    num_repos = len(repos)
    repos = repos[start:(start + limit)]

    total_page = int(ceil(num_repos / float(limit)))

    return flask.render_template(
        'index.html',
        repos=chunks(repos, 5),
        total_page=total_page,
        page=page,
    )
