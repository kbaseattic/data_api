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
    """An object describing a single type.
    """
    separator = '.'
    req_keywords = {'name', 'statements', 'properties'}
    all_keywords = set(list(req_keywords) + ['description'])

    def __init__(self, spec):
        """Create type from specification.

        :param spec: Specification, see below
        :type spec: dict

        The specification, a dict that could have been
        parsed directly from a JSON string (so, a dict containing
        only lists, dicts, and JSON scalars):

        .. code-block:: javascript

            {
            // Optional namespace for type name
            "namespace": "kbase.us",
            // Type name using UpperCamelCase convention
            "name": "BananaBunch",
             // Description of what these objects mean
            "description": "A yellow fruit",
            // List of properties, each with name and type.
            // These are the value(s) for your type.
            "properties": [
                {"name": "num", "type": "int"},
                {"name": "color", "type": "string"},
            ],
            // Zero or more statements about the relationship to
            // other types, which are pairs of the form
            // ["relationship", "NameOfType"].
            // The Statements class defines constants, given
            // in comments, for standard relationships.
            // Arbitrary relationships are also possible.
            "statements": [
                ["isSubclassOf", "Fruit"],     // .extends
                ["aggregates", "Banana"],      // .agg
                ["derivedFrom", "BananaTree"], // .derived_from
                ["inAFruitBasketWith", "GrapeBunch"],
            }
        """
        self._parse(spec)

    def _parse(self, spec):
        self._spec = spec.copy()  # save original
        keys = set(spec.keys())
        if (self.req_keywords - keys) or (keys - self.all_keywords):
            raise ParseError("Bad keys in spec '{}': ".format(spec) +
                             keys_error(self.req_keywords - keys,
                                        keys - self.all_keywords))

        self.version = None
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

        # copy properties out of spec to avoid side-effects
        self.properties = spec['properties'][:]

    def as_json(self, indent=2):
        """Return JSON string representation of this type.
        """
        return json.dumps(self._spec, indent=indent)

    def __str__(self):
        return self.as_json(indent=0)


class Statement(object):
    """Single RDF-like triple of the form (subject, predicate, object), where
    the 'subject' and 'object' are both :class:`Type` and the predicate is
    a string desribing the nature of the association.
    """
    derived_from = 'derivedFrom' #: The object is derived from the subject
    agg = 'aggregates'           #: Multiple objects are aggregated in the subject
    extends = 'isSubclassOf'     #: The subject is a sub-class of the object

    def __init__(self, class1, relationship, class2):
        self.subject = class1
        self.predicate = relationship
        self.object = class2

class TypeSystem(object):
    """Multiple types, that may refer to each other by name.

    Importantly, versions are a property of this class, and not of
    individual types.
    """
    def __init__(self, namespace='', version=None):
        """Initialize an empty container.

        :param namespace: optional default namespace to prepend to the
                          referenced names, unless they are already qualified
        :type namespace: str
        """
        self.types = {}
        if namespace:
            self._ns = lambda s: namespace + Type.separator + s
        else:
            self._ns = lambda s: s

    def add(self, type_):
        """Add a type.

        :param type_: New type to add
        :type type_: Type
        :return: None
        """
        key = type_.full_name
        if key in self.types:
            raise DuplicateTypeError(key)
        self.types[key] = type_

    def _resolve(self, name):
        """Prepare for serialization.
        """
        t = self.types[self._ns(name)]
        # avoid modifying shared lists
        t.statements = t.statements[:]
        t.properties = t.properties[:]

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

