"""
Description language for type semantics.

These are used to construct the type structure descriptions in Avro, Thrift,
or whatever.

They could also be used to generate diagrams (or, in some fancy world, the
other way around).

See the documentation for the module for details.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/7/15'

import json
import pprint

# comma-list
clist = lambda a: ", ".join(a)

def keys_error(missing, extra):
    return "{missing}{plus}{extra}".format(
        missing="missing={}".format(clist(list(missing))) if missing else "",
        extra="extra={}".format(clist(list(extra))) if extra else "",
        plus=" and " if (missing and extra) else "")

class ParseError(Exception):
    pass

class DuplicateTypeError(Exception):
    def __init__(self, name):
        Exception.__init__(self, "Duplicate type '{}'".format(name))

class BaseTypeNotFoundError(Exception):
    def __init__(self, base, derived):
        Exception.__init__(self, "Base type '{}' for '{}' not found".format(
            base, derived))

class Type(object):
    separator = '.'
    req_keywords = {'name', 'statements', 'properties'}
    all_keywords = set(list(req_keywords) + ['description'])

    def __init__(self, spec):
        """Create type from JSON spec.
        """
        self.parse(spec)

    def parse(self, spec):
        self._spec = spec.copy()  # save original
        keys = set(spec.keys())
        if (self.req_keywords - keys) or (keys - self.all_keywords):
            raise ParseError("Bad keys in spec '{}': ".format(spec) +
                             keys_error(self.req_keywords - keys,
                                        keys - self.all_keywords))

        self.extends = None
        self.name = spec['name']
        self.namespace = spec.get('namespace', '')
        if self.namespace:
            self.full_name = self.separator.join([self.namespace, self.name])
        else:
            self.full_name = self.name
        self.description = spec.get('description', '')

        self.statements = []
        for s in spec['statements']:
            st = Statement(self.full_name, s[0], s[1])
            self.statements.append(st)
            if st.predicate == Statement.extends:
                self.extends = st.object

        self.properties = spec['properties']

    def as_json(self, indent=2):
        return json.dumps(self._spec, indent=indent)

    def __str__(self):
        return self.as_json(indent=0)


class Statement(object):
    """Single statement of the form (subject, predicate, object), where
    the subject and object are of :class:`Type` and the predicate is
    a string desribing the association. Just like RDF.
    """
    derived_from = 'derivedFrom'
    agg = 'aggregates'
    extends = 'isSubclassOf'

    def __init__(self, class1, relationship, class2):
        self.subject = class1
        self.predicate = relationship
        self.object = class2

class TypeSystem(object):
    """Multiple types, that may refer to each other by name.
    """
    def __init__(self, namespace=''):
        """Initialize empty container.

        :param namespace: optional default namespace to prepend to the
                          referenced names, unless they are already qualified
        """
        self.types = {}
        if namespace:
            self._ns = lambda s: namespace + Type.separator + s
        else:
            self._ns = lambda s: s

    def add(self, type_):
        """Add a type.

        :param type_: New type to add
        :type type_: Type  # bit repeti-repeti-repeti .. boring.
        :return:
        """
        key = type_.full_name
        if key in self.types:
            raise DuplicateTypeError(key)
        self.types[key] = type_

    def _resolve(self, name):
        """Prepare for serialization."""
        t = self.types[self._ns(name)]

        # add all properties and statements from base classes
        # (assume single-inheritance)
        cur = t
        while cur.extends:
            if not cur.namespace or (Type.separator in cur.extends):
                base_name = cur.extends
            else:
                base_name = Type.separator.join([t.namespace, cur.extends])
            base = self.types.get(base_name, None)
            if base is None:
                raise BaseTypeNotFoundError(base_name, t.full_name)
            # add properties
            for p in base.properties:
                t.properties.append(p) # XXX: same name?
            # add statements
            for s in base.statements:
                t.statements.append(s)
            cur = base # continue with parent

        # TODO: check Types referenced in statements

        return t

    def as_avro(self, name):
        """Create and return avro schema.

         :param name: Name of the schema to create, which should match the
                      name of some type given to `add()`.
        :return: The new avro schema.
        :rtype: dict
        """
        t = self._resolve(name)
        rec = {
            "type": "record",
            "namespace": t.namespace,
            "name": t.name,
            "fields": []
        }

        for p in t.properties:
            rec['fields'].append(p)

        # make an 'somethingId' name from 'something'
        makeid = lambda s: s + 'Id'

        # add FooId:string to the 'provenance' field,
        # for each 'derived-from Foo' in statements
        provenance = []
        for s in t.statements:
            if s.predicate == Statement.derived_from:
                name = makeid(s.object)
                provenance.append({"name": name, "type": "string"})
        rec['fields'].append({
            "type": "record",
            "name": "provenance",
            "fields": provenance
            })

        # add FooId:string to fields for each 'aggregates Foo' in statements
        for s in t.statements:
            if s.predicate == Statement.agg:
                name = makeid(s.object)
                rec['fields'].append({"name": name, "type": "string",
                                      "description": "Dependency"})

        # add all other statements to a generic container
        exclude = (Statement.agg, Statement.derived_from, Statement.extends)
        assoc = []
        for s in t.statements:
            if s.predicate not in exclude:
                assoc.append({"name": s.predicate,
                              "type": {
                                  "type": "array", "items": "string",
                                  "description": "list of " + makeid(s.object)
                              }})
        rec['fields'].append({
            "type": "record",
            "name": "associations",
            "fields": assoc
        })

        return rec

