import pygame

from panels.panel import Panel  # serve per importare la classe Panel dal file panel.py




# classe pannello di prova per testare il sistema dei riquadri

class TestPanel(Panel):
    
    def __init__(self, width, height, state):

        # dimensioni della finestra
        self.width = width
        self.height = height
    
        # stato globale del gioco
        self.state = state

        # dimensioni del pannello
        self.panel_width = 600
        self.panel_height = 400

        # dimensioni iniziali per l'animazione 
        self.current_width = 0
        self.current_height = 0

        # velocita apertura pannello (animazione)
        self.open_speed = 3

        # indica se il pannello e' ancora in apertura
        self.opening = True

        # Colore pannello
        self.color = (100, 100, 100)

        # font di prova
        self.font = pygame.font.SysFont("Arial", 40)


    # eventi del pannello
    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state.close_panel()

    
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

        #testo di prova
        text = self.font.render("Test Panel - press ESC", True, (255, 255, 255))

        text_x = (self.width - text.get_width()) // 2
        text_y = (self.height - text.get_height()) // 2

        screen.blit(text, (text_x, text_y))
