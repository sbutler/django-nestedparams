"""
The MIT License (MIT)

Copyright (c) 2015 Stephen J. Butler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Notes
=====================================================================
Parts of this file are adapted from Rack::Utils:

    https://github.com/rack/rack/blob/master/lib/rack/utils.rb
"""
from __future__ import absolute_import, unicode_literals

import json
import re
import six

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.six.moves.urllib.parse import parse_qsl

PARENT_KEY_REGEXP = re.compile(r'[\[\]]*([^\[\]]+)\]*')
CHILD_KEY_1LEVEL_REGEXP = re.compile(r'\[\]\[([^\[\]]+)\]$')
CHILD_KEY_XLEVEL_REGEXP = re.compile(r'\[\](.+)$')


class JSONParsingError(ValueError):
    """
    Exception that is thrown when there is a problem parsing JSON.
    """
    pass


class ParameterTypeError(TypeError):
    """
    ParameterTypeError is the error that is raised when incoming structural
    parameters (parsed by parse_nested_query) contain conflicting types.
    """
    pass


def parse_nested_query(query_string, encoding=None):
    params = {}
    if not query_string:
        return params

    if not encoding:
        encoding = settings.DEFAULT_CHARSET

    if six.PY3:
        if isinstance(query_string, bytes):
            # query_string normally contains URL-encoded data, a subset of ASCII.
            try:
                query_string = query_string.decode(encoding)
            except UnicodeDecodeError:
                # ... but some user agents are misbehaving :-(
                query_string = query_string.decode('iso-8859-1')
        for key, value in parse_qsl(query_string or '',
                                    keep_blank_values=True,
                                    encoding=encoding):
            normalize_params(params, key, value)
    else:
        for key, value in parse_qsl(query_string or '',
                                    keep_blank_values=True):
            key = force_text(key, encoding, errors='replace')
            try:
                value = value.decode(encoding)
            except UnicodeDecodeError:
                value = value.decode('iso-8859-1')

            normalize_params(params, key, value)

    return params


def parse_querydict(querydict, params=None):
    if not params:
        params = {}

    for (key, values) in six.iterlists(querydict):
        for value in values:
            normalize_params(params, key, value)

    return params


def normalize_params(params, name, value=None):
    """
    Recursively expand parameters into structural types. If
    the structural types represented by two different parameter names are in
    conflict, a ParameterTypeError is raised.
    """
    m = PARENT_KEY_REGEXP.match(name)
    if m:
        key = m.group(1)
        after = name[m.end():]

    if not key:
        return

    def _valuelist():
        if not key in params:
            params[key] = []
        elif not isinstance(params[key], list):
            raise ParameterTypeError(
                "expected list (got {0}) for param '{1}'".format(
                    params[key].__class__,
                    key
                )
            )

    if after == "":
        params[key] = value
    elif after == "[":
        params[name] = value
    elif after == "[]":
        _valuelist()
        params[key].append(value)
    else:
        m = CHILD_KEY_1LEVEL_REGEXP.match(after) or CHILD_KEY_XLEVEL_REGEXP.match(after)
        if m:
            _valuelist()
            child_key = m.group(1)
            if isinstance(params[key][-1], (params.__class__, dict)) and not child_key in params[key][-1]:
                normalize_params(params[key][-1], child_key, value)
            else:
                params[key].append(normalize_params(params.__class__(), child_key, value))
        else:
            if not key in params:
                params[key] = params.__class__()
            elif not isinstance(params[key], (params.__class__, dict)):
                raise ParameterTypeError(
                    "expected dict (got {0}) for param '{1}'".format(
                        params[key].__class__,
                        key
                    )
                )

            params[key] = normalize_params(params[key], after, value)

    return params


def process_request(request, view_kwargs):
    """
    Processes the parts of a requiest, returning a params dictionary.
    """
    params = {}

    # Handle POST processing by looking at the POST QueryDict,
    # which should catch multipart/form-data and 
    # application/x-www-form-urlencoded. Then it checks to see
    # if the Content-Type is application/json, and tries to parse
    # that.
    if request.POST:
        params.update(parse_querydict(request.POST))
    elif request.META.get('CONTENT_TYPE', '').startswith('application/json'):
        try:
            params.update(json.loads(request.body, request.encoding))
        except ValueError as valueErr:
            raise JSONParsingError()

    # Handle query string parameters.
    if request.GET:
        params.update(parse_querydict(request.GET))

    # Handle path parameters. These don't really make sense as
    # nester parameters, so don't pass them through.
    if view_kwargs:
        params.update(view_kwargs)

    return params
