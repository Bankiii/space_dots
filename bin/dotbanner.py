#!/usr/bin/env python3
"""dotbanner: arte de terminal estilo Cowboy Bebop.

Uso:
  dotbanner.py "TU FRASE"                  # puntos amarillos + triangulo binario
  dotbanner.py "TU FRASE" --style star     # estrella de binario atravesada por la frase
  dotbanner.py --style star --tilt 30      # mas inclinada (negativo = hacia el otro lado)
  dotbanner.py --style star --fit          # estrella braille (~7 filas) para el arranque de la terminal
  dotbanner.py --style star --classic      # estrella grande de un punto por celda (modo anterior)
  dotbanner.py "TU FRASE" --compact        # puntos mas juntos (terminal angosta)
  dotbanner.py "TU FRASE" --no-binary      # solo el texto de puntos
"""
import argparse
import math
import random
import shutil
import unicodedata

YEL = "\x1b[38;5;214m"  # ambar
AMB = "\x1b[38;5;214m"
BOLD = "\x1b[1m"
RST = "\x1b[0m"

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    " ": ["000"] * 7,
}


def clean(text):
    """Mayusculas y sin acentos (Ñ -> N); lo que no existe en la fuente se omite."""
    text = unicodedata.normalize("NFKD", text.upper())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "".join(c for c in text if c in FONT)


def glyph_width(ch):
    return len(FONT[ch][0])


def line_width(line, cell):
    cols = sum(glyph_width(c) for c in line) + max(len(line) - 1, 0)
    return cols * cell


def wrap(text, avail, cell):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word) if cur else word
        if cur and line_width(trial, cell) > avail:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def render_line(line, cell):
    rows = []
    for r in range(7):
        out = ""
        for i, ch in enumerate(line):
            for bit in FONT[ch][r]:
                out += ("●" + " " * (cell - 1)) if bit == "1" else " " * cell
            if i < len(line) - 1:
                out += " " * cell
        rows.append(YEL + out + RST)
    return rows


def render_text_block(lines, cell):
    block = []
    for n, line in enumerate(lines):
        block += render_line(line, cell)
        if n < len(lines) - 1:
            block.append("")
    return block


def binary_triangle(height, width, rng):
    peak = max(int(height * 0.4), 1)
    rows = []
    for i in range(height):
        if i <= peak:
            w = 2 + (width - 2) * (i / peak) ** 3
        else:
            w = width - (width - 2) * ((i - peak) / max(height - 1 - peak, 1)) ** 0.8
        w = max(2, int(round(w)))
        digits = "".join(rng.choice("01") for _ in range(w))
        if i >= int(height * 0.75):
            gap = 2 + (i - int(height * 0.75)) * 3
            half = max(w // 2, 1)
            digits = digits[:half] + " " * gap + digits[half:]
        rows.append(AMB + digits.center(width + 14).rstrip() + RST)
    return rows


def star_art(lines, size, tilt, rng, overlap=2):
    """Estrella de 5 puntas hecha de 0 y 1, inclinada, con el texto encima."""
    big, small = size, size * 0.42
    h = 2 * size + 3
    cy, cx = h // 2, 2 * size + 2
    verts = []
    for i in range(10):
        rad = big if i % 2 == 0 else small
        phi = math.radians(tilt + i * 36)
        verts.append((cx + 2 * rad * math.sin(phi), cy - rad * math.cos(phi)))

    text_w = max((len(l) for l in lines), default=0)
    w = cx + 2 * size + 3
    grid = [[None] * w for _ in range(h)]

    steps = 150
    for i in range(10):
        (x0, y0), (x1, y1) = verts[i], verts[(i + 1) % 10]
        for t in range(steps + 1):
            col = int(round(x0 + (x1 - x0) * t / steps))
            row = int(round(y0 + (y1 - y0) * t / steps))
            for dc in (0, 1):  # 2 celdas de ancho: las lineas se ven continuas
                if 0 <= row < h and 0 <= col + dc < w:
                    grid[row][col + dc] = (rng.choice("01"), AMB)

    n = len(lines)
    # El texto va a la derecha: solo las primeras letras cruzan el borde de la estrella
    first_row = cy - (n - 1)
    right = max((c for c in range(w) if grid[first_row][c] is not None), default=cx)
    tx = right - (overlap - 1)
    w2 = max(w, tx + text_w + 2)
    for row in grid:
        row.extend([None] * (w2 - w))
    w = w2
    for k, line in enumerate(lines):
        row = cy - (n - 1) + 2 * k
        for j, ch in enumerate(line):
            if ch == " ":
                continue
            # halo para que la letra se lea (no en las que cruzan la estrella)
            for dc in ((0,) if j < overlap else (-1, 0, 1)):
                if 0 <= tx + j + dc < w:
                    grid[row][tx + j + dc] = None
        for j, ch in enumerate(line):
            if ch != " ":
                grid[row][tx + j] = (ch, BOLD + YEL)

    out = []
    for row in grid:
        s = "".join(" " if c is None else c[1] + c[0] + RST for c in row)
        out.append(s.rstrip())
    return out


def big_text(line):
    """Texto grande, en negrita y cursiva, hecho con medios bloques (4 filas de alto)."""
    pix = [[] for _ in range(8)]
    for ch in line:
        g = FONT[ch]
        gw = len(g[0])
        rows = []
        for y in range(7):
            r = [int(b) for b in g[y]]
            if ch != " ":  # negrita: engrosar cada trazo una columna
                r = [(r[x] if x < gw else 0) | (r[x - 1] if x >= 1 else 0) for x in range(gw + 1)]
            rows.append(r + [0])
        rows.append([0] * len(rows[0]))
        for y in range(8):
            pix[y] += rows[y]
    for y in range(8):  # cursiva: las filas de arriba se corren a la derecha
        pix[y] = [0] * ((7 - y) // 4) + pix[y]
    width = max(len(r) for r in pix)
    pix = [r + [0] * (width - len(r)) for r in pix]
    out = []
    for r in range(4):
        row = ""
        for x in range(width):
            t, b = pix[2 * r][x], pix[2 * r + 1][x]
            row += "█" if t and b else "▀" if t else "▄" if b else " "
        out.append(row)
    return out


def star_dots(lines, size, tilt, thick, dot, shift, stagger, big):
    """Estrella hueca de puntos (estilo matriz LED) con el texto saliendo por la derecha."""
    bigr, small = size, size * 0.42
    h = 2 * size + 3
    cy, cg = h // 2, size + 2          # centro (fila, columna de la rejilla)
    wg = 2 * size + 5                  # ancho de la rejilla; cada punto ocupa 2 celdas
    verts = []
    for i in range(10):
        rad = bigr if i % 2 == 0 else small
        phi = math.radians(tilt + i * 36)
        verts.append((cg + rad * math.sin(phi), cy - rad * math.cos(phi)))

    mask = set()
    steps = 400
    offs = range(-(thick // 2), thick - thick // 2)
    for i in range(10):
        (x0, y0), (x1, y1) = verts[i], verts[(i + 1) % 10]
        for t in range(steps + 1):
            col = int(round(x0 + (x1 - x0) * t / steps))
            row = int(round(y0 + (y1 - y0) * t / steps))
            for dy in offs:
                for dx in offs:
                    mask.add((row + dy, col + dx))

    n = len(lines)
    blocks = [big_text(l) if big else [l] for l in lines]
    th = len(blocks[0]) if blocks else 1
    half = 2 * bigr                                  # radio de la estrella en celdas
    tx = [2 * cg + int(shift * half) + int(stagger * half) * k for k in range(n)]
    tops = [cy - 8 + 7 * k if big else cy - 2 + 3 * k for k in range(n)]
    width = max([2 * wg] + [tx[k] + len(blocks[k][0]) + 2 for k in range(n)])
    grid = [[None] * width for _ in range(h)]
    for (row, col) in mask:
        if 0 <= row < h and 0 <= col < wg:
            grid[row][2 * col] = (dot, YEL)

    for k in range(n):
        bw = len(blocks[k][0])
        for r in range(-1, th + 1):
            row = tops[k] + r
            if not 0 <= row < h:
                continue
            for c in range(tx[k] - 2, tx[k] + bw + 2):  # hueco para que se lea
                if 0 <= c < width and (not big or 0 <= r < th or True):
                    grid[row][c] = None
        for r, rowstr in enumerate(blocks[k]):
            row = tops[k] + r
            if not 0 <= row < h:
                continue
            style = YEL if big else "\x1b[1;3m" + YEL
            for j, chx in enumerate(rowstr):
                if chx != " ":
                    grid[row][tx[k] + j] = (chx, style)

    out = []
    for row in grid:
        s_ = "".join(" " if c is None else c[1] + c[0] + RST for c in row)
        out.append(s_.rstrip())
    return out


BRAILLE_BITS = ((0x01, 0x08), (0x02, 0x10), (0x04, 0x20), (0x40, 0x80))  # [fila][columna]


def star_braille(lines, size, tilt, thick, shift, stagger):
    """La misma estrella hueca de star_dots, pero dibujada con puntos braille.

    Cada celda de la terminal guarda 2x4 puntos, asi que la estrella queda
    ~4 veces mas baja y ~2 veces mas angosta que en el modo clasico, con la
    misma forma. El texto va en celdas normales (negrita + cursiva)."""
    bigr, small = size, size * 0.42
    cy = cx = size + 2.0
    verts = []
    for i in range(10):
        rad = bigr if i % 2 == 0 else small
        phi = math.radians(tilt + i * 36)
        verts.append((cx + rad * math.sin(phi), cy - rad * math.cos(phi)))

    mask = set()
    steps = 400
    offs = range(-(thick // 2), thick - thick // 2)
    for i in range(10):
        (x0, y0), (x1, y1) = verts[i], verts[(i + 1) % 10]
        for t in range(steps + 1):
            col = int(round(x0 + (x1 - x0) * t / steps))
            row = int(round(y0 + (y1 - y0) * t / steps))
            for dy in offs:
                for dx in offs:
                    mask.add((row + dy, col + dx))

    min_r = min(r for r, _ in mask)
    min_c = min(c for _, c in mask)
    mask = {(r - min_r, c - min_c) for r, c in mask}
    n_rows = max(r for r, _ in mask) // 4 + 1
    n_cols = max(c for _, c in mask) // 2 + 1

    cells = [[0] * n_cols for _ in range(n_rows)]
    for r, c in mask:
        cells[r // 4][c // 2] |= BRAILLE_BITS[r % 4][c % 2]

    n = len(lines)
    half = size / 2                                  # radio de la estrella en celdas
    ccol = (cx - min_c) / 2                          # columna central (celdas)
    crow = n_rows // 2
    tx = [int(round(ccol + shift * half)) + int(round(stagger * half)) * k for k in range(n)]
    trow = [crow - 1 + k for k in range(n)]
    width = max([n_cols] + [tx[k] + len(lines[k]) + 2 for k in range(n)])

    grid = [[None] * width for _ in range(n_rows)]
    for r in range(n_rows):
        for c in range(n_cols):
            if cells[r][c]:
                grid[r][c] = (chr(0x2800 + cells[r][c]), YEL)

    style = "\x1b[1;3m" + YEL
    for k in range(n):
        row = trow[k]
        if not 0 <= row < n_rows:
            continue
        for c in range(tx[k] - 1, tx[k] + len(lines[k]) + 1):  # hueco para que se lea
            if 0 <= c < width:
                grid[row][c] = None
        for j, ch in enumerate(lines[k]):
            if ch != " ":
                grid[row][tx[k] + j] = (ch, style)

    out = []
    for row in grid:
        out.append("".join(" " if c is None else c[1] + c[0] + RST for c in row).rstrip())
    return out


def split_two(text):
    words = text.split()
    best, best_diff = 1, 10**9
    for k in range(1, len(words)):
        diff = abs(len(" ".join(words[:k])) - len(" ".join(words[k:])))
        if diff < best_diff:
            best, best_diff = k, diff
    if len(words) < 2:
        return [text]
    return [" ".join(words[:best]), " ".join(words[best:])]


def side_by_side(left, right, gap=4):
    h = max(len(left), len(right))
    lw = max(len(strip(x)) for x in left) if left else 0
    top_l = (h - len(left)) // 2
    top_r = (h - len(right)) // 2
    out = []
    for i in range(h):
        l = left[i - top_l] if 0 <= i - top_l < len(left) else ""
        r = right[i - top_r] if 0 <= i - top_r < len(right) else ""
        pad = " " * (lw - len(strip(l)))
        out.append(l + pad + " " * gap + r)
    return out


def strip(s):
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phrase", nargs="?", default="")
    ap.add_argument("--style", choices=["dots", "star"], default="dots")
    ap.add_argument("--compact", action="store_true")
    ap.add_argument("--no-binary", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--size", type=int, default=None,
                    help="tamano de la estrella (braille: 13 = imagen de referencia; --classic: 22)")
    ap.add_argument("--classic", action="store_true",
                    help="estrella grande de un punto por celda (el modo anterior)")
    ap.add_argument("--overlap", type=int, default=2, help="cuantas letras cruzan el borde de la estrella")
    ap.add_argument("--fill", choices=["dots", "binary"], default="dots",
                    help="estrella de puntos (como la referencia) o de ceros y unos")
    ap.add_argument("--thick", type=int, default=None, help="grosor de la estrella (puntos)")
    ap.add_argument("--text", choices=["big", "small"], default=None, help="texto grande (bloques) o de una fila")
    ap.add_argument("--dot", default="●", help="caracter de los puntos")
    ap.add_argument("--shift", type=float, default=0.32, help="donde empieza el texto (0 = centro, 1 = borde derecho)")
    ap.add_argument("--stagger", type=float, default=0.36, help="cuanto se corre la 2da linea a la derecha")
    ap.add_argument("--tilt", type=float, default=None, help="inclinacion en grados (+ hacia el texto)")
    ap.add_argument("--fit", action="store_true",
                    help="achica el dibujo para que quepa en la terminal (ideal para el arranque)")
    a = ap.parse_args()

    cols = shutil.get_terminal_size((120, 30)).columns

    if a.style == "star":
        phrase = clean(a.phrase or "SEE YOU SPACE COWBOY . . .")
        rows_avail = shutil.get_terminal_size((120, 30)).lines

        def make(size):
            if a.fill == "binary":
                tilt = 20 if a.tilt is None else a.tilt
                return star_art(split_two(phrase), size, tilt, random.Random(a.seed), a.overlap)
            tilt = -27 if a.tilt is None else a.tilt
            if not a.classic:  # por defecto: puntos braille, tamano de la imagen de referencia
                return star_braille(split_two(phrase), size, tilt, a.thick or 3, a.shift, a.stagger)
            big = (size >= 15) if a.text is None else (a.text == "big")
            thick = a.thick if a.thick else (3 if size >= 15 else 2)
            return star_dots(split_two(phrase), size, tilt, thick, a.dot, a.shift, a.stagger, big)

        def fits(art):
            return len(art) + 3 <= rows_avail and max(len(strip(x)) for x in art) <= cols

        default_size = 9 if a.fill == "binary" else (22 if a.classic else 13)
        size = a.size if a.size is not None else default_size
        art = make(size)
        if a.fit:  # achica el dibujo hasta que quepa en la terminal; si no cabe, no muestra nada
            while size > 5 and not fits(art):
                size -= 1
                art = make(size)
            if not fits(art):
                return
    else:
        phrase = clean(a.phrase or "AD ASTRA PER ASPERA")
        cell = 1 if a.compact else 2
        left_w = 0 if a.no_binary else 40
        lines = wrap(phrase, cols - left_w - 4, cell)
        if cell == 2 and any(line_width(l, 2) > cols - left_w - 4 for l in lines):
            cell = 1
            lines = wrap(phrase, cols - left_w - 4, cell)
        block = render_text_block(lines, cell)
        if a.no_binary:
            art = block
        else:
            tri = binary_triangle(len(block), 26, random.Random(a.seed))
            art = side_by_side(tri, block, gap=2)

    print("\n".join(art))


if __name__ == "__main__":
    main()
