#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""


import json
import os
import shutil
import tempfile
import uuid

import sqlalchemy
from datetime import timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError

import pygit2

import spechub.exceptions
from spechub import model


def create_session(db_url, debug=False, pool_recycle=3600):
    ''' Create the Session object to use to query the database.

    :arg db_url: URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg debug: a boolean specifying wether we should have the verbose
        output of sqlalchemy or not.
    :return a Session that can be used to query the database.

    '''
    engine = sqlalchemy.create_engine(
        db_url, echo=debug, pool_recycle=pool_recycle)
    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession


def add_pull_request_comment(session, request, commit, row, comment, user):
    ''' Add a comment to a pull-request. '''
    user_obj = get_user(session, user)
    if not user_obj:
        user_obj = get_user_by_email(session, user)

    if not user_obj:
        raise spechub.exceptions.SpecHubException(
            'No user "%s" found' % user
        )

    pr_comment = model.PullRequestComment(
        pull_request_id=request.id,
        commit_id=commit,
        line=row,
        comment=comment,
        user_id=user_obj.id,
    )
    session.add(pr_comment)
    # Make sure we won't have SQLAlchemy error before we create the repo
    session.flush()

    return 'Comment added'


def new_pull_request(
        session, repo, repo_from, title, user, stop_id, start_id=None):
    ''' Create a new pull request on the specified repo. '''
    user_obj = session.query(model.User).filter(user==user).first()

    if not user_obj:
        raise spechub.exceptions.SpecHubException(
            'No user "%s" found' % user
        )

    request = model.PullRequest(
        project_id=repo.id,
        project_id_from=repo_from.id,
        title=title,
        start_id=start_id,
        stop_id=stop_id,
        user_id=user_obj.id,
    )
    session.add(request)
    # Make sure we won't have SQLAlchemy error before we create the request
    session.flush()

    global_id = model.GlobalId(
        project_id=repo.id,
        request_id=request.id,
    )

    session.add(global_id)
    session.flush()

    return 'Request created'


def fork_project(session, user, repo, gitfolder, forkfolder):
    ''' Fork a given project into the user's forks. '''

    reponame = os.path.join(gitfolder, repo + '.git')
    forkreponame = '%s.git' % os.path.join(forkfolder, user, repo)

    if os.path.exists(forkreponame):
        raise spechub.exceptions.RepoExistsException(
            'Repo "%s/%s" already exists' % (user, repo))

    if not user:
        raise spechub.exceptions.SpecHubException(
            'No user "%s" found' % user
        )

    user = model.User.get_or_create(session, user)

    project = model.Fork(
        name=repo,
        user=user,
    )
    session.add(project)
    # Make sure we won't have SQLAlchemy error before we create the repo
    session.flush()

    pygit2.clone_repository(reponame, forkreponame, bare=True)

    return 'Repo "%s" cloned to "%s/%s"' % (repo, user, repo)


def get_pull_requests(
        session, project_id=None, project_id_from=None, status=None):
    ''' Retrieve the specified issue
    '''

    query = session.query(
        model.PullRequest,
    ).order_by(
        model.PullRequest.id
    )

    if project_id:
        query = query.filter(
            model.PullRequest.project_id == project_id
        )

    if project_id_from:
        query = query.filter(
            model.PullRequest.project_id_from == project_id_from
        )

    if status is not None:
        query = query.filter(
            model.PullRequest.status == status
        )

    return query.all()


def get_pull_request(session, requestid, project=None):
    ''' Retrieve the specified issue
    '''

    query = session.query(
        model.PullRequest
    ).filter(
        model.PullRequest.project_id == model.Fork.id
    ).filter(
        model.PullRequest.id == requestid
    ).filter(
        model.Fork.name == project
    ).order_by(
        model.PullRequest.id
    )

    return query.first()


def close_pull_request(session, request):
    ''' Close the provided pull-request.
    '''
    request.status = False
    session.add(request)
    session.flush()


def get_forks(session, project, user=None):
    ''' Retrieve the forks of a project
    '''

    query = session.query(
        model.Fork
    ).filter(
        model.Fork.name == project
    ).order_by(
        model.Fork.date_created
    )

    if user:
        query = query.filter(
            model.Fork.user_id == model.User.id
        ).filter(
            model.User.user == None
        )

    return query.all()
