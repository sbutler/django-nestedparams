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
"""
from __future__ import absolute_import, unicode_literals

import json

from django.http import HttpResponseBadRequest

from .parser import JSONParsingError, ParameterTypeError, process_request


class NestedParamsMiddleware(object):
    """
    This will add a PARAMS object to the request before calling
    the view function. This does it by:

    1. Adding either request.POST (multipart/form-data and
       application/x-www-form-urlencoded) or JSON deserialized
       data if the content type is application/json.
    2. Adding the request.GET parameters.
    3. Adding the view keyword args. This does not go through
       the nested parameters parsing.

    This should be added very late in the middleware list since
    it will trigger request.POST processing.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            request.PARAMS = process_request(request, view_kwargs)

        except JSONParsingError as jsonParseErr:
            return HttpResponseBadRequest()

        except ParameterTypeError as paramTypeErr:
            return HttpResponseBadRequest()

        else:
            # Continue procesing
            return None
