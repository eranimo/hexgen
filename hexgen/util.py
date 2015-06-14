import random

def blend_colors(color1, color2):
    return min(round((color1[0] + color2[0]) / 2), 255), \
           min(round((color1[1] + color2[1]) / 2), 255), \
           min(round((color1[2] + color2[2]) / 2), 255)

def lighten(color, amount):
    return min(round(color[0] + color[0] * amount), 255), \
           min(round(color[1] + color[1] * amount), 255), \
           min(round(color[2] + color[2] * amount), 255)

def randomize_color(color, dist=1):
    colors = [
        color,
        (color[0] - dist, color[dist] - dist, color[2] - dist),
        (color[0] + dist, color[dist] + dist, color[2] + dist),
        (color[0] - dist, color[dist] + dist, color[2] - dist),
        (color[0] + dist, color[dist] - dist, color[2] - dist),
        (color[0] - dist, color[dist] + dist, color[2] - dist),
        (color[0] - dist, color[dist] - dist, color[2] + dist),
        (color[0] + dist, color[dist] - dist, color[2] + dist),
        (color[0] - dist, color[dist] + dist, color[2] - dist)
    ]
    return random.choice(colors)
