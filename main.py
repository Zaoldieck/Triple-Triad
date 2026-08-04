import pygame #serve per creare la finestra di gioco

#inizializzo py game
pygame.init()

# dimensioni della finestra
width = 1280
height = 720

# creo la finestra di gioco
screen = pygame.display.set_mode((width, height))

running = True
while running: #loop per tenere aperta la finestra di gioco
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # aggiorno la finestra di gioco
    pygame.display.flip()

# Chiude pygame
pygame.quit()