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

    def setup(self):
        """
        Sets up the game's starting state.
        :return: None
        """
        self.running = True
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
        left_click_event = 1
        left_mouse_press = 0

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

            pygame.display.flip()

            self.fps = 60
            self.space.step(1.0 / self.fps)
            self.gui.clock.tick(self.fps)

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
