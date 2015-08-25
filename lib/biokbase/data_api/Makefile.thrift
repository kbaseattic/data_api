# Makefile for Thrift RPC

default: python

python: python-object

python-object: object.thrift
	thrift --gen py:new_style -out . object.thrift
