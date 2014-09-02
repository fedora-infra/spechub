#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

__requires__ = ['SQLAlchemy >= 0.8', 'jinja2 >= 2.4']
import pkg_resources

import datetime
import logging

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import relation

BASE = declarative_base()

ERROR_LOG = logging.getLogger('spechub.model')


def create_tables(db_url, alembic_ini=None, debug=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
        information with regards to the database engine, the host to
        connect to, the user and password and the database name.
          ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg alembic_ini, path to the alembic ini file. This is necessary
        to be able to use alembic correctly, but not for the unit-tests.
    :kwarg debug, a boolean specifying wether we should have the verbose
        output of sqlalchemy or not.
    :return a session that can be used to query the database.

    """
    engine = create_engine(db_url, echo=debug)
    BASE.metadata.create_all(engine)
    if db_url.startswith('sqlite:'):
        ## Ignore the warning about con_record
        # pylint: disable=W0613
        def _fk_pragma_on_connect(dbapi_con, con_record):
            ''' Tries to enforce referential constraints on sqlite. '''
            dbapi_con.execute('pragma foreign_keys=ON')
        sa.event.listen(engine, 'connect', _fk_pragma_on_connect)

    if alembic_ini is not None:  # pragma: no cover
        # then, load the Alembic configuration and generate the
        # version table, "stamping" it with the most recent rev:

        ## Ignore the warning missing alembic
        # pylint: disable=F0401
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config(alembic_ini)
        command.stamp(alembic_cfg, "head")

    scopedsession = scoped_session(sessionmaker(bind=engine))
    # Insert the default data into the db
    try:
        create_default_status(scopedsession)
    except SQLAlchemyError:
        pass
    return scopedsession


def create_default_status(session):
    """ Insert the defaults status in the status tables.
    """

    for status in ['Open', 'Invalid', 'Merged', 'Rejected']:
        pr_stat = StatusPullRequest(status=status)
        session.add(pr_stat)
        try:
            session.flush()
        except SQLAlchemyError, err:
            ERROR_LOG.debug('P-R Status %s could not be added', status)

    session.commit()


class StatusPullRequest(BASE):
    """ Stores the status a ticket can have.

    Table -- status_pull_request
    """
    __tablename__ = 'status_pull_request'

    id = sa.Column(sa.Integer, primary_key=True)
    status = sa.Column(sa.Text, nullable=False, unique=True)


class Project(BASE):
    """ Stores the projects.

    Table -- projects
    """

    __tablename__ = 'projects'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(32), nullable=False, index=True)

    date_created = sa.Column(sa.DateTime, nullable=False,
                             default=datetime.datetime.utcnow)

    @property
    def path(self):
        ''' Return the name of the git repo on the filesystem. '''
        if self.parent_id:
            path = '%s/%s.git' % (self.user.user, self.name)
        else:
            path = '%s.git' % (self.name)
        return path

    @property
    def is_fork(self):
        ''' Return a boolean specifying if the project is a fork or not '''
        return self.parent_id is not None

    @property
    def fullname(self):
        ''' Return the name of the git repo as user/project if it is a
        project forked, otherwise it returns the project name.
        '''
        str_name = self.name
        if self.parent_id:
            str_name = "%s/%s" % (self.user.user, str_name)
        return str_name


class User(BASE):
    """ Stores information about users.

    Table -- users
    """

    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    user = sa.Column(sa.String(32), nullable=False, unique=True, index=True)


class PullRequest(BASE):
    """ Stores the pull requests created on a project.

    Table -- pull_requests
    """

    __tablename__ = 'pull_requests'

    id = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'projects.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    project_id_from = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'projects.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    title = sa.Column(
        sa.Text,
        nullable=False)
    start_id = sa.Column(
        sa.String(40),
        nullable=True)
    stop_id = sa.Column(
        sa.String(40),
        nullable=False)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('users.id', onupdate='CASCADE'),
        nullable=False,
        index=True)
    status = sa.Column(sa.Boolean, nullable=False, default=True)

    date_created = sa.Column(sa.DateTime, nullable=False,
                             default=datetime.datetime.utcnow)

    repo = relation(
        'Project', foreign_keys=[project_id], remote_side=[Project.id],
        backref='requests')
    repo_from = relation(
        'Project', foreign_keys=[project_id_from], remote_side=[Project.id])

    def __repr__(self):
        return 'PullRequest(%s, project:%s, user:%s, title:%s)' % (
            self.id, self.repo.name, self.user.user, self.title
        )


class PullRequestComment(BASE):
    """ Stores the comments made on a pull-request.

    Table -- pull_request_comments
    """

    __tablename__ = 'pull_request_comments'

    id = sa.Column(sa.Integer, primary_key=True)
    pull_request_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'pull_requests.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    commit_id = sa.Column(
        sa.String(40),
        nullable=False,
        index=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('users.id', onupdate='CASCADE'),
        nullable=False,
        index=True)
    line = sa.Column(
        sa.Integer,
        nullable=True)
    comment = sa.Column(
        sa.Text(),
        nullable=False)
    parent_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('pull_request_comments.id', onupdate='CASCADE'),
        nullable=True)

    date_created = sa.Column(sa.DateTime, nullable=False,
                             default=datetime.datetime.utcnow)

    user = relation('User', foreign_keys=[user_id],
                    remote_side=[User.id], backref='pull_request_comments')
    pull_request = relation(
        'PullRequest', foreign_keys=[pull_request_id], remote_side=[PullRequest.id],
        backref='comments')
