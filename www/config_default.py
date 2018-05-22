#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Default configurations.
"""

__author__ = 'Jiaji Xu'

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'password123456',
        'db': 'awesome'
    },
    'session': {
        'secret': 'Awesome'
    }
}