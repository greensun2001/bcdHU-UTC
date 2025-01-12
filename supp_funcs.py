from random import random, randint


def colorBetween(r1, g1, b1, r2, g2, b2, n_c):
    colors = []
    colors.append((r1, g1, b1))
    if n_c > 1:
        sr = (r2 - r1) / n_c
        sg = (g2 - g1) / n_c
        sb = (b2 - b1) / n_c
        for i in range(n_c):
            r = r1 + (i + 1) * sr
            g = g1 + (i + 1) * sg
            b = b1 + (i + 1) * sb
            colors.append((r, g, b))
    return colors


def randColor(i: int = 0):
    l = ["#ff0000", "#0000ff", "#08a108", "#ea00ff", "#04a3a3", "#96a008", "#006666"]

    if i < 7:
        color = l[i]
    else:
        color = (random(), random(), random())
    return color


def randMarker(i: int = 0):
    lstMk = [
        "o",
        "x",
        "s",
        "*",
        "D",
        "v",
        "8",
        "^",
        "2",
        "p",
        "<",
        ">",
        "1",
        "3",
        "4",
        "P",
        "h",
        "H",
        "+",
        "X",
        "d",
        "|",
        "_",
    ]
    if i > 22:
        i = randint(0, 22)
    return lstMk[i]
