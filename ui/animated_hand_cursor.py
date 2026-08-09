import math

import pygame


# cursore a forma di mano con una leggera animazione fluttuante
class AnimatedHandCursor:

    def __init__(
        self,
        image_path,
        size=(64, 64)
    ):

        # carico l'immagine mantenendo la trasparenza
        self.image = pygame.image.load(
            image_path
        ).convert_alpha()

        # ridimensiono il cursore
        self.image = pygame.transform.smoothscale(
            self.image,
            size
        )

        # ampiezza del movimento in pixel
        self.horizontal_amplitude = 5
        self.vertical_amplitude = 2

        # velocità delle due oscillazioni
        self.horizontal_speed = 4.0
        self.vertical_speed = 2.5

    # disegna la manina a sinistra dell'elemento indicato
    def draw(self, screen, target_rect, gap=5):

        # recupero il tempo trascorso in secondi
        elapsed_time = (
            pygame.time.get_ticks() / 1000.0
        )

        # calcolo l'oscillazione orizzontale
        horizontal_offset = int(
            math.sin(
                elapsed_time * self.horizontal_speed
            ) * self.horizontal_amplitude
        )

        # calcolo la fluttuazione verticale
        vertical_offset = int(
            math.sin(
                elapsed_time * self.vertical_speed
            ) * self.vertical_amplitude
        )

        # preparo la posizione base della manina
        hand_rect = self.image.get_rect()

        hand_rect.centery = (
            target_rect.centery + vertical_offset
        )

        hand_rect.right = (
            target_rect.left
            - gap
            + horizontal_offset
        )

        # disegno la manina nella posizione animata
        screen.blit(
            self.image,
            hand_rect
        )