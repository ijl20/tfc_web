SmartCambridge Program API
==========================

The 'Program API' is a [Django Rest Framework](http://www.django-rest-framework.org/)-based interface to
current and archived SmartCambridge data. This compliments the
'[Download API](download_api.md)' which provides efficient download access
to potentially large amounts of archived SmartCambridge data as compressed
CSV files.

Public documentation about the Program API is at https://smartcambridge.org/api/program/

Layout
======

The API provides functionality in the `aq`, `parking`, `traffic` and
`transport` applications of the SmartCambridge Django site. For each
of these the functionality is implemented by files in an 'api' directory
within the application:

```
tfc_web
├── aq
│   ├── ...
│   └── api
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── parking
│   ├── ...
│   └── api
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── traffic
│   ├── ...
│   └── api
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
└── transport
    ├── ...
    └── api
        ├── serializers.py
        ├── urls.py
        └── views.py
```

The `api` application provides functionality common to all API components:

```
tfc_web
└── api
    ├── apps.py
    ├── auth.py
    ├── auth_urls.py
    ├── templates
    │   └── api
    │       ├── ...
    │       ├── base.html
    │       ├── index.html
    │       └── program_api.html
    ├── tests
    │   ├── data
    │   │   ├── README_test_data.md
    │   │   └── ...
    │   ├── setup_env
    │   └── test_api.py
    ├── urls.py
    ├── util.py
    └── views.py
```

The `authmultitoken` and `smartcambridge` applications provide the token authentication scheme used
to identify API users and the the `smartcambridge_user` user class:

```
tfc_web
│
├── authmultitoken
│   ├── LICENSE.md
│   ├── README.md
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py
│   ├── endpoint_urls.py
│   ├── html_urls.py
│   ├── management
│   │   └── commands
│   │       ├── add_restriction.py
│   │       ├── create_multitoken.py
│   │       ├── delete_multitoken.py
│   │       ├── delete_restriction.py
│   │       └── list_multitoken.py
│   ├── migrations
│   │   └── ...
│   ├── models.py
│   ├── serializers.py
│   ├── templates
│   │   └── authmultitoken
│   │       ├── new_token.html
│   │       ├── token_created.html
│   │       ├── token_list.html
│   │       └── token_management.html
│   └── views.py
└── smartcambridge
    ├── admin.py
    ├── admin_email.py
    ├── apps.py
    ├── decorator.py
    ├── migrations
    │   └── ...
    ├── models.py
    ├── templates
    │   └── smartcambridge
    │       └── tcs.html
    ├── urls.py
    └── views.py
```

Implementation
==============

`aq`, `parking`, `traffic` and `transport`
------------------------------------------

The 4 applications `aq`, `parking`, `traffic` and `transport` implement
their API endpoints in their `views.py` files and bind these to URLs in
their `urls.py`. The corresponding `serializers.py` files define the rules by
which internal Python representations of the data is converted
to serialized formats such as JSON.

`aq`, `parking`, `traffic` all follow a common pattern. Their views are
all class-based views inheriting from `api.auth.AuthenticateddAPIView`.
This inherits from
`rest_framework.views.APIView` and applies authentication, authorisation
and throttling and implements usage logging. `get()` methods in the various classes read JSON data
directly out of the file system using helper methods in `api.util`
and rely on the serializer classes to perform data manipulation (choosing
which fields to include, renaming fields, deriving new fields form
existing ones, etc.).

The API for the `transport` application is rather different, partly
because much of its data comes from the database rather than from the filing
system. It uses a combination of ordinary procedural views and
class-based views based on classes from `rest_framework.generics`. For
procedural views, authentication, authorisation and throttling are
implemented using decorators; for the class-based views this is done by
assigning to the class variables `authentication_classes`,
`permission_classes` and `throttle_classes`. These are all set using
the same variables exported by `api.auth` which are used inside
`api.auth.AuthenticateddAPIView` resulting in consistent behaviour across
the API. There is no usage logging in `transport` - see [tfc_web#232](https://github.com/SmartCambridge/tfc_web/issues/232).

A schema and documentation for API endpoints are automatically generated by the
`rest_framework.documentation` package based on the docstrings and values of the
`schema` class variables in class-based views, and on the docstrings and
`schema` decorator for procedural views.

`api`
-----

The `api` application pulls the individual API components together and
exposes their URLs by including their URL definitions in its `urls.py` file.
It provides the templates pages for the `api/` section of the web page
and drives schema and documentation generation via the `rest_framework.documentation`
package. It also provides a home for the `api.auth` and `api.util` packages,
and provides functionality used by the '[Download API](download_api.md)'.

The `api` application also contains a small amount of data for testing
the API - see its [README_test_data.md](tfc_web/api/tests/data/README_test_data.md)
for more details. A partial unit test script for the API exists in `tfc_web/api/tests/test_api.py`.

`authmultitoken`
----------------

`authmultitoken` is a 'stand alone' [Django Rest Framework](http://www.django-rest-framework.org/)
[Authentication class](http://www.django-rest-framework.org/api-guide/authentication/)
supporting a token-based authentication scheme which is one of those
allowed by `api.auth.default_authentication`. See [its README.md](tfc_web/authmultitoken/README.md)
for further details.

`smartcambridge`
----------------

The 'smartcambridge' app provides the `smartcambridge_valid_user` decorator and related
scaffolding that extends Django user management to ensure that users have provided
additional information and accepted the SmartCambridge Terms and Conditions
before accessing the API.

Adding a new data source
========================

Assuming the new data source stores data in the file system like `aq`, `parking`,
`traffic` then the following should be sufficient to add it:

1. Create `tfc_web/<datasource>/api/serializers.py` to map the data into how it will be returned

2. Create `tfc_web/<datasource>/api/views.py` implementing the API endpoints you
    want to provide. Be careful to implement authentication, authorisation and throttling
    by inheriting from `api.auth.AuthenticateddAPIView` or otherwise. Include
    docstrings and schema information for the documentation.

3. Create `tfc_web/<datasource>/api/urls.py` to map API endpoint URLs onto the views.

4. Include your URL patterns in `tfc_web/api/urls.py`, both in `docpatterns` so that
    documentation gets generated for the endpoints and in `urlpatterns` so that
    incomming requests get routed to them.

5. Add test for the new endpoints to `tfc_web/api/tests/test_api.py`

6. Update `tfc_web/api/remplates/api/index.html` to list the data source.