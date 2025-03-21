from PIL import ImageFont, Image, ImageDraw, ImageFilter

def add_corners(im: Image.Image, rad: int) -> Image:
    """
    Adds rounded corners to an image using a transparent alpha mask.

    Creates a circular mask and applies it to the image's alpha channel to make
    corners transparent. The radius determines the roundness intensity.

    :param im: (Image) Input image (will be modified in-place).
    :param rad: (int) Radius of the rounded corners in pixels. Larger values create
                more pronounced rounded corners.
    :return: Modified image with rounded corners (has alpha channel added).
    """
    circle = Image.new('L', (rad * 2, rad * 2), 0)

    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)

    alpha = Image.new('L', im.size, 255)

    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0)) #Top left corner
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad)) #Bottom left corner
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0)) #Top right corner
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad)) #Bottom right corner

    im.putalpha(alpha)
    return im

def wrap_text(text: str, font: ImageFont.truetype, maxWidth: int) -> str:
    """
    Function that returns the given text in a wrapped format, based on the font and maxWidth given

    :param text: (string) The given text
    :param font: (ImageFont.truetype) The font of the text
    :param maxWidth: (int) The max width of a line
    :return: (string) The wrapped text
    """

    lines = []
    currentLine = ""
    for word in text.split():
        if font.getlength(currentLine + word) <= maxWidth:
            currentLine += f"{word} "
        else:
            lines.append(currentLine.strip())
            currentLine = f"{word} "

    if currentLine != "":
        lines.append(currentLine.strip())

    return '\n'.join(lines)
