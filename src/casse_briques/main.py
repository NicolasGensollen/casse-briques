import math
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

Vitesse = tuple[float, float]
Position = tuple[float, float]
TAILLE_BALLE = 12
VITESSE_INITIALE: Vitesse = (4, -4)

Mur = list[pygame.Rect]
NB_LIGNES = 5
NB_COLONNES = 10
ESPACEMENT = 4
MARGE_HAUT = 60
HAUTEUR_BRIQUE = 20
LARGEUR_BRIQUE = (LARGEUR - (NB_COLONNES + 1) * ESPACEMENT) // NB_COLONNES

VIES_INITIALES = 3
POINTS_PAR_BRIQUE = 10

police = pygame.font.SysFont(None, 32)
grande_police = pygame.font.SysFont(None, 48)

ANGLE_MAX = 60 # angle maximal (en degrés) par rapport à la verticale


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
        decalage = (balle.centerx - raquette.centerx) / (raquette.width / 2)
        decalage = max(-1.0, min(1.0, decalage))  # bornage dans [-1, 1]
        angle = math.radians(ANGLE_MAX * decalage)
        norme = math.hypot(vx, vy)
        vx = norme * math.sin(angle)
        vy = -norme * math.cos(angle)
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


def gerer_collision_briques(balle: pygame.Rect, vitesse: Vitesse, mur: Mur) -> tuple[Vitesse, int]:
    """Détruit la brique touchée (s'il y en a une) et fait rebondir la balle.

    Renvoie la nouvelle vitesse et le nombre de briques détruites (0 ou 1).
    """
    indice = balle.collidelist(mur)
    if indice == -1:
        return vitesse, 0
    brique = mur.pop(indice)
    vx, vy = vitesse
    
    # Largeur et hauteur de la zone de chevauchement entre la balle et la brique.
    # Si le chevauchement est plus étroit que haut, la balle a touché un côté
    # de la brique : on inverse la composante horizontale. Sinon, elle a touché
    # le dessus ou le dessous : on inverse la composante verticale.
    chevauchement_x = min(balle.right, brique.right) - max(balle.left, brique.left)
    chevauchement_y = min(balle.bottom, brique.bottom) - max(balle.top, brique.top)
 
    if chevauchement_x < chevauchement_y:
        vx = -vx
    else:
        vy = -vy
    
    return (vx, vy), 1


def balle_perdue(balle: pygame.Rect) -> bool:
    return balle.top > HAUTEUR


def afficher_infos(score: int, vies: int) -> None:
    texte_score = police.render(f"Score : {score}", True, BLANC)
    texte_vies = police.render(f"Vies : {vies}", True, BLANC)
    ecran.blit(texte_score, (10, 15))
    ecran.blit(texte_vies, (LARGEUR - texte_vies.get_width() - 10, 15))


def afficher_message(message: str, sous_titre: str = "") -> None:
    texte = grande_police.render(message, True, JAUNE)
    ecran.blit(texte, texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 60)))
    if sous_titre:
        texte2 = police.render(sous_titre, True, BLANC)
        ecran.blit(texte2, texte2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 105)))


def coller_balle(balle: pygame.Rect, raquette: pygame.Rect) -> Position:
    """Place la balle au centre de la raquette (avant le lancement)."""
    balle.centerx = raquette.centerx
    balle.bottom = raquette.top - 2
    return float(balle.centerx), float(balle.centery)


def synchroniser_position(balle: pygame.Rect, position: Position) -> Position:
    """Si un rebond a recalé le rectangle, on recale aussi la position flottante."""
    if balle.center != (round(position[0]), round(position[1])):
        return float(balle.centerx), float(balle.centery)
    return position


def main() -> None:
    horloge = pygame.time.Clock()
    raquette = initialiser_raquette()
    balle = initialiser_balle()
    position = coller_balle(balle, raquette)
    balle_lancee: bool = False
    vitesse = VITESSE_INITIALE
    mur = creer_mur()
    score = 0
    vies = VIES_INITIALES
    game_over: bool = False
    victoire: bool = False
    en_cours: bool = True
    
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_over or victoire:
                    return True          # on relance une nouvelle partie
                balle_lancee = True

        if not game_over and not victoire:
            deplacer_raquette(raquette, pygame.key.get_pressed())
            
            if not balle_lancee:
                position = coller_balle(balle, raquette)
            else:
                deplacer_balle(balle, vitesse)
                vitesse = rebondir_murs(balle, vitesse)
                vitesse = rebondir_raquette(balle, vitesse, raquette)
                vitesse, nb_detruites = gerer_collision_briques(balle, vitesse, mur)
                position = synchroniser_position(balle, position)
                score += nb_detruites * POINTS_PAR_BRIQUE

            if balle_perdue(balle):
                vies -= 1
                if vies == 0:
                    game_over = True
                else:
                    raquette = initialiser_raquette()
                    position = coller_balle(balle, raquette)
                    vitesse = VITESSE_INITIALE
                    balle_lancee = False

            if len(mur) == 0:
                victoire = True

        ecran.fill(NOIR)
        dessiner_mur(mur)
        dessiner_raquette(raquette)
        if not game_over:
            dessiner_balle(balle)
        afficher_infos(score, vies)
        
        if game_over:
            afficher_message(f"Perdu ! Score final : {score}")
        elif victoire:
            afficher_message(f"Gagné ! Score final : {score}")
        elif not balle_lancee:
            afficher_message("", "ESPACE pour lancer la balle")

        pygame.display.update()
        horloge.tick(FPS)

    pygame.quit()
