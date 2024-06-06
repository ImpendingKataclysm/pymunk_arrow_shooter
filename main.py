import pygame
import pymunk

from gui import Interface


class App:
    """
    Pymunk target shooting simulation.
    """
    def __init__(self):
        pygame.init()

        self.running: bool = False

        self.space = pymunk.Space()
        self.space.gravity = (0, 100)

        self.gui = Interface(self.space)

        print(self.gui)

    def setup(self):
        """
        Sets up the game's starting state.
        :return: None
        """
        self.running = True

    def run(self):
        """
        Update the screen and the physics engine.
        :return: None
        """
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    self.handle_key_input()
                elif e.type == pygame.QUIT:
                    self.running = False

            self.gui.clear()

            pygame.display.flip()

    def handle_key_input(self):
        """
        Handle events triggered by keypress inputs.
        :return: None
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            self.running = False


def main():
    game = App()
    game.setup()
    game.run()


if __name__ == '__main__':
    main()
