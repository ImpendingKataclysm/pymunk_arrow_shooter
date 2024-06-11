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
        self.player_score: int = 0

    def setup(self):
        """
        Sets up the game's starting state.
        :return: None
        """
        self.running = True
        self.fps = 0
        self.start_time = 0
        self.player_score = 0

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
        left_click_event = 1
        left_mouse_press = 0
        collision_type_target = 0
        collision_type_missile = 1

        missile_hit_handler = self.space.add_collision_handler(
            collision_type_target,
            collision_type_missile
        )

        missile_hit_handler.post_solve = self.post_solve_missile_hit

        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == left_click_event:
                        self.start_time = pygame.time.get_ticks()
                elif e.type == pygame.MOUSEBUTTONUP:
                    if e.button == left_click_event:
                        self.fire()
                        self.missile = Missile(self.player.position)
                        self.space.add(self.missile, self.missile.shape)

            self.handle_key_input()
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

            self.gui.show_score(self.player_score)

            pygame.display.flip()

            self.fps = 60
            self.space.step(1.0 / self.fps)
            self.gui.clock.tick(self.fps)
            
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
            self.player_score += target_body.score_points

        if missile_body in self.flying_missiles:
            self.flying_missiles.remove(missile_body)
            self.space.remove(missile_body, missile_body.shape)

        if target_shape in space.shapes and target_body in space.bodies:
            self.space.remove(target_shape)
            self.space.remove(target_body)

    def handle_key_input(self):
        """
        Handle events triggered by keypress inputs. Move the player with arrow
        keys and WASD, and save a screenshot with P.
        :return: None
        """
        keys = pygame.key.get_pressed()
        max_x = self.gui.screen_width
        max_y = self.gui.screen_height

        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            self.running = False

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
        self.ticks_to_next_target -= 1

        if self.ticks_to_next_target <= 0:
            self.ticks_to_next_target = 100
            self.spawn_target()

        targets_to_remove = [
            target for target in self.targets if (
                target.position.y >= self.gui.screen_height
                or target not in self.space.bodies
            )
        ]

        for target in targets_to_remove:
            if target in self.space.bodies:
                self.space.remove(target, target.shape)

            if target in self.targets:
                self.targets.remove(target)

    def spawn_target(self):
        """
        Create a target at a random position at the top of the screen.
        :return:
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
