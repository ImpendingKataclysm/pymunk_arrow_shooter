import pymunk
from pymunk.vec2d import Vec2d


class Missile(pymunk.Body):
    """
    Polygonal shape that automatically spawns at the player's location and can
    be fired at targets.
    """
    def __init__(self, position):
        super(Missile, self).__init__(body_type=pymunk.Body.KINEMATIC)

        self.vertices = [(-30, 0), (0, 3), (10, 0), (0, -3)]
        self.position = position

        self.shape = pymunk.Poly(self, self.vertices)
        self.shape.friction = 0.1
        self.shape.collision_type = 1
        self.shape.density = 0.1

    def update_movement(self):
        """
        Move the missile across the screen while it is in flight.
        :return: None
        """
        drag_constant = 0.0002
        point_direction = Vec2d(1, 0).rotated(self.angle)
        flight_direction = Vec2d(*self.velocity)
        flight_direction, flight_speed = flight_direction.normalized_and_length()
        dot = flight_direction.dot(point_direction)
        drag_force = (1 - abs(dot)) * flight_speed ** 2 * drag_constant * self.mass
        impulse = drag_force * flight_direction
        tail_position = self.position + Vec2d(-50, 0).rotated(self.angle)

        self.apply_impulse_at_world_point(
            impulse,
            tail_position
        )

        self.angular_velocity *= 0.5
