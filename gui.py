import pygame


class Interface:
    """
    Creates the GUI and defines properties for static screen objects.
    """
    def __init__(self, space):
        self.space = space
        self.clock = pygame.time.Clock()

        self.screen_width = 690
        self.screen_height = 675
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

    def clear(self):
        """
        Clear the screen and display a solid background.
        :return: None
        """
        self.screen.fill(pygame.Color('darkslategray'))
