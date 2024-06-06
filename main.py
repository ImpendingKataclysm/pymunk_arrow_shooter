import pygame
import pymunk
import pymunk.pygame_util

from typing import Optional

from gui import Interface
from player import Player


class App:
    """
    Pymunk target shooting simulation.
    """
    def __init__(self):
        pygame.init()

        self.running: bool = False
        self.fps: float = 0

        self.space = pymunk.Space()
        self.space.gravity = (0, 100)

        self.gui = Interface(self.space)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.gui.screen)

        self.player: Optional[Player] = None

    def setup(self):
        """
        Sets up the game's starting state.
        :return: None
        """
        self.running = True
        self.fps = 0

        self.player = Player()
        self.player.place()
        self.space.add(self.player, self.player.shape)

    def run(self):
        """
        Update the screen and the physics engine.
        :return: None
        """
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

            self.handle_key_input()

            self.gui.clear()

            self.space.debug_draw(self.draw_options)
            pygame.display.flip()

            self.fps = 60
            self.space.step(1.0 / self.fps)

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


def main():
    game = App()
    game.setup()
    game.run()


if __name__ == '__main__':
    main()
