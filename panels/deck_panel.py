import pygame
from panels.panel import Panel

class DeckPanel(Panel):

    def __init__(self, width, height, state):

        self.width = width
        self.height = height
        self.state = state

        # dimensioni del pannello
        self.panel_width = 900
        self.panel_height = 550

        # dimensioni iniziali per l'animazione
        self.current_width = 0
        self.current_height = 0

        # velocita apertura pannello (animazione)
        self.open_speed = 3

        # indica se il pannello e' ancora in apertura
        self.opening = True

        # colore pannello
        self.color = (100, 100, 100)

        # font 
        self.font = pygame.font.SysFont("Arial", 40)

        # font piu piccolo per info del deck
        self.info_font = pygame.font.SysFont("Arial", 24)

        # carico l'immagine del cursore
        self.hand_cursor = pygame.image.load(
            "assets/images/hand_cursor.png"
        ).convert_alpha()

        # ridimensiono il cursore manina
        self.hand_cursor = pygame.transform.smoothscale(self.hand_cursor, (64,64))

        # indice dello slot attualmente selezionato
        self.selected_card = 0

        # dato che ci sono piu pagine di carte
        self.current_page = 0

        # numero pagine
        self.total_pages = 10

        # lista che contiene i rettangoli dei 10 slot delle carte
        self.slot_rects = []

    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()

            #faccio spostare la manina su e giu nei 10 slots del pannello
            elif event.key == pygame.K_UP:
                self.selected_card = (self.selected_card - 1) % 10

            elif event.key == pygame.K_DOWN:
                self.selected_card = (self.selected_card + 1) % 10


            # pagina sinistra e destra del pannello deck
            elif event.key == pygame.K_LEFT:
                self.current_page = (self.current_page - 1) % self.total_pages

            elif event.key == pygame.K_RIGHT:
                self.current_page = (self.current_page + 1) % self.total_pages

        # evento rotella del mouse
        if event.type == pygame.MOUSEWHEEL:

            # rotella verso l'alto 
            if event.y > 0:
                self.current_page = (
                    self.current_page - 1
                ) % self.total_pages

            # rotella verso il basso 
            if event.y < 0:
                self.current_page = (
                    self.current_page + 1
                ) % self.total_pages

        # se il mouse si muove
        if event.type == pygame.MOUSEMOTION:

            # controllo tutti i rettangoli degli slot
            for i, slot_rect in enumerate(self.slot_rects):

                # se il mouse si trova sopra uno slot, lo seleziono
                if slot_rect.collidepoint(event.pos):
                    self.selected_card = i

    # logica del pannello                
    def update(self):

        if self.opening:

            self.current_width += self.open_speed
            self.current_height += self.open_speed

            # quando raggiunge la dimensione finale ferma l'animazione!
            if self.current_width >= self.panel_width:
                self.current_width = self.panel_width

            if self.current_height >= self.panel_height:
                self.current_height = self.panel_height

            if self.current_width == self.panel_width and self.current_height == self.panel_height:
                self.opening = False            

    # disegna il pannello
    def draw(self, screen):

        #posizione del pannello sullo schermo
        x = (self.width - self.current_width) // 2
        y = (self.height - self.current_height) // 2

        #creo il rettangolo del pannello
        panel_rect = pygame.Rect(x, y, self.current_width, self.current_height)

        #disegno il pannello
        pygame.draw.rect(screen, self.color, panel_rect)

        # area che conterra' la lista delle carte
        list_rect = pygame.Rect(
            x + 30,
            y + 30,
            400,
            self.current_height - 60
        )
        # area per la lista delle carte, disegna
        pygame.draw.rect(screen, (70, 70, 70), list_rect)

        # creo i 10 spazi per le carte della pagina
        slot_height = 42
        slot_spacing = 5

        # svuoto la lista prima di ricreare i rettangoli degli slot
        self.slot_rects = []

        for i in range(10):
            slot_rect = pygame.Rect(
                list_rect.x + 10,
                list_rect.y + 10 + i * (slot_height + slot_spacing),
                list_rect.width - 20,
                slot_height
            )

            self.slot_rects.append(slot_rect)

            pygame.draw.rect(screen, (50,50,50), slot_rect)

            # disegno la manina accanto allo slot selezionato
            if i == self.selected_card:
                hand_rect = self.hand_cursor.get_rect()
                hand_rect.centery = slot_rect.centery
                hand_rect.right = slot_rect.left - 5

                screen.blit(self.hand_cursor, hand_rect)

        #preparo il testo con il numero della pagina corrente
        page_text = self.info_font.render(
            f"Page {self.current_page + 1} / {self.total_pages}",
            True,
            (255, 255, 255)
        )

        #posiziono il numero della pagina nella parte destra del pannello
        page_text_rect = page_text.get_rect(
            center=(x + 665, y + 30)
        )

        #disegno il numero sulla pagina
        screen.blit(page_text,page_text_rect)





        #testo di prova
        #text = self.font.render("Deck Panel - press ESC", True, (255, 255, 255))

        #text_x = (self.width - text.get_width()) // 2
        #text_y = (self.height - text.get_height()) // 2

        #screen.blit(text, (text_x, text_y))                