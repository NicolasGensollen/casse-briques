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

LARGEUR_RAQUETTE = 100
HAUTEUR_RAQUETTE = 12
VITESSE_RAQUETTE = 7
MARGE_BAS = 30  # distance entre la raquette et le bas de l'écran


def initialiser_raquette() -> pygame.Rect:
    """Crée la raquette centrée horizontalement, en bas de l'écran."""
    x = (LARGEUR - LARGEUR_RAQUETTE) // 2
    y = HAUTEUR - MARGE_BAS - HAUTEUR_RAQUETTE
    return pygame.Rect(x, y, LARGEUR_RAQUETTE, HAUTEUR_RAQUETTE)


def dessiner_raquette(raquette: pygame.Rect) -> None:
    pygame.draw.rect(ecran, TURQUOISE, raquette, border_radius=4)


def main() -> None:
    horloge = pygame.time.Clock()
    raquette = initialiser_raquette()

    en_cours: bool = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        ecran.fill(NOIR)
        dessiner_raquette(raquette)
        pygame.display.update()
        horloge.tick(FPS)

    pygame.quit()
