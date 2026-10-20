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
COULEURS_LIGNES = [
    (231, 76, 60),    # rouge
    (230, 126, 34),   # orange
    (241, 196, 15),   # jaune
    (46, 204, 113),   # vert
    (52, 152, 219),   # bleu
]

LARGEUR_RAQUETTE = 100
HAUTEUR_RAQUETTE = 12
VITESSE_RAQUETTE = 7
MARGE_BAS = 30  # distance entre la raquette et le bas de l'écran

Vitesse = tuple[int, int]
TAILLE_BALLE = 12
VITESSE_INITIALE: Vitesse = (4, -4)

Mur = list[pygame.Rect]
NB_LIGNES = 5
NB_COLONNES = 10
ESPACEMENT = 4
MARGE_HAUT = 60
HAUTEUR_BRIQUE = 20
LARGEUR_BRIQUE = (LARGEUR - (NB_COLONNES + 1) * ESPACEMENT) // NB_COLONNES


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


def creer_mur() -> Mur:
    """Crée la liste des briques, ligne par ligne."""
    mur: Mur = []
    for ligne in range(NB_LIGNES):
        for colonne in range(NB_COLONNES):
            x = ESPACEMENT + colonne * (LARGEUR_BRIQUE + ESPACEMENT)
            y = MARGE_HAUT + ligne * (HAUTEUR_BRIQUE + ESPACEMENT)
            mur.append(pygame.Rect(x, y, LARGEUR_BRIQUE, HAUTEUR_BRIQUE))
    return mur


def dessiner_mur(mur: Mur) -> None:
    for brique in mur:
        # On retrouve le numéro de ligne à partir de l'ordonnée de la brique
        ligne = (brique.y - MARGE_HAUT) // (HAUTEUR_BRIQUE + ESPACEMENT)
        pygame.draw.rect(ecran, COULEURS_LIGNES[ligne], brique)


def main() -> None:
    horloge = pygame.time.Clock()
    raquette = initialiser_raquette()
    balle = initialiser_balle()
    vitesse = VITESSE_INITIALE
    mur = creer_mur()

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
        dessiner_mur(mur)
        dessiner_raquette(raquette)
        dessiner_balle(balle)
        pygame.display.update()
        horloge.tick(FPS)

    pygame.quit()
