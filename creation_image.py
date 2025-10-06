from functools import partial
from PIL.Image import new as new_image
from PIL.ImageFont import truetype as load_font
from PIL.ImageDraw import Draw

BACKGROUND_COLOR = "#000000"
IMAGE_WIDTH = 1024

# 10 = à 10% de la largeur de l'image
FIRST_LINE = (IMAGE_WIDTH // 100) * 10
LAST_LINE = (IMAGE_WIDTH // 100) * 83
LINES_WIDTH = 5
LINES_COLOR = "#A6A6A6"

FONT = load_font("alienfont.ttf", 48)
PADDING = FIRST_LINE // 3
STROKE_WIDTH = 0
# 10 40
# 0  50
MAX_CHARS = 24


async def generate_scoreboard(
    src: list, iteration: int = 0, *, show_before_saving: bool = False
) -> None:
    """
    :src: les donnes a afficher, liste au format [[couleur,place,nom,score], ...]
    :dst: le chemin ou sauvegarder le resultat, si None, ne sauvegarde rien
    :show_before_saving: si True affiche l'image a la fin
    """
    # place;pseudo;couleur;points
    if (src_type := type(src)) != list:
        raise ValueError("'src' doit etre une liste, pas {src_type}")
    COLUMN_HEIGHT = round(102 / 2.3)
    IMAGE_HEIGHT = COLUMN_HEIGHT + (len(src)) * 40
    scoreboard_image = new_image("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
    draw = Draw(scoreboard_image)

    draw_text = partial(draw.text, font=FONT, stroke_width=STROKE_WIDTH)

    draw.line(
        (FIRST_LINE, 0, FIRST_LINE, IMAGE_HEIGHT), fill=LINES_COLOR, width=LINES_WIDTH
    )
    draw.line(
        (LAST_LINE, 0, LAST_LINE, IMAGE_HEIGHT), fill=LINES_COLOR, width=LINES_WIDTH
    )

    # [display_name,display_color(hex),pr_number,user_id]
    for column, user in enumerate(src):
        name = user.display_name
        if len(name) > MAX_CHARS:
            name = name[: MAX_CHARS - 2] + "..."

        FONT_COLOR = user.display_color
        Y = column * COLUMN_HEIGHT

        draw_text((PADDING, Y), str(column + 1 + iteration * 12), fill=FONT_COLOR)
        draw_text((FIRST_LINE + PADDING, Y), name, fill=FONT_COLOR)
        draw_text((LAST_LINE + PADDING, Y), str(user.total_pr), fill=FONT_COLOR)

    if show_before_saving:
        scoreboard_image.show()

    return scoreboard_image
