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

        self.main_font = pygame.font.SysFont('Calibri', 18)

    def clear(self):
        """
        Clear the screen and display a solid background.
        :return: None
        """
        self.screen.fill(pygame.Color('darkslategray'))

    def show_score(self, points: int):
        """
        Display the player's score in the GUI.
        :param points: Player's current score
        :return: None
        """
        text = f'Score: {points}'
        text_start = (self.screen_width - 100, 20)
        self.render_text(text, text_start)

    def render_text(self, text: str, text_start: tuple):
        """
        Render a string of text on the screen.
        :param text: String of text to render
        :param text_start: Starting point of the text string on the screen
        :return: None
        """
        text_surface = self.main_font.render(text, True, pygame.Color('white'))
        self.screen.blit(source=text_surface, dest=text_start)
