import json

class MalformedSpecError(Exception):
    pass

def spec_from_json(string):
    dc = json.loads(string)
    return spec_from_dict(dc)

def spec_from_dict(dc):
    if isinstance(dc, list):
        return [spec_from_dict(d) for d in dc]
    elif isinstance(dc, dict):
        dc = {key: spec_from_dict(value) for key, value in dc.items()}
        return spec_types[dc["type"]](**dc)
    else:
        return dc

def try_json(dc, *args, **kwargs):
    try:
        return dc.to_json(*args, **kwargs)
    except:
        return str(dc)

spec_types = {}
""" Map to identify types of specs """

def add_to_spec_types(cls):
    spec_types[cls.type()] = cls
    return cls

class Default:
    def __init__(self, value=None, name=None):
        self.value = value
        self.name = name

    def __rtruediv__(self, name):
        return Default(self.value, name)

class SpecPart:
    """
    Part of a spec, jsonifyable with to_json
    """
    def __init__(self, *args, **kwargs):
        self.attrs = {}
        names = []
        for n in self.attr_names:
            names.append(n if isinstance(n, Default) else Default(name=n))
        for arg in args:
            self.attrs[names.pop(0).name] = arg
        for key, value in kwargs.items():
            for i, name in enumerate(names):
                if name.name == key:
                    self.attrs[name.name] = value
                    names.pop(i)
                    break;
        for name in names:
            self.attrs[name.name] = name.value
        self.attrs["type"] = self.type()

    def __getattr__(self, attr):
        return self.attrs[attr]

    def __eq__(self, other):
        return self.attrs == other.attrs

    def to_dict(self):
        out_dict = {}
        for key, value in self.attrs.items():
            try:
                out_dict[key] = value.to_dict()
            except:
                try:
                    out_dict[key] = list(map(lambda k: k.to_dict(), value))
                except:
                    out_dict[key] = value
        return out_dict

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, **kwargs)

    @classmethod
    def type(cls):
        return cls.__name__

@add_to_spec_types
class Spec(SpecPart):
    """
    Data-class to store a spec
    """
    attr_names = ["params" / Default([]), "constraints" / Default([]), "drawn" / Default([])]

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def add_param(self, param):
        existing = False
        for existing_param in self.params:
            if param.name == existing_param.name:
                existing = True
                if param != existing_param:
                    p1 = try_json(param)
                    p2 = try_json(existing_param)
                    msg = f"Invalid param pair: {p1} and {p2}"
                    raise MalformedSpecError(msg)
        if not existing:
            self.params.append(param)

    def add_drawing(self, drawing):
        self.drawn.append(drawing)

@add_to_spec_types
class ConstructPoint(SpecPart):
    attr_names = ["name"]

@add_to_spec_types
class ConstructSegment(SpecPart):
    attr_names = ["point_1", "point_2"]

@add_to_spec_types
class ParamPoint(SpecPart):
    attr_names = ["name"]

@add_to_spec_types
class ConstrainObjects(SpecPart):
    attr_names = ["constraint_type", "objects"]

@add_to_spec_types
class DrawPoint(SpecPart):
    attr_names = ["point"]

@add_to_spec_types
class DrawSegment(SpecPart):
    attr_names = ["point_1", "point_2"]
