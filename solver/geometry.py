class Point:
    pos = None

    def __init__(self, pos):
        self.pos = pos

    def __repr__(self):
        return f"Point({self.pos[0]}, {self.pos[1]})"
