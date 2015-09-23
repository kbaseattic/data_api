Creating a Data API
===================

A guide for the perplexed.

"It is thus necessary to examine all things according to their essence, to infer from every species such true and well established propositions as may assist us in the solution of metaphysical problems." -Maimonides

Overview
--------

The basic procedure for creating a new Data API has 8 steps:

1. Name your API
2. Create a directory
3. Create a Thrift specification of the data API as a service
4. Generate the Thrift client/server stubs
5. Create Python API modules
6. Create test client and server
7. Test!
8. Publish your API

1. Name your API
^^^^^^^^^^^^^^^^^
The name should be short, descriptive, and be composed solely of letters. For the rest of the steps we will use the classic name, "foo". This name will be used several places in the following.

2. Create a directory
^^^^^^^^^^^^^^^^^^^^^
Give the directory the same name, e.g., "foo/"

3. Create a specification
^^^^^^^^^^^^^^^^^^^^^^^^^
This specification should be named after the type, e.g. "foo.thrift". The Thrift "namespace" should also be the same as the name of the API, e.g. "namespace * foo".
 
In this specification, import base definitions from other types, particularly "object.thrift", and define new ones you need. Create a "service { }" section named with the capitalized type followed by API, e.g. "FooAPI". Put methods in this section.

4. Generate stubs
^^^^^^^^^^^^^^^^^
Use the "-out ." option to generate output in the namespaced directory (which is the same as your API name). Then add language output options. For example, for Python stubs: 

   thrift --gen py:new_style -out . object.thrift

5. Create Python API modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create two Python modules in your new directory, called "api" and "impl", e.g. "foo/api.py" and "foo/impl.py".

You can use the examples from "object/api.py" and "object/impl.py" as a starting point. Basically, you implement the high-level idiomatic API in api.py and then implement the set of functions defined in the Thrift service in impl.py. The class in api.py will take either a client to a remote service or an instance of the implementation in its constructor, depending on whether you want to call locally or not. On the server side, the class defined in impl.py will act as a "handler" of the incoming messages.

6. Create test client/server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TBD

7. Test!
^^^^^^^^
TBD

8. Publish your API
^^^^^^^^^^^^^^^^^^^
TBD