#!/usr/bin/env python

from distutils.core import setup
import subprocess

subprocess.Popen('cp npu.py npu',shell=True)
setup(scripts=['npu'])
subprocess.Popen('rm npu',shell=True)

