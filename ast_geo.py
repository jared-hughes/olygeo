from parser import *

class SentenceList:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s\n%s"%(self.left, self.right)

class Sentence:
    def __init__(self, things):
        self.things = things

    def __repr__(self):
        return "Sentence\n%s"%(indented(self.things))

class Statement:
    pass

class LetStatement(Statement):
    def __init__(self, name, object):
        self.name = name
        self.object = object

    def __repr__(self):
        return "Let[%s, %s]"%(self.name, self.object)

class ObjectBoolAdj:
    def __init__(self, adj):
        self.adj = adj

    def __repr__(self):
        return "BoolAdj[%s]"%self.adj

class AdjectiveList:
    def __init__(self, adj_list):
        self.adj_list = adj_list

    def __repr__(self):
        return "AdjList[%s]"%(self.adj_list)

class Relation:
    """ ABC is an acute triangle """
    def __init__(self, rel, objects):
        self.rel = rel
        self.objects = objects

    def __repr__(self):
        return "Relation[%s, %s]"%(self.rel, self.objects)

class Distance:
    def __init__(self, point_1, point_2):
        self.point_1 = point_1
        self.point_2 = point_2

    def __repr__(self):
        return "Distance[%s, %s]"%(self.point_1, self.point_2)

class CompareRelation(Relation):
    """ e.g. AB=BC, AB=BC=CD """
    def __init__(self, rel, left, right):
        self.rel = rel
        self.left = left
        self.right = right

    def __repr__(self):
        return "Relation[%s %s %s]"%(self.left, self.rel, self.right)

class Construction:
    """ M is the midpoint of BC """
    def __init__(self, rel, from_objects):
        self.rel = rel
        self.from_objects = from_objects

    def __repr__(self):
        return "Construction[%s, %s]"%(self.rel, self.from_objects)

class Reference:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Reference[%s]"%(self.name)

class Point(Reference):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Point[%s]"%(self.name)

class Segment(Reference):
    def __init__(self, point_1, point_2):
        self.point_1 = point_1
        self.point_2 = point_2

    def __repr__(self):
        return "Segment[%s, %s]"%(self.point_1, self.point_2)

class Polygon(Reference):
    def __init__(self, points):
        self.points = points

    def __repr__(self):
        return "Polygon[%s]"%(self.points)

class Object(Reference):
    """ e.g. \\omega """
    pass
