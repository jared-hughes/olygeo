"""
Data classes for the geometry Abstract Syntax Tree (AST), where the results
of parsing are stored
"""
from .parser import *

class SentenceList:
    """ A list (tree) of sentences """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s\n%s"%(self.left, self.right)

class Sentence:
    """ A sentence, which may have several statements """
    def __init__(self, things):
        self.things = things

    def __repr__(self):
        return "Sentence\n%s"%(indented(self.things))

class Statement:
    """ A statement, which can contain several relations """
    pass

class ObjectBoolAdj:
    """ A boolean adjective that can apply to a shape """
    def __init__(self, adj):
        self.adj = adj

    def __repr__(self):
        return "BoolAdj[%s]"%self.adj

class AdjectiveList:
    """ A list of adjectives that can apply to a shape """
    def __init__(self, adj_list):
        self.adj_list = adj_list

    def __repr__(self):
        return "AdjList[%s]"%(self.adj_list)

class Relation:
    """
    A relation that specifies a constraint based on several objecs

    e.g. ABC is an acute triangle
    """
    def __init__(self, rel, objects):
        self.rel = rel
        self.objects = objects

    def __repr__(self):
        return "Relation[%s, %s]"%(self.rel, self.objects)

class Verb:
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
        return Relation(self.rel, self.objects + [noun])

class Distance:
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

class ReferenceType:
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

class Segment(ReferenceType):
    """ A segment between two points """
    def __init__(self, point_1, point_2):
        self.point_1 = point_1
        self.point_2 = point_2

    def __repr__(self):
        return "Segment[%s, %s]"%(self.point_1, self.point_2)

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
