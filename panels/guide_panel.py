import pygame

from panels.panel import Panel
from ui.animated_hand_cursor import AnimatedHandCursor


# pannello scorrevole che mostra la guida del gioco
class GuidePanel(Panel):

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

        # area visibile del testo
        self.content_width = 820
        self.content_view_height = 500

        self.content_x = (
            self.width - self.content_width
        ) // 2

        self.content_y = self.panel_y + 30

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
            180,
            180,
            180
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
            27
        )

        self.text_font = pygame.font.SysFont(
            "Arial",
            21
        )

        # scorrimento
        self.scroll_offset = 0
        self.scroll_step = 55
        self.max_scroll_offset = 0

        # pulsante Back
        self.back_rect = None

        self.hand_cursor = AnimatedHandCursor(
            "assets/images/hand_cursor.png"
        )

        # contenuto completo della guida
        self.guide_sections = [
            (
                "HOW TO PLAY",
                [
                    (
                        "Each player starts with five cards. "
                        "Players take turns placing one card on "
                        "an empty space of the 3 × 3 board."
                    ),
                    (
                        "The match ends when all nine spaces are "
                        "occupied. The player who controls the "
                        "most cards wins."
                    )
                ]
            ),
            (
                "CARD VALUES & BASIC CAPTURE",
                [
                    (
                        "Every card has four values: Top, Right, "
                        "Bottom, and Left."
                    ),
                    (
                        "When a card is placed next to an opposing "
                        "card, the two touching values are compared."
                    ),
                    (
                        "If the newly placed card has the higher "
                        "value, the opposing card is captured and "
                        "changes color."
                    ),
                    (
                        "Equal values do not cause a normal capture."
                    )
                ]
            ),
            (
                "MATCH SETUP",
                [
                    (
                        "Face Up — The opponent's hand is visible."
                    ),
                    (
                        "Face Down — The opponent's hand is hidden."
                    ),
                    (
                        "Choice — Select your five cards manually."
                    ),
                    (
                        "Random — Five available cards are selected "
                        "automatically."
                    ),
                    (
                        "Extra, Special, and Trade Rules can be "
                        "combined before starting the match."
                    )
                ]
            ),
            (
                "SAME",
                [
                    (
                        "Same activates when at least two sides of "
                        "the newly placed card have values equal to "
                        "the touching values beside them."
                    ),
                    (
                        "Any opposing cards involved in those "
                        "matching sides are captured."
                    ),
                    (
                        "Cards captured by Same can start a Combo."
                    )
                ]
            ),
            (
                "PLUS",
                [
                    (
                        "Plus activates when at least two touching "
                        "sides produce the same sum."
                    ),
                    (
                        "Example: 3 + 5 = 8 and 6 + 2 = 8."
                    ),
                    (
                        "Any opposing cards involved in the matching "
                        "sums are captured."
                    ),
                    (
                        "Cards captured by Plus can start a Combo."
                    )
                ]
            ),
            (
                "COMBO",
                [
                    (
                        "Combo can begin after Same or Plus."
                    ),
                    (
                        "A card captured by Same or Plus immediately "
                        "compares its values with adjacent opposing "
                        "cards using the normal capture rule."
                    ),
                    (
                        "Each newly captured card can continue the "
                        "chain, creating multiple waves of captures."
                    )
                ]
            ),
            (
                "WALL",
                [
                    (
                        "Wall works together with Same."
                    ),
                    (
                        "The outer edges of the board are treated "
                        "as having a value of 10."
                    ),
                    (
                        "A card with a value of 10 facing an outer "
                        "edge can use that edge as one of the matches "
                        "required to activate Same."
                    ),
                    (
                        "Enabling Wall automatically enables Same."
                    )
                ]
            ),
            (
                "ELEMENTAL",
                [
                    (
                        "When Elemental is active, some board spaces "
                        "receive an element."
                    ),
                    (
                        "Matching element — The card receives +1 on "
                        "all four values."
                    ),
                    (
                        "Different element or no card element — The "
                        "card receives -1 on all four values."
                    ),
                    (
                        "Elemental modifiers affect normal captures "
                        "and Combo."
                    ),
                    (
                        "Same, Plus, and Wall always use the card's "
                        "original values."
                    )
                ]
            ),
            (
                "SUDDEN DEATH",
                [
                    (
                        "If the match ends in a draw, a new round "
                        "begins automatically."
                    ),
                    (
                        "All ten cards are redistributed according "
                        "to their final color."
                    ),
                    (
                        "The board is cleared and the starting player "
                        "is selected again."
                    ),
                    (
                        "Sudden Death continues until one player wins."
                    )
                ]
            ),
            (
                "TRADE RULES",
                [
                    (
                        "One — The winner takes one card from the "
                        "loser."
                    ),
                    (
                        "Difference — The winner takes a number of "
                        "cards equal to the difference between the "
                        "final scores, up to a maximum of five."
                    ),
                    (
                        "Direct — Each card is awarded according to "
                        "the color it has at the end of the match."
                    ),
                    (
                        "All — The winner takes all five cards from "
                        "the loser."
                    )
                ]
            ),
            (
                "CONTROLS",
                [
                    (
                        "Arrow Keys — Navigate menus, select cards, "
                        "and move across the board."
                    ),
                    (
                        "Enter — Confirm the current selection."
                    ),
                    (
                        "Escape — Go back or open the leave-match "
                        "confirmation."
                    ),
                    (
                        "Mouse — Move over an option to select it."
                    ),
                    (
                        "Left Click — Confirm the selected option, "
                        "card, or board space."
                    ),
                    (
                        "Right Click — Go back or cancel."
                    ),
                    (
                        "Mouse Wheel — Scroll menus and card lists."
                    )
                ]
            )
        ]

    # chiude la guida
    def close_guide(self):

        self.state.close_panel()

    # divide automaticamente una frase
    # in più righe entro la larghezza disponibile
    def wrap_text(
        self,
        text,
        font,
        max_width
    ):

        words = text.split()
        lines = []
        current_line = ""

        for word in words:

            test_line = (
                word
                if not current_line
                else f"{current_line} {word}"
            )

            test_width = font.size(
                test_line
            )[0]

            if test_width <= max_width:
                current_line = test_line

            else:
                if current_line:
                    lines.append(
                        current_line
                    )

                current_line = word

        if current_line:
            lines.append(
                current_line
            )

        return lines

    # gestisce tastiera e mouse
    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.close_guide()

            elif event.key == pygame.K_RETURN:
                self.close_guide()

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

            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(
                    0,
                    self.scroll_offset
                    - self.content_view_height
                )

            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = min(
                    self.max_scroll_offset,
                    self.scroll_offset
                    + self.content_view_height
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

            if event.button == 3:
                self.close_guide()

            elif (
                event.button == 1
                and self.back_rect is not None
                and self.back_rect.collidepoint(
                    event.pos
                )
            ):
                self.close_guide()

    # nessuna logica aggiuntiva
    def update(self):
        pass

    # disegna una riga centrata
    def draw_centered_line(
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

    # disegna la guida
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

        # preparo prima tutte le righe
        # per calcolare l'altezza necessaria
        layout_items = []
        separator_positions = []

        y = 45

        layout_items.append(
            (
                "GUIDE",
                self.title_font,
                self.primary_color,
                y
            )
        )

        y += 85

        for (
            section_title,
            section_paragraphs
        ) in self.guide_sections:

            layout_items.append(
                (
                    section_title,
                    self.heading_font,
                    self.heading_color,
                    y
                )
            )

            y += 42

            for paragraph in section_paragraphs:

                wrapped_lines = self.wrap_text(
                    paragraph,
                    self.text_font,
                    self.content_width - 100
                )

                for line in wrapped_lines:

                    layout_items.append(
                        (
                            line,
                            self.text_font,
                            self.primary_color,
                            y
                        )
                    )

                    y += 29

                y += 13

            separator_positions.append(
                y
            )

            y += 42

        content_height = y + 20

        # creo una superficie alta esattamente
        # quanto il contenuto della guida
        content_surface = pygame.Surface(
            (
                self.content_width,
                content_height
            ),
            pygame.SRCALPHA
        )

        for (
            text,
            font,
            color,
            line_y
        ) in layout_items:

            self.draw_centered_line(
                content_surface,
                text,
                font,
                color,
                line_y
            )

        for separator_y in separator_positions:

            pygame.draw.line(
                content_surface,
                self.secondary_color,
                (
                    80,
                    separator_y
                ),
                (
                    self.content_width - 80,
                    separator_y
                ),
                1
            )

        # aggiorno i limiti dello scorrimento
        self.max_scroll_offset = max(
            0,
            content_height
            - self.content_view_height
        )

        self.scroll_offset = min(
            self.scroll_offset,
            self.max_scroll_offset
        )

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

        # disegno una piccola barra di scorrimento
        if self.max_scroll_offset > 0:

            scrollbar_x = (
                self.panel_x
                + self.panel_width
                - 20
            )

            scrollbar_top = self.content_y
            scrollbar_height = (
                self.content_view_height
            )

            pygame.draw.line(
                screen,
                self.secondary_color,
                (
                    scrollbar_x,
                    scrollbar_top
                ),
                (
                    scrollbar_x,
                    scrollbar_top
                    + scrollbar_height
                ),
                2
            )

            thumb_height = max(
                35,
                int(
                    scrollbar_height
                    * (
                        self.content_view_height
                        / content_height
                    )
                )
            )

            scroll_ratio = (
                self.scroll_offset
                / self.max_scroll_offset
            )

            thumb_y = int(
                scrollbar_top
                + (
                    scrollbar_height
                    - thumb_height
                )
                * scroll_ratio
            )

            pygame.draw.rect(
                screen,
                self.primary_color,
                pygame.Rect(
                    scrollbar_x - 3,
                    thumb_y,
                    6,
                    thumb_height
                )
            )

        # Back rimane fisso
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