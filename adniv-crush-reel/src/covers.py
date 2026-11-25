import sys; sys.path.insert(0, '.')
from grade import frame
from overlay import *

X0 = 72


def cover_logo(c, dark=False):
    # y=300 keeps the logo inside the 4:5 (y285-1635) and 3:4 (y240-1680) grid crops
    place(c, logo(280, dark), 1008, 300, anchor="rt", depth_kw=dict(soft=(0, 4, 12, .5), tight=(0, 1, 2, .4)))


def bar_line(text, font, fg, bg, padx=22, pady=12):
    t = text_img(text, font, fg, tracking=-1)
    asc, desc = font.getmetrics()
    b = rounded((t.width + 2 * padx, asc + desc + 2 * pady - 8), 10, bg)
    b.alpha_composite(t, (padx, pady - 6))
    return b


def cover1():
    """Donut hero: product-as-hero, name-drop the project."""
    c = Image.fromarray(frame("IMG_4903", 2.4)).convert("RGBA")
    k = text_img("CRUSH SALON  ·  GURGAON", F("Inter-Bold", 30), ORANGE, tracking=6)
    place(c, k, X0, 1150)
    place(c, text_img("Lit by Adniv.", F("InterDisplay-Bold", 138), WHITE, tracking=-3), X0 - 6, 1196,
          depth_kw=dict(soft=(0, 12, 26, .6), tight=(0, 3, 3, .45)))
    place(c, text_img("Donut pendants  ·  Panels  ·  Dome lights", F("Inter-Medium", 34), WHITE), X0, 1378)
    cover_logo(c)
    return c.convert("RGB")


def cover2():
    """Wide salon: question hook in solid navy label bars over the bright ceiling."""
    c = Image.fromarray(frame("IMG_4905", 0.6)).convert("RGBA")
    k = chip("PROJECT  ·  CRUSH SALON, GURGAON", F("Inter-Bold", 24), bg=ORANGE + (255,), fg=WHITE, dot=None, padx=18, h=48, r=10)
    place(c, k, X0, 420)
    f = F("InterDisplay-Bold", 92)
    place(c, bar_line("How CRUSH Salon", f, WHITE, NAVY + (255,)), X0, 484, depth_kw=dict(soft=(0, 12, 22, .45), tight=(0, 2, 3, .3)))
    place(c, bar_line("got its glow.", f, WHITE, NAVY + (255,)), X0, 606, depth_kw=dict(soft=(0, 12, 22, .45), tight=(0, 2, 3, .3)))
    cover_logo(c, dark=True)
    return c.convert("RGB")


def cover3():
    """Warm domes: direct question to salon owners (the buyer)."""
    c = Image.fromarray(frame("IMG_4896", 1.4)).convert("RGBA")
    place(c, text_img("FOR SALON OWNERS", F("Inter-Bold", 30), ORANGE, tracking=6), X0, 1080)
    f = F("InterDisplay-Bold", 120)
    place(c, text_img("Your salon,", f, WHITE, tracking=-3), X0 - 6, 1124, depth_kw=dict(soft=(0, 12, 26, .65), tight=(0, 3, 3, .5)))
    place(c, text_img("lit like this?", f, WHITE, tracking=-3), X0 - 6, 1262, depth_kw=dict(soft=(0, 12, 26, .65), tight=(0, 3, 3, .5)))
    place(c, chip("CRUSH Salon, Gurgaon  ·  by Adniv", F("Inter-SemiBold", 28), padx=20, h=56, r=28), X0, 1420)
    cover_logo(c)
    return c.convert("RGB")


def grid_check(im, name):
    a = im.convert("RGBA")
    ov = Image.new("RGBA", a.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle((0, 285, 1079, 1634), outline=(0, 255, 120, 255), width=6)
    d.rectangle((0, 240, 1079, 1679), outline=(80, 180, 255, 255), width=4)
    d.text((20, 292), "4:5 grid crop", font=F("Inter-Bold", 28), fill=(0, 255, 120))
    d.text((20, 200), "3:4 grid crop (current IG profile grid)", font=F("Inter-Bold", 28), fill=(80, 180, 255))
    full = Image.alpha_composite(a, ov).convert("RGB").resize((540, 960), Image.LANCZOS)
    c45 = im.crop((0, 285, 1080, 1635)).resize((540, 675), Image.LANCZOS)
    c34 = im.crop((0, 240, 1080, 1680)).resize((540, 720), Image.LANCZOS)
    out = Image.new("RGB", (540 * 3 + 40, 1000), (24, 24, 28))
    out.paste(full, (0, 40)); out.paste(c45, (560, 40)); out.paste(c34, (1120, 40))
    dd = ImageDraw.Draw(out); ff = F("Inter-Bold", 26)
    for x, l in [(0, "9:16 reel cover"), (560, "4:5 centre crop"), (1120, "3:4 centre crop")]:
        dd.text((x + 10, 6), l, font=ff, fill="white")
    out.save(f"samples/{name}_gridcheck.jpg", quality=88)


if __name__ == "__main__":
    for i, fn in enumerate([cover1, cover2, cover3], 1):
        im = fn(); im.save(f"samples/cover{i}.png"); grid_check(im, f"cover{i}")
        safe_overlay(im).convert("RGB").save(f"samples/cover{i}_safezone.jpg", quality=85)
        print("cover", i)
