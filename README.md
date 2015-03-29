# Django-NestedParams

Django implementation of Rails style nested parameters. This is a
proof-of-concept only at this point. It's had about 10 minutes of
testing and even less thought as to security. Use at your own risk.

# Populating request.PARAMS

This populates `request.PARAMS` with nested parameters in the style
of Ruby on Rails. It uses the following process to merge the various
parameters:

1. Adding either `request.POST` (`multipart/form-data` and
   `application/x-www-form-urlencoded`) or JSON deserialized
   data if the content type is `application/json`.
2. Adding the `request.GET` parameters.
3. Adding the view keyword args. This does not go through
   the nested parameters parsing.

# View Decorator

You can get `request.PARAMS` by decorating your view:

```python
from django.utils.decorators import method_decorator
from django_nestedparams.decorators import nestedparams

@nestedparams()
def a_method_view(request, *args, **kwargs):
    # request.PARAMS

class AClassView(object):
    @method_decorator(nestedparams())
    def dispatch(self, request, *args, **kwargs):
        # ... request.PARAMS
```

# Middleware

You can also get `request.PARAMS` by installing it as middleware.
You must do this late in your middleware chain since it accesses
`request.POST`.

```python
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'django_nestedparams.middleware.NestedParamsMiddleware',
)
```

# Security Concerns

IDK. You tell me. This is just a proof of concept.

Ruby on Rails Rack::Utils checks the size of the parameter keyspace.
Django doesn't appear to do this in the QueryDict implementation, so
django-nestedparams doesn't either.

# TODO

* Add unit tests.
* Should freeze the PARAMS dict.
