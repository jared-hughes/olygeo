"""
Data classes for the geometry Abstract Syntax Tree (AST), where the results
of parsing are stored
"""
from abc import ABC, abstractmethod
import re
from functools import wraps
from .parser import *
from ..backend import spec_geo as sp

def vectorize(func):
    """ Wraper to vectorize over first argument """
    @wraps(func)
    def wrapper_vectorize(x, *args, **kwargs):
        if isinstance(x, list):
            return [func(item, *args, **kwargs) for item in x]
        else:
            return func(x, *args, **kwargs)
    return wrapper_vectorize

@vectorize
def update_spec(ast, spec):
    ast.update_spec(spec)

@vectorize
def get_construction(ast, spec, *args, **kwargs):
    return ast.get_construction(spec, *args, **kwargs)

def also_update_spec(func):
    @wraps(func)
    def wrapper_also_update_spec(*args, uspec=True, **kwargs):
        if uspec:
            update_spec(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper_also_update_spec

class AST:
    def pprint(self):
        """
        Pretty-prints the AST by removing brackets
        """
        s = str(self)
        # put items split by commas onto separate lines
        s = re.sub(",\s?", "\n", s)
        # repeatedly expand brackets
        subs = 1
        bracket_regex = re.compile("\[([^\[\]]*)\],?\s?")
        repl = lambda m: f"\n{indented(m.group(1))}\n"
        while subs > 0:
            s, subs = re.subn(bracket_regex, repl, s)
        # remove unnecessary whitespace
        s = re.sub("\n\s*\n", "\n", s)
        # shift apostrophes left by one, inspired by new ls quoting style
        s = indented(s, amount=1)
        s = s.replace(" '", "'")
        # shift back if no top-level apostrophes
        s = deindented(s, 1, " ")
        print(s)

    def get_spec(self):
        """
        Get the corresponding spec
        """
        spec = sp.Spec()
        update_spec(self, spec)
        return spec

    @abstractmethod
    def __repr__(self):
        pass

class SentenceList(AST):
    """ A list (tree) of sentences """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s\n%s"%(self.left, self.right)

    def update_spec(self, spec):
        update_spec(self.left, spec)
        update_spec(self.right, spec)

class Sentence(AST):
    """ A sentence, which may have several statements """
    def __init__(self, things):
        self.things = things

    def __repr__(self):
        return "Sentence\n%s"%(indented(self.things))

    def update_spec(self, spec):
        update_spec(self.things, spec)

class Statement(AST):
    """ A statement, which can contain several relations """
    pass

class ObjectBoolAdj(AST):
    """ A boolean adjective that can apply to a shape """
    def __init__(self, adj):
        self.adj = adj

    def __repr__(self):
        return "BoolAdj[%s]"%self.adj

class Adjective(AST):
    def __init__(self, rel, objects):
        self.rel = rel
        self.objects = objects

    def __repr__(self):
        return "Adjective[%s, %s]"%(self.rel, self.objects)

    def add_noun(self, noun):
        return Relation(self.rel, [noun] + self.objects)

class AdjectiveList(AST):
    """ A list of adjectives that can apply to a shape """
    def __init__(self, adj_list):
        self.adj_list = adj_list

    def __repr__(self):
        return "AdjList[%s]"%(self.adj_list)

    def add_noun(self, noun):
        rel_list = [adj.add_noun(noun) for adj in self.adj_list]
        return RelationList(rel_list)

class Relation(AST):
    """
    A relation that specifies a constraint based on several objecs

    e.g. ABC is an acute triangle
    """
    def __init__(self, rel, objects):
        self.rel = rel
        self.objects = objects

    def __repr__(self):
        return "Relation[%s, %s]"%(self.rel, self.objects)

    def update_spec(self, spec):
        spec.add_constraint(sp.ConstrainObjects(self.rel, get_construction(self.objects, spec)))

class RelationList(AST):
    def __init__(self, rel_list):
        self.rel_list = rel_list

    def __repr__(self):
        return "RelList[%s]"%(self.rel_list)

    def update_spec(self, spec):
        update_spec(self.rel_list, spec)

class Verb(AST):
    """
    A relation lacking a noun to complete it

    Examples
    ---------
    >>> apply_parser(meets(), "meets $A$ and $B$ at $C$ and $D$").value
    Verb[meets, [Multi[[Reference[Point[A], AdjList[[None]]], Reference[Point[B], AdjList[[None]]]]], Multi[[Point[C], Point[D]]]]]
    """
    def __init__(self, rel, objects):
        self.rel = rel
        self.objects = objects

    def __repr__(self):
        return "Verb[%s, %s]"%(self.rel, self.objects)

    def add_noun(self, noun):
        """ Complete a verb with a noun to get a relation """
        return Relation(self.rel, [noun] + self.objects)

class Distance(AST):
    """ A distance between two points """
    def __init__(self, point_1, point_2):
        self.point_1 = point_1
        self.point_2 = point_2

    def __repr__(self):
        return "Distance[%s, %s]"%(self.point_1, self.point_2)

class CompareRelation(Relation):
    """
    A relation between two objects, usually distances

    Examples
    ---------
    >>> apply_parser(compare_relation(), "$AB<CD=EF$").value
    Relation[Relation[Distance[Point[A], Point[B]] < Distance[Point[C], Point[D]]] = Distance[Point[E], Point[F]]]
    """
    def __init__(self, rel, left, right):
        self.rel = rel
        self.left = left
        self.right = right

    def __repr__(self):
        return "Relation[%s %s %s]"%(self.left, self.rel, self.right)

class Construction(Relation):
    """ ``M`` is the midpoint of ``BC`` """
    def __init__(self, rel, from_objects):
        self.rel = rel
        self.from_objects = from_objects

    def __repr__(self):
        return "Construction[%s, %s]"%(self.rel, self.from_objects)

class ReferenceType(AST):
    """ A reference to an object by name """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ReferenceType[%s]"%(self.name)

class Point(ReferenceType):
    """ A point """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Point[%s]"%(self.name)

    @also_update_spec
    def get_construction(self, spec):
        return sp.ConstructPoint(self.name)

    def update_spec(self, spec):
        spec.add_param(sp.ParamPoint(self.name))
        spec.add_drawing(sp.DrawPoint(self.get_construction(spec, uspec=False)))

class Segment(ReferenceType):
    """ A segment between two points """
    def __init__(self, point_1, point_2):
        self.point_1 = point_1
        self.point_2 = point_2

    def __repr__(self):
        return "Segment[%s, %s]"%(self.point_1, self.point_2)

    @also_update_spec
    def get_construction(self, spec):
        point_1 = get_construction(self.point_1, spec)
        point_2 = get_construction(self.point_2, spec)
        return sp.ConstructSegment(point_1, point_2)

    def update_spec(self, spec):
        point_1 = get_construction(self.point_1, spec)
        point_2 = get_construction(self.point_2, spec)
        spec.add_drawing(sp.DrawSegment(point_1, point_2))

class Polygon(ReferenceType):
    """ A polygon from many points """
    def __init__(self, points):
        self.points = points

    def __repr__(self):
        return "Polygon[%s]"%(self.points)

class Object(ReferenceType):
    r""" An object with a special name such as ``"\\omega"`` """
    pass

class Multi(ReferenceType):
    """
    A set of several objects such as ``"A and B"``

    Operations on ``Multi``-s should vectorize in many cases but have different
    handling methods
    """
    def __init__(self, objects):
        self.objects = objects

    def __repr__(self):
        return "Multi[%s]"%(str(self.objects))

class Reference(Statement):
    """ A reference to an object with an adjective list """
    def __init__(self, ref, adj_list):
        self.ref = ref
        self.adj_list = adj_list

    def __repr__(self):
        return "Reference[%s, %s]"%(self.ref, self.adj_list)

    def get_construction(self, spec):
        self.update_spec(spec)
        return get_construction(self.ref, spec)

    def update_spec(self, spec):
        rel_list = self.adj_list.add_noun(self.ref)
        update_spec(rel_list, spec)
