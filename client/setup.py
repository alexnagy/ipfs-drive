from distutils.core import setup
import py2exe
import sys
sys.setrecursionlimit(5000)

setup(console=['main.py'], requires=['ipfshttpclient'])