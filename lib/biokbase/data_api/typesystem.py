import abc

class AbstractTypeRegistry:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_namespaces(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_types(self, namespace=None):
        raise NotImplementedError
        
    @abc.abstractmethod
    def register_namespace(self, namespace=None):
        raise NotImplementedError

    @abc.abstractmethod
    def update_spec(self, namespace=None, schema=None):
        raise NotImplementedError
    
    @abc.abstractmethod
    def register_spec(self, namespace=None, schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_spec_hash(self, schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_registry_info(self, hash=None):
        raise NotImplementedError


class AbstractTypeNamespaceAPI:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_type_names(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_type(self, type_name=None):
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_type(self, type_schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_type(self, type_schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def update_type(self, type_name=None, type_schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def publish_type(self, type_name=None):
        raise NotImplementedError

    @abc.abstractmethod
    def unpublish_type(self, type_name=None):
        raise NotImplementedError

    @abc.abstractmethod
    def add_user(self, type_schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def update_user(self, type_schema=None):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_user(self, type_schema=None):
        raise NotImplementedError


class AbstractTypeAPI:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_schema(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set_schema(self, schema=None):
        raise NotImplementedError
    
    @abc.abstractmethod
    def validate_schema(self, schema=None):
        raise NotImplementedError
