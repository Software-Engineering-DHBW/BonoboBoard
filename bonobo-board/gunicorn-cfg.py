# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

with open("gunicorn.txt", "w+") as fd:
    fd.write("Was in gunicorn-cfg.py")

bind = '0.0.0.0:5005'
workers = 9 #cores*2+1  src: https://docs.gunicorn.org/en/stable/design.html#how-many-workers
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
