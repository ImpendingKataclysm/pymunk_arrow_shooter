import random

import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d

from typing import Optional, List

from gui import Interface
from player import Player
from missile import Missile
from target import Target


class App:
    """
    Pymunk target shooting simulation.
    """
    def __init__(self):
        pygame.init()

        self.running: bool = False
        self.playing: bool = False

        self.fps: float = 0
        self.start_time: float = 0

        self.space = pymunk.Space()

        self.gui = Interface(self.space)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.gui.screen)

        self.player: Optional[Player] = None
        self.missile: Optional[Missile] = None

        self.flying_missiles: List[Missile] = []
        self.targets: List[Target] = []

        self.ticks_to_next_target = 5

        self.line_start_point: Optional[Vec2d] = None

    def setup(self):
        """
        Sets up the game's starting state.
        :return: None
        """
        self.running = True
        self.playing = True

        self.fps = 0
        self.start_time = 0

        self.space.gravity = (0, 100)

        self.player = Player()
        self.player.place()
        self.space.add(self.player, self.player.shape)

        self.missile = Missile(self.player.position)
        self.space.add(self.missile, self.missile.shape)

        self.flying_missiles = []

    def run(self):
        """
        Update the screen and the physics engine.
        :return: None
        """
        left_mouse_press = 0

        self.add_collision_handlers()

        while self.running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            self.handle_quit_event(events, keys)

            if not self.playing:
                continue

            self.handle_mouse_event(events)
            self.handle_key_input(keys)
            self.aim()
            self.update_targets()

            for missile in self.flying_missiles:
                missile.update_movement()

                if missile.position.y >= self.gui.screen_height:
                    self.flying_missiles.remove(missile)

            self.gui.clear()
            self.space.debug_draw(self.draw_options)

            if pygame.mouse.get_pressed()[left_mouse_press]:
                self.show_power_meter()

            self.gui.show_gui_data(self.player.score, self.player.hit_points)

            if self.line_start_point is not None:
                self.start_drawing_wall()

            pygame.display.flip()

            self.fps = 60
            self.space.step(1.0 / self.fps)
            self.gui.clock.tick(self.fps)

    def start_drawing_wall(self):
        """
        Start drawing a line segment between the current line start point and
        the current mouse position.
        :return: None
        """
        point_a = (int(self.line_start_point.x), int(self.line_start_point.y))
        point_b = pymunk.pygame_util.from_pygame(
            Vec2d(*pygame.mouse.get_pos()),
            self.gui.screen
        )

        pygame.draw.lines(
            self.gui.screen,
            pygame.Color('black'),
            False,
            [point_a, point_b]
        )

    def finish_drawing_wall(self, end_point):
        """
        Draw a line segment between the current line start point and the given
        end point
        :param end_point: The point at which to end the line segment
        :return: None
        """
        wall = pymunk.Segment(
            self.space.static_body,
            self.line_start_point,
            end_point,
            radius=0.0
        )

        wall.friction = 0.99

        self.space.add(wall)

    def add_collision_handlers(self):
        """
        Define handlers for collisions between different shapes:
        - Missile colliding with a Target
        - Target colliding with the Player
        :return: None
        """
        collision_type_target = 0
        collision_type_missile = 1
        collision_type_player = 2

        missile_hit_handler = self.space.add_collision_handler(
            collision_type_target,
            collision_type_missile
        )

        missile_hit_handler.post_solve = self.post_solve_missile_hit

        player_hit_handler = self.space.add_collision_handler(
            collision_type_player,
            collision_type_target
        )

        player_hit_handler.post_solve = self.post_solve_player_hit

    def handle_quit_event(self, events, keys):
        """
        Stop running the game if the player clicks the 'X' button or presses 'Q'
        or 'Esc'.
        :param events: Pygame events currently occurring.
        :param keys: Keys currently pressed.
        :return: None
        """
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False

        if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
            self.running = False

    def handle_mouse_event(self, events):
        """
        Handle events triggered by mouse inputs. Charge and fire the arrow when
        the user presses and releases the left mouse button.
        :param events: Pygame events currently occurring
        :return: None
        """
        left_click_event = 1
        right_click_event = 3

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == left_click_event:
                    self.start_time = pygame.time.get_ticks()
                elif (
                    e.button == right_click_event
                    and self.line_start_point is None
                ):
                    self.line_start_point = Vec2d(*e.pos)
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == left_click_event:
                    self.fire()
                    self.missile = Missile(self.player.position)
                    self.space.add(self.missile, self.missile.shape)
                elif (
                    e.button == right_click_event
                    and self.line_start_point is not None
                ):
                    self.finish_drawing_wall(e.pos)
                    self.line_start_point = None

    def post_solve_missile_hit(self, arbiter, space, data):
        """
        Handles a collision between a missile and a target by calling a callback
        function.
        :param arbiter: Pymunk Arbiter that contains the colliding shapes
        :param space: Pymunk Space in which the collision is taking place
        :param data: Additional arguments required by the callback
        :return: None
        """
        impulse_len = 300

        if arbiter.total_impulse.length > impulse_len:
            target, missile = arbiter.shapes
            missile.collision_type = 0
            missile.group = 1
            target_body = target.body
            missile_body = missile.body

            self.space.add_post_step_callback(
                self.hit_target,
                missile_body,
                target_body,
                target
            )

    def hit_target(self, space, missile_body, target_body, target_shape):
        """
        Called when a missile hits a target. Increments the player's score by
        the target's points value and removes the target and the missile.
        :param space: The space in which the collision occurs.
        :param missile_body: Missile hitting the Target
        :param target_body: Target hit by the Missile
        :param target_shape: Shape of the Target
        :return: None
        """
        if target_body in self.targets:
            self.player.score += target_body.score_points

        if missile_body in self.flying_missiles:
            self.flying_missiles.remove(missile_body)
            self.space.remove(missile_body, missile_body.shape)

        if target_shape in space.shapes and target_body in space.bodies:
            self.space.remove(target_shape)
            self.space.remove(target_body)

    def post_solve_player_hit(self, arbiter, space, data):
        """
        Handles a collision between the player and a target.
        :param arbiter: Pymunk Arbiter containing the colliding shapes
        :param space: Pymunk Space in which the collision occurs
        :param data: Additional data for the callback
        :return: None
        """
        player, target = arbiter.shapes
        player_body = player.body
        target_body = target.body

        self.space.add_post_step_callback(
            self.hit_player,
            target_body,
            player_body
        )

    def hit_player(self, space, target, player):
        """
        Called when a target hits the player. Removes the target and reduces
        the player's hit points by the target's damage points. The game ends if
        the player's HP reaches zero.
        :param space: Pymunk Space in which the collision occurs
        :param target: Target that hits the player
        :param player: Player hit by the target
        :return: None
        """
        if target in space.bodies and target.shape in space.shapes:
            self.space.remove(target, target.shape)

        if target in self.targets:
            self.targets.remove(target)

        player.hit_points -= target.damage_points

        if player.hit_points <= 0:
            self.game_over()

    def game_over(self):
        """
        Stop the game and display a game over screen.
        :return: None
        """
        self.playing = False
        self.space.remove(*self.space.bodies, *self.space.shapes)
        self.gui.show_game_over_screen()
        pygame.display.flip()

    def handle_key_input(self, keys):
        """
        Handle events triggered by keypress inputs. Move the player with arrow
        keys and WASD, and save a screenshot with P.
        :return: None
        """
        max_x = self.gui.screen_width
        max_y = self.gui.screen_height

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move(0, -1, max_x, max_y)

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move(0, 1, max_x, max_y)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1, 0, max_x, max_y)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1, 0, max_x, max_y)

        if keys[pygame.K_p]:
            pygame.image.save(self.gui.screen, 'shooter.png')

    def aim(self):
        """
        Aim the missile with the mouse.
        :return: None
        """
        mouse_position = pymunk.pygame_util.from_pygame(
            Vec2d(*pygame.mouse.get_pos()),
            self.gui.screen
        )

        missile_offset = Vec2d(self.player.shape.radius + 40, 0)

        self.player.angle = (mouse_position - self.player.position).angle
        self.missile.position = self.player.position + missile_offset.rotated(
            self.player.angle
        )

        self.missile.angle = self.player.angle

    def fire(self):
        """
        Fire a charged missile.
        :return: None
        """
        power = 13.5
        charge = self.charge_shot() * power
        impulse = charge * Vec2d(1, 0)
        impulse = impulse.rotated(self.missile.angle)

        self.missile.body_type = pymunk.Body.DYNAMIC
        self.missile.apply_impulse_at_world_point(
            impulse,
            self.missile.position
        )

        self.flying_missiles.append(self.missile)

    def charge_shot(self) -> float:
        """
        Increases the power of the fired missile depending on how long the
        player has held the mouse down.
        :return: The factor by which the missile's power is increased.
        """
        max_charge = 1000
        min_charge = 10
        time = pygame.time.get_ticks()
        dt = time - self.start_time
        charge = min(dt, max_charge)
        power = max(charge, min_charge)
        return power

    def show_power_meter(self):
        """
        Display the power meter on the let side of the screen as the player
        charges a shot.
        :return: None
        """
        start_x = 30
        start_y = 550
        width = 10
        height = self.charge_shot() // 2

        pygame.draw.line(
            self.gui.screen,
            pygame.Color('red'),
            (start_x, start_y),
            (start_x, start_y - height),
            width
        )

    def update_targets(self):
        """
        Periodically spawn a new falling target and remove targets that are no
        longer in play.
        :return: None
        """
        self.ticks_to_next_target -= 1

        if self.ticks_to_next_target <= 0:
            self.ticks_to_next_target = 100
            self.spawn_target()

        targets_to_remove = []

        for target in self.targets:
            if target.position.y >= self.gui.screen_height:
                targets_to_remove.append(target)
                self.player.score -= target.damage_points

                if self.player.score < 0:
                    self.player.score = 0

        for target in targets_to_remove:
            if target in self.space.bodies:
                self.space.remove(target, target.shape)

            if target in self.targets:
                self.targets.remove(target)

    def spawn_target(self):
        """
        Create a target at a random position at the top of the screen.
        :return: None
        """
        target = Target()
        target_x = random.randint(100, self.gui.screen_width - 100)

        target.position = target_x, 100
        self.space.add(target, target.shape)
        self.targets.append(target)


def main():
    game = App()
    game.setup()
    game.run()


if __name__ == '__main__':
    main()
