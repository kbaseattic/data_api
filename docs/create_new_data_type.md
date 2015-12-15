# Working with the Data API

Let's say you have a new data type called `Foo`.

## Step 1: Create `FooAPI` class

Create a module for your new data type, e.g. `foo`. 

    mkdir foo
    touch foo/__init__.py


Create an abstract base class, i.e. an interface, with the methods of the API. These methods should return the object itself and be put in a module called `api`, e.g.:

    File `api.py`:
        class FooInterface:
            def get_bar(self, select_param):
                pass
            def get_baz(self, select_param):
                pass

This class inherits from the base `ObjectAPI` and from the abstract base class `AbstractFooAPI`, and also add a constructor that configures the instance to use an appropriate local or remote implementation, as well as an object identifier to choose the exact object to work on.

    Add to file `api.py`:
        from biokbase.data_api import ObjectAPI
        
        ...
        
        class FooAPI(FooInterface, ObjectAPI):
            def __init__(self, which_kbase, object_id):
                ObjectAPI.__init__(self, which_kbase)
            def get_bar(self, select_param):
                pass
            def get_baz(self, select_param):
                pass

## Step 2: Test new FooAPI class

Create a `tests` module and add unit tests for each method in the `FooAPI` class.

## Step 3: Create Thrift definition file for the remote service

Still in the module directory for `foo`, create a `foo.thrift` file that defines operations and structures that are analogous to the FooAPI methods. However, each of these needs to take the object identifier(s) used to initialize the FooAPI in every call, allowing clients to interleave calls for different objects. For example:

    struct ObjectReference { ... }
    struct SelParam { ... }
    struct BarType { ... }
    struct BazType { ... }
    service FooService {
         BarType get_bar(1: ObjectReference, 2: SelParam),
         BazType get_baz(1: ObjectReference, 2: SelParam)
    }
    


## Step 4: