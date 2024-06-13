import pymunk
from pymunk.vec2d import Vec2d


class Player(pymunk.Body):
    """
    Player avatar.
    """
    def __init__(self):
        super(Player, self).__init__(body_type=pymunk.Body.KINEMATIC)

        self.radius = 25
        self.color = (255, 50, 50, 255)
        self.start_x = 100
        self.start_y = 500
        self.speed = 2.5
        self.friction = 0.5
        self.elasticity = 0.9
        self.shape = pymunk.Circle(self, self.radius)
        self.shape.collision_type = 2
        self.hit_points = 5
        self.score = 0

    def place(self):
        """
        Set the player avatar's color and initial position.
        :return: None
        """
        self.shape.sensor = False
        self.shape.color = self.color
        self.position = self.start_x, self.start_y

    def move(self, dx, dy, max_x, max_y):
        """
        Move the player avatar according to changes in x and y position.
        :param dx: The change in x position
        :param dy: The change in y position
        :param max_x: Maximum x position
        :param max_y: Maximum y position
        :return: None
        """
        self.position += self.speed * Vec2d(dx, dy)

        if self.position.x < 0:
            self.position = Vec2d(max_x, self.position.y)
        elif self.position.x > max_x:
            self.position = Vec2d(0, self.position.y)

        if self.position.y < 0:
            self.position = Vec2d(self.position.x, max_y)
        elif self.position.y > max_y:
            self.position = Vec2d(self.position.x, 0)
