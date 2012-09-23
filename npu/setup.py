#!/usr/bin/env python

from distutils.core import setup
import subprocess

subprocess.Popen('cp npu.py npu',shell=True)
subprocess.Popen('cp npl.py npl',shell=True)
setup(scripts=['npu','npl'],py_modules=['npu_instructions'])
subprocess.Popen('rm npu npl',shell=True)

