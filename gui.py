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

        self.font_family = 'Calibri'
        self.font_size_p = 18
        self.font_size_h1 = 36

        # self.main_font = pygame.font.SysFont('Calibri', 18)

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
        self.render_text(text, text_start, self.font_size_p)

    def show_frame_rate(self):
        """
        Display the current frame rate at the top of the screen
        :return: None
        """
        frames_per_second = self.clock.get_fps()
        text = f'{frames_per_second} FPS'
        text_start = (0, 5)
        self.render_text(text, text_start, self.font_size_p)

    def show_instructions(self):
        """
        Display the instructions at the bottom of the screen.
        :return: None
        """
        text_start_x = 5
        text_start_y = self.screen_height - 75
        line_height = 25
        instructions = [
            'Aim with the mouse. Hold the left mouse button to charge the shot,'
            ' then release it to fire',
            'Use the arrow keys or WASD keys to move.',
            'Press Esc or \'Q\' to quit.'
        ]

        for line in instructions:
            self.render_text(line, (text_start_x, text_start_y), self.font_size_p)
            text_start_y += line_height

    def show_game_over_screen(self):
        """
        Clear the screen and display the game over text.
        :return: None
        """
        self.clear()

        text = 'Game over'
        text_start_x = self.screen_width / 2 - self.font_size_h1 * 2
        text_start_y = self.screen_height / 2

        self.render_text(text, (text_start_x, text_start_y), self.font_size_h1)

    def render_text(self, text: str, text_start: tuple, text_size: int):
        """
        Render a string of text on the screen.
        :param text_size: Font size for the rendered text
        :param text: String of text to render
        :param text_start: Starting point of the text string on the screen
        :return: None
        """
        font = pygame.font.SysFont(self.font_family, text_size)
        text_surface = font.render(text, True, pygame.Color('white'))
        self.screen.blit(source=text_surface, dest=text_start)
