#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

from flask.ext import wtf
import wtforms


class RequestPullForm(wtf.Form):
    ''' Form to create a request pull. '''
    title = wtforms.TextField(
        'Title<span class="error">*</span>',
        [wtforms.validators.Required()]
    )


class AddPullRequestCommentForm(wtf.Form):
    ''' Form to add a comment to a pull-request. '''
    commit = wtforms.HiddenField('commit identifier')
    row = wtforms.HiddenField('row')
    requestid = wtforms.HiddenField('requestid')
    comment = wtforms.TextAreaField(
        'Comment<span class="error">*</span>',
        [wtforms.validators.Required()]
    )
