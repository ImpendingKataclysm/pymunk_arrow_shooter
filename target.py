import pymunk


class Target(pymunk.Body):
    """
    Circular falling target.
    """
    def __init__(self):
        super(Target, self).__init__(mass=10)

        self.radius = 25
        self.offset = (0, 0)
        self.shape = pymunk.Circle(self, self.radius, self.offset)
        self.moment = pymunk.moment_for_circle(
            self.mass,
            0,
            self.radius,
            self.offset
        )

        self.shape.collision_type = 0
        self.shape.friction = 0.9
        self.shape.elasticity = 0.95

        self.score_points = 5
