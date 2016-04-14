.. image:: https://img.shields.io/travis/Nekmo/djangocms-comments.svg?style=flat-square&maxAge=2592000
  :target: https://travis-ci.org/Nekmo/djangocms-comments
  :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/v/djangocms-comments.svg?style=flat-square
  :target: https://pypi.python.org/pypi/djangocms-comments
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/djangocms-comments.svg?style=flat-square
  :target: https://pypi.python.org/pypi/djangocms-comments
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/djangocms-comments.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/djangocms-comments
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/djangocms-comments/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/djangocms-comments
  :alt: Test coverage

DjangoCMS Comments
==================
A comment system for Django CMS unintrusive and easy to use.
Add it to your pages without modifying your models. It is highly customizable!

These are the principles of Django CMS Comments:

- It does not require javascript to work (but it is recommended).
- Almost everything is customizable.
- Anonymous users can post comments.
- It is easy to use and install.
- Comments really are in your website.

Installation
============
You can install DjangoCMS-Comments From **Pypi**::

  pip install djangocms-comments

...Or you can install directly from **source**::

  git clone https://github.com/Nekmo/djangocms-comments.git
  cd djangocms-comments
  python setup.py install

You can also install it from **Aldryn cloud**:
https://marketplace.django-cms.org/en/addons/browse/djangocms-comments/

Configuration
=============
First you need to add ``djangocms_comments`` to your INSTALLED_APPS::

  INSTALLED_APPS = [
      # ...
      'djangocms_comments',
  ]

Now run migrations::

  python manage.py migrate

Add to your urlpatterns::

  urlpatterns = [
      url(r'^djangocms_comments/', include('djangocms_comments.urls')),
  ]

That's all!

Usage
=====
DjangoCMS-Comments includes a plugin. Add the plugin to a page, preferably in a "static placeholder".

The first time you add a plugin, you need to create a new configuration. You can create different configurations
for separate different comments lists on the same page.

**For example, you have a blog with two languages. The posts are translated (the id is the same) and you need separate 
comments. The solution is to create a plugin for each language with a different configuration.**

Comments will be associated to the instance in the page. That instance is necessary.

To make the relationship, DjangoCMS-Comments uses a ``GenericForeignKey``. If the primary key is not an integer, the
relationship will not work! However, this is not usual.

Settings
========
You can overwrite the following options in your settings file:
https://github.com/Nekmo/djangocms-comments/blob/master/djangocms_comments/settings.py

Contribute
==========
Please feel free to send a pull request. All suggestions are welcome.
