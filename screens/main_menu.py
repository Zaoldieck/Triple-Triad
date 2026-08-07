import pygame
from screens.screen import Screen

# Classe che gestisce il menu principale del gioco

class MainMenu(Screen):

    def __init__(self, width, height, state):

        # dimensioni della finestra
        self.width = width
        self.height = height
    
        # stato globale del gioco
        self.state = state

        # carico lo sfondo del menu
        self.background_image = pygame.image.load("assets/images/background_start_menu.png").convert()  # carico l'immagine di sfondo
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))  # ridimensiono l'immagine di sfondo alle dimensioni della finestra

        self.font = pygame.font.SysFont("Arial", 45)  # font Arial, dimensione 45

        # elenco delle voci del menu
        self.menu_items = [
            "Story Mode",
            "Free Match",
            "Local Multiplayer",
            "Deck",
            "Statistics",
            "Guide",
            "Settings",
            "Credits",
            "Exit"
        ]

        # variabili per gestire la selezione e animazione delle voci del menu
        self.selected_item = 0  # indice della voce selezionata

        # animazione dello scorrimento del menu
        self.scrolling = False  # flag per indicare se il menu sta animando lo scorrimento
        self.scroll_direction = 0  # direzione dello scorrimento (-1 per su, 1 per giù)
        self.scroll_offset = 0.0  # offset di scorrimento per l'animazione
        self.scroll_speed = 0.4  # velocità di scorrimento in pixel per frame

        #quante voci nel menu appaiono sullo schermo contemporaneamente, 5 in questo caso
        self.positions = [
            -2,   # voce sopra
            -1,   # voce sopra
             0,   # voce selezionata
             1,   # voce sotto
             2    # voce sotto
        ]

        # rettangolo della voce menu selezionata 
        self.selected_item_rect = None

    # gestisco gli eventi del menu principale
    def handle_events(self, event):

        if self.scrolling:  # se il menu sta animando lo scorrimento, ignoro gli input
            return

        #controllo mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1: # tasto sinistro del mouse
                mouse_x, mouse_y = event.pos # posizione del mouse
                if self.selected_item_rect.collidepoint(mouse_x, mouse_y): # se il cursore e' nel "rettangolo"
                    selected = self.menu_items[self.selected_item]
                    if selected == "Exit":
                        self.state.running = False

        # controllo tastiera
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:  # se premo INVIO

                selected = self.menu_items[self.selected_item] # assegna a selected la voce del menu centrale

                if selected == "Exit":
                    self.state.running = False

                elif selected == "Story Mode":
                    pass

                elif selected == "Free Match":
                    pass
 




                # from screens.test_screen import TestScreen  # importo la schermata di test
                # self.state.change_screen(TestScreen(self.width, self.height, self.state))  # cambio la schermata attiva a quella di test

            #if event.key == pygame.K_p:

                #from panels.test_panel import TestPanel
                #self.state.open_panel(TestPanel(self.width, self.height, self.state))


            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)  # seleziono la voce precedente
                self.scrolling = True  # inizio l'animazione dello scorrimento
                self.scroll_direction = -1  # imposto la direzione dello scorrimento
                self.scroll_offset = 0.0  # resetto l'offset di scorrimento
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)  # seleziono la voce successiva
                self.scrolling = True  # inizio l'animazione dello scorrimento
                self.scroll_direction = 1  # imposto la direzione dello scorrimento 
                self.scroll_offset = 0.0  # resetto l'offset di scorrimento

        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # scroll up
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                self.scrolling = True
                self.scroll_direction = -1
                self.scroll_offset = 0.0
            elif event.y < 0:  # scroll down
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                self.scrolling = True
                self.scroll_direction = 1
                self.scroll_offset = 0.0

    def update(self):

        CENTER_Y = self.height // 2  # coordinata y del centro dello schermo
        SPACING = 41  # distanza tra le voci del menu

        if self.scrolling:  # se il menu sta animando lo scorrimento
            self.scroll_offset += self.scroll_speed  # aggiorno l'offset di scorrimento
            if self.scroll_offset >= SPACING:  # se l'offset ha raggiunto la distanza tra le voci del menu
                self.scrolling = False  # fermo l'animazione dello scorrimento
                self.scroll_offset = 0.0  # resetto l'offset di scorrimento

    # disegna il menu principale sullo schermo
    def draw(self, screen):
        
        CENTER_Y = self.height // 2  # coordinata y del centro dello schermo
        SPACING = 41  # distanza tra le voci del menu

        # aggiorno la finestra di gioco
        screen.blit(self.background_image, (0, 0))  # disegno lo sfondo

        for offset in self.positions:
            index = (self.selected_item + offset) % len(self.menu_items)  # calcolo l'indice della voce da disegnare
            text_surface = self.font.render(self.menu_items[index], True, (255, 255, 255))  # creo la superficie del testo

            if offset == 0:  # se la voce è selezionata
                text_surface.set_alpha(255)  # opacità normale

            elif offset == -1 or offset == 1:  # se la voce è sopra o sotto quella selezionata
                text_surface.set_alpha(120)  # opacità ridotta
                text_surface = pygame.transform.scale(text_surface, (int(text_surface.get_width() * 0.7), int(text_surface.get_height() * 0.8)))  

            else:  # se la voce è più lontana da quella selezionata
                text_surface.set_alpha(60)  # opacità molto ridotta
                text_surface = pygame.transform.scale(text_surface, (int(text_surface.get_width() * 0.5), int(text_surface.get_height() * 0.6)))  # ridimensiono il testo

            x = (self.width - text_surface.get_width()) // 2  # calcolo la coordinata x per centrare il testo
            y = CENTER_Y + (CENTER_Y // 5 * 3) + offset * SPACING - self.scroll_offset * self.scroll_direction - text_surface.get_height() // 2  # calcolo la coordinata y per posizionare il testo

            text_rect = text_surface.get_rect(topleft=(x, y))

            if offset == 0:
                self.selected_item_rect = text_rect

            screen.blit(text_surface, (x, y))  # disegno il testo sullo schermo