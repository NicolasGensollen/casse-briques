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

Vitesse = tuple[int, int]
TAILLE_BALLE = 12
VITESSE_INITIALE: Vitesse = (4, -4)


def initialiser_raquette() -> pygame.Rect:
    """Crée la raquette centrée horizontalement, en bas de l'écran."""
    x = (LARGEUR - LARGEUR_RAQUETTE) // 2
    y = HAUTEUR - MARGE_BAS - HAUTEUR_RAQUETTE
    return pygame.Rect(x, y, LARGEUR_RAQUETTE, HAUTEUR_RAQUETTE)


def dessiner_raquette(raquette: pygame.Rect) -> None:
    pygame.draw.rect(ecran, TURQUOISE, raquette, border_radius=4)


def deplacer_raquette(raquette: pygame.Rect, touches: pygame.key.ScancodeWrapper) -> None:
    """Déplace la raquette selon les touches maintenues, sans sortir de l'écran."""
    if touches[pygame.K_LEFT]:
        raquette.x -= VITESSE_RAQUETTE
    if touches[pygame.K_RIGHT]:
        raquette.x += VITESSE_RAQUETTE
    # On empêche la raquette de sortir de la fenêtre
    if raquette.left < 0:
        raquette.left = 0
    if raquette.right > LARGEUR:
        raquette.right = LARGEUR


def initialiser_balle() -> pygame.Rect:
    """Crée la balle juste au-dessus du centre de la raquette."""
    x = (LARGEUR - TAILLE_BALLE) // 2
    y = HAUTEUR - MARGE_BAS - HAUTEUR_RAQUETTE - TAILLE_BALLE - 2
    return pygame.Rect(x, y, TAILLE_BALLE, TAILLE_BALLE)


def dessiner_balle(balle: pygame.Rect) -> None:
    pygame.draw.ellipse(ecran, BLANC, balle)


def deplacer_balle(balle: pygame.Rect, vitesse: Vitesse) -> None:
    vx, vy = vitesse
    balle.x += vx
    balle.y += vy


def rebondir_murs(balle: pygame.Rect, vitesse: Vitesse) -> Vitesse:
    """Fait rebondir la balle sur les bords gauche, droit et haut.

    On utilise abs() plutôt qu'une simple inversion de signe : si la balle reste
    plusieurs images « dans » le bord, elle ne repart pas dans le mauvais sens.
    """
    vx, vy = vitesse

    if balle.left <= 0:
        balle.left = 0
        vx = abs(vx)
    elif balle.right >= LARGEUR:
        balle.right = LARGEUR
        vx = -abs(vx)
    if balle.top <= 0:
        balle.top = 0
        vy = abs(vy)
    return vx, vy


def rebondir_raquette(balle: pygame.Rect, vitesse: Vitesse, raquette: pygame.Rect) -> Vitesse:
    """Renvoie la balle vers le haut si elle touche la raquette en descendant."""
    vx, vy = vitesse
    if balle.colliderect(raquette) and vy > 0:
        balle.bottom = raquette.top
        vy = -vy
    return vx, vy


def main() -> None:
    horloge = pygame.time.Clock()
    raquette = initialiser_raquette()
    balle = initialiser_balle()
    vitesse = VITESSE_INITIALE

    en_cours: bool = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        deplacer_raquette(raquette, pygame.key.get_pressed())
        deplacer_balle(balle, vitesse)
        vitesse = rebondir_murs(balle, vitesse)
        vitesse = rebondir_raquette(balle, vitesse, raquette)

        ecran.fill(NOIR)
        dessiner_raquette(raquette)
        dessiner_balle(balle)
        pygame.display.update()
        horloge.tick(FPS)

    pygame.quit()
