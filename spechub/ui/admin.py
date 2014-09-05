#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

from functools import wraps

import flask

import spechub.lib
from spechub import (APP, SESSION, LOG, cla_required, authenticated,
                    is_admin)


def admin_required(function):
    """ Flask decorator to retrict access to admins of spechub.
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        """ Decorated function, actually does the work. """
        if not authenticated():
            return flask.redirect(
                flask.url_for('auth_login', next=flask.request.url))
        elif not is_admin():
            flask.flash('Access restricted', 'error')
            return flask.redirect(flask.url_for('.index'))
        return function(*args, **kwargs)
    return decorated_function


### Application


@APP.route('/admin')
@admin_required
def admin_index():
    """ Front page of the admin section of the application.
    """
    forks = spechub.lib.get_all_forks(SESSION)

    return flask.render_template(
        'admin_index.html',
        forks=forks,
    )


@APP.route('/admin/gitolite/conf')
def gitolite_conf():
    """ Display the configuration file for gitolite
    """
    forks = spechub.lib.get_all_forks(SESSION)

    return flask.Response(
        flask.render_template(
            'gitolite.html',
            forks=forks,
        ),
        mimetype="text/plain",
    )


@APP.route('/admin/delete', methods=["POST"])
@admin_required
def admin_delete_project():
    """ Delete a specified project.
    """

    forkname = flask.request.form.get('project', None)

    if not forkname or not '/' in forkname:
        flask.flash('Invalid format, should be <user>/<project>', 'error')
        return flask.redirect(flask.url_for('admin_index'))

    user, project = forkname.split('/', 1)

    fork = spechub.lib.get_fork(SESSION, user, project)
    if not fork:
        flask.flash('Could not find fork %s' % forkname, 'error')
        return flask.redirect(flask.url_for('admin_index'))

    try:
        output = spechub.lib.delete_fork(
            SESSION, fork, APP.config['FORK_FOLDER'])
        flask.flash(output)
    except spechub.exceptions.SpecHubException, err:
        flask.flash(str(err), 'error')

    return flask.redirect(flask.url_for('admin_index'))
