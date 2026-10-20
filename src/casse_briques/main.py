import pygame


pygame.init()

LARGEUR = 640
HAUTEUR = 480
FPS = 60

ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Casse-briques")

NOIR = (20, 20, 20)
BLANC = (240, 240, 240)
TURQUOISE = (23, 154, 175)
JAUNE = (255, 207, 0)


def main() -> None:
    horloge = pygame.time.Clock()

    print("Welcome to casse briques !")

    en_cours: bool = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        ecran.fill(NOIR)
        pygame.display.update()
        horloge.tick(FPS)

    pygame.quit()
