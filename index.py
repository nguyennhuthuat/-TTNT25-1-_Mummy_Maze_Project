import pygame 

pygame.init()

SCREEN = pygame.display.set_mode([1000, 600])

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    SCREEN.fill((255,255,255))

    pygame.display.flip()


pygame.quit()





