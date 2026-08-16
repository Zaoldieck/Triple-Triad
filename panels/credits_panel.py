import pygame

from panels.panel import Panel
from ui.animated_hand_cursor import AnimatedHandCursor


# pannello che mostra i crediti del progetto
class CreditsPanel(Panel):

    def __init__(
        self,
        width,
        height,
        state
    ):

        self.width = width
        self.height = height
        self.state = state

        # dimensioni e posizione del pannello
        self.panel_width = 900
        self.panel_height = 640

        self.panel_x = (
            self.width - self.panel_width
        ) // 2

        self.panel_y = (
            self.height - self.panel_height
        ) // 2

        # colori
        self.panel_color = (
            45,
            45,
            50
        )

        self.border_color = (
            255,
            255,
            255
        )

        self.primary_color = (
            255,
            255,
            255
        )

        self.secondary_color = (
            175,
            175,
            175
        )

        self.heading_color = (
            220,
            200,
            120
        )

        # font
        self.title_font = pygame.font.SysFont(
            "Arial",
            44
        )

        self.heading_font = pygame.font.SysFont(
            "Arial",
            25
        )

        self.text_font = pygame.font.SysFont(
            "Arial",
            23
        )

        self.small_font = pygame.font.SysFont(
            "Arial",
            19
        )

        # area visibile del contenuto scorrevole
        self.content_width = 820
        self.content_view_height = 500

        self.content_x = (
            self.width - self.content_width
        ) // 2

        self.content_y = self.panel_y + 30

        # stato dello scorrimento
        self.scroll_offset = 0
        self.scroll_step = 45
        self.max_scroll_offset = 0

        # pulsante fisso Back
        self.back_rect = None

        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

    # chiude il pannello dei crediti
    def close_credits(self):

        self.state.close_panel()

    # gestisce tastiera e mouse
    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.close_credits()

            elif event.key == pygame.K_RETURN:
                self.close_credits()

            elif event.key == pygame.K_UP:
                self.scroll_offset = max(
                    0,
                    self.scroll_offset
                    - self.scroll_step
                )

            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(
                    self.max_scroll_offset,
                    self.scroll_offset
                    + self.scroll_step
                )

            elif event.key == pygame.K_HOME:
                self.scroll_offset = 0

            elif event.key == pygame.K_END:
                self.scroll_offset = (
                    self.max_scroll_offset
                )

        if event.type == pygame.MOUSEWHEEL:

            self.scroll_offset = max(
                0,
                min(
                    self.max_scroll_offset,
                    self.scroll_offset
                    - event.y * self.scroll_step
                )
            )

        if event.type == pygame.MOUSEBUTTONDOWN:

            # click destro chiude sempre il pannello
            if event.button == 3:
                self.close_credits()

            # click sinistro chiude tramite Back
            elif (
                event.button == 1
                and self.back_rect is not None
                and self.back_rect.collidepoint(
                    event.pos
                )
            ):
                self.close_credits()

    # nessuna logica aggiuntiva
    def update(self):
        pass

    # aggiunge una riga centrata al contenuto
    def draw_content_line(
        self,
        surface,
        text,
        font,
        color,
        y
    ):

        text_surface = font.render(
            text,
            True,
            color
        )

        text_rect = text_surface.get_rect(
            center=(
                self.content_width // 2,
                y
            )
        )

        surface.blit(
            text_surface,
            text_rect
        )

    # disegna il pannello dei crediti
    def draw(self, screen):

        panel_rect = pygame.Rect(
            self.panel_x,
            self.panel_y,
            self.panel_width,
            self.panel_height
        )

        pygame.draw.rect(
            screen,
            self.panel_color,
            panel_rect
        )

        pygame.draw.rect(
            screen,
            self.border_color,
            panel_rect,
            2
        )

        # contenuto completo, più alto
        # rispetto all'area visibile
        content_height = 1250

        content_surface = pygame.Surface(
            (
                self.content_width,
                content_height
            ),
            pygame.SRCALPHA
        )

        y = 45

        self.draw_content_line(
            content_surface,
            "CREDITS",
            self.title_font,
            self.primary_color,
            y
        )

        y += 80

        credit_sections = [
            (
                "Created by",
                "Zao"
            ),
            (
                "Programming, Game Systems & Interface",
                "Zao"
            ),
            (
                "Visual Assets",
                "Created and adapted for this project by Zao"
            ),
            (
                "Built With",
                "Python & Pygame"
            ),
            (
                "Based on",
                "Triple Triad from Final Fantasy VIII"
            ),
            (
                "Original Game Concept and Characters",
                "Square Enix"
            ),
            (
                "Special Thanks",
                "The Final Fantasy VIII community"
            )
        ]

        for heading, value in credit_sections:

            self.draw_content_line(
                content_surface,
                heading,
                self.heading_font,
                self.heading_color,
                y
            )

            y += 34

            self.draw_content_line(
                content_surface,
                value,
                self.text_font,
                self.primary_color,
                y
            )

            y += 60

        # linea di separazione
        pygame.draw.line(
            content_surface,
            self.secondary_color,
            (
                80,
                y
            ),
            (
                self.content_width - 80,
                y
            ),
            2
        )

        y += 55

        disclaimer_lines = [
            (
                "This is an unofficial, non-commercial "
                "fan recreation"
            ),
            (
                "created for educational purposes."
            ),
            "",
            (
                "This project is not affiliated with "
                "or endorsed by Square Enix."
            ),
            "",
            (
                "FINAL FANTASY, TRIPLE TRIAD,"
            ),
            (
                "and related names and characters belong"
            ),
            (
                "to their respective rights holders."
            )
        ]

        for line in disclaimer_lines:

            if line:
                self.draw_content_line(
                    content_surface,
                    line,
                    self.small_font,
                    self.secondary_color,
                    y
                )

            y += 32

        # calcolo il limite dello scorrimento
        self.max_scroll_offset = max(
            0,
            y - self.content_view_height + 20
        )

        self.scroll_offset = min(
            self.scroll_offset,
            self.max_scroll_offset
        )

        # mostro soltanto la porzione corrente
        visible_area = pygame.Rect(
            0,
            self.scroll_offset,
            self.content_width,
            self.content_view_height
        )

        screen.blit(
            content_surface,
            (
                self.content_x,
                self.content_y
            ),
            visible_area
        )

        # pulsante Back fisso nella parte inferiore
        back_surface = self.heading_font.render(
            "Back",
            True,
            self.primary_color
        )

        self.back_rect = back_surface.get_rect(
            center=(
                self.width // 2,
                self.panel_y
                + self.panel_height
                - 45
            )
        )

        screen.blit(
            back_surface,
            self.back_rect
        )

        self.hand_cursor.draw(
            screen,
            self.back_rect,
            gap=5
        )