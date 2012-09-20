#!/usr/bin/env python

from distutils.core import setup
import subprocess

subprocess.Popen('cp qa.py qa',shell=True)
setup(scripts=['qa'])
subprocess.Popen('rm qa',shell=True)

