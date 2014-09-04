#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

from functools import wraps

import flask

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

    return flask.render_template(
        'admin_index.html',
    )
