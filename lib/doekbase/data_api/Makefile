# Makefile for Thrift RPC

default: python

python: python-object

python-object: baseobj.thrift
	thrift --gen py:new_style -out . $<
