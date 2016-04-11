#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_comments')

if __name__ == '__main__':
    run()
