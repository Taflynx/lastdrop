"""Classika water sensor housing - parametric CadQuery model.
Coordinates (assembled): tank narrow face at x=0 (machine side is +x), y up from tank bottom, z across the narrow face.
ASSUMED values are marked; change them and re-run after measuring."""
import cadquery as cq
import numpy as np
# ---- ASSUMED tank / machine values (measure and update) ----
RIM   = 250.0   # E: tank height 25 cm (ECM P9010 tank spec; measured approx. 240)
B     = 3.0     # B: rim wall thickness at the top
# ---- measured parts ----
FD, FT, BD, TOT, CAB, CAB_FROM_BACK = 28.23, 3.98, 25.53, 16.73, 3.67, 5.0   # XKC-Y25
ATOM = (9.5, 24.0, 24.0)                                                    # x, y, z
WAGO = (8.2, 18.19, 13.1)  # measured by Igal
# ---- design values ----
CL = 0.3; T = 1.6
SLOT, LIP, BAR = B + 0.4, 2.5, 2.5
BX0, BX1, BZ = 0.0, 16.0, 31.0           # box depth and half width
YB1 = RIM - 14.0; YB0 = YB1 - 85.0       # box top / bottom (7 mm taller: cable passages under and over the Wagos)
RX0, RX1, RZ0, RZ1 = 6.0, 14.0, 21.0, 27.0   # rail section (x and |z|)
RAILB, LAP = 8.0, 22.0   # pad 8 mm above the assumed bottom, margin for the approximate height
PIN_D, PIN_H = 3.0, 3.25
JF, JM, JB, JZ0, JY0 = 1.0, 8.0, 15.5, 13.0, YB1 - 85.0 - 32.0   # screw joint: front block x JF..JM (threaded), stub x JM..JB, inner z, block bottom y
SCREW_CLR = 6.6
ATOM_GAP = 4.5                          # gap port face -> back wall: Grove plug 4.38, its wires leave sideways (per Igal, 2 mm closer)
USB_W, USB_H = 13.0, 7.4                # generic USB-C plug window (overmold up to ~12.5 x 7)
GPLUG = (11.0, 6.5)                     # Grove plug pass-through (x length, z width)
DOOR_TABS = 3
WIRE_ROOM, RIB_T, RIB_H = 15.0, 1.6, 5.0
WAGO_RECESS = 1.0
CAB_HOLE = 5.0                          # round hole for the 3.67 mm sensor cable (4.0 printed too tight)
PASS_H = 4.6                            # cable passages under the lowest and over the top Wago
CAB_X = 8.0                             # floor hole for the sensor cable: centred in the 16 mm floor, 5.5 mm of wall each side
CLIP_D, CLIP_SLOT, CLIP_L = 4.6, 3.1, 8.0    # clip bore under the floor hole: 4.6 per Igal (4.47 still tight)
BRIDGE_BORE = 4.8                       # carriage bridge ring for the cable (snap slot stays 3.1)
USB_HALF_X = 4.6                        # window edge on the tank side (kept as printed, per Igal)
SIDE_CUT_BACK = 2.0                     # side opening starts 2 mm behind the stop line (covers more of the USB)
LED_SLOT, LED_SLOT_R = (1.2, 3.2), 0.5                   # LED window: ATOM LED bar is 1 x 3 mm (Igal), +0.2 so the printed slot is not smaller
SEAT_D, NECK_W = 4.0, 3.5                # head peg seat and click neck in the carriage (was 4.1 / 3.75: head fell out too easily)
SLIDE_CL, TOOTH_IN = 0.28, 0.55            # carriage-on-rail clearance per side (0.2 too stiff, 0.35 too loose), latch bite
CAB_HEAD_X = 0.3 + 16.73 - 5.0         # cable position on the head (5 mm from the sensor's narrow end)
LID_TABS, LID_T0, LID_P, LID_TL, LID_SLIDE = 4, YB1 - 85.0 + 2.8, 20.0, 7.2, 8.0   # lid tabs: count, first start y, pitch, length, slide
# ---- branding engraved on the LED face (x = BX1), sized for a 0.4 nozzle / 0.2 layers: every stroke >= 0.6 mm
NAME, NAME_W, NAME_D = "Lastdrop", 34.0, 0.6     # Parisienne script: ink width along z, engrave depth
NAME_GROW = 0.20                                 # outline grown per side: the script's hairlines are ~0.2 mm otherwise
# byline in the taflev.com style: label in Geist Mono caps with wide spacing; site name = "taflev" Geist 600 + ".com" Instrument Serif italic
# line: (text, cap/x height, extra letter spacing, grow) in BYLINE_FONT, or a dict of font segments on one baseline (see branding.rich_line)
import os
_F = lambda n: os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", n)
BYLINE = [("BY IGAL TAFLEV", 1.8, 0.35, 0.15),
          {"h": 2.1, "ref": "x", "segments": [("taflev", _F("Geist-600.ttf"), 0.0, 0.10),
                                              (".com", _F("InstrumentSerif-Italic.ttf"), 0.0, 0.18)]}]
BYLINE_GROW = 0.15
DROP_R, DROP_TIP, DROP_LINE = 3.4, 2.25, 0.8    # logo: water drop outline (radius, tip distance / R, line width), low water inside
GAPS = (2.2, 2.6, 1.5)                          # drop -> name -> byline -> url
import os
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
NAME_FONT = os.path.join(FONTS, "Parisienne-Regular.ttf")
BYLINE_FONT = os.path.join(FONTS, "GeistMono-400.ttf")   # fixed instances of the variable fonts, made with fontTools

def bx(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))
def cyl(d, axis, p0, length):
    wp = {"x": cq.Workplane("YZ"), "y": cq.Workplane("XZ"), "z": cq.Workplane("XY")}[axis]
    c = wp.circle(d/2).extrude(length)
    if axis == "y": c = c.mirror("XZ")
    return c.translate(p0)

# ---------------- top frame: hook + box + rail stubs ----------------
# Housing sits on the LEFT narrow end of the tank (seen from the machine front):
# +x = toward the machine's left wall, +z = toward the back of the machine.
# Tank top: wall TW thick (x -TW..0), rim flange FL_T thick sticking out FL_W from the wall (x up to FL_W).
# Install path (checked in check_install.py): lower into the gap ~9 mm away from the tank and ~9 mm above the rim,
# push horizontally toward the tank, then press down: inner lip drops into the tank, fingers click under the flange.
TW = 3.0                           # ASSUMED tank wall thickness under the flange (same as the flange)
HOOK_W, BAR_T = 56.0, 3.0          # bar 3 mm thick (was 5: too high under the lid), 56 wide (was 40) to keep it strong
FL_T, FL_W = 3.0, 7.23             # flange thickness and how far it sticks out (measured)
LIP_L, LIP_T, LIP_CL = 8.0, 3.0, 0.5
TX = 2.4                           # front and back box walls, thick enough for the lid grooves
FX0, FX1 = FL_W + 0.4, FL_W + 2.4  # snap fingers just outside the flange edge
NECK_X = FX1 + 1.3                 # gap that lets the fingers flex outward
NAME_YC = (YB0 + RIM + BAR_T)/2   # middle of the LED face, box bottom to hook top: drop tip and lowest text line centred on it
HOOK_R, HOOK_EDGE_R = 2.5, 1.0      # rounded top: profile corners (bar is 3 mm, so < 3) and the top-face edges
def hook():
    xl1 = -(TW + LIP_CL); xl0 = xl1 - LIP_T
    top, r = RIM + BAR_T, HOOK_R
    def profile():                                         # same outline as before, the two top corners now arcs
        a = 0.29289 * r                                    # (1 - cos 45) * r: arc mid point
        return (cq.Workplane("XY").moveTo(xl0, RIM-LIP_L+1.0).lineTo(xl0+1.0, RIM-LIP_L).lineTo(xl1, RIM-LIP_L)
                .lineTo(xl1, RIM).lineTo(NECK_X, RIM).lineTo(NECK_X, YB1-0.8).lineTo(BX1, YB1-0.8).lineTo(BX1, top-r)
                .threePointArc((BX1-a, top-a), (BX1-r, top)).lineTo(xl0+r, top)
                .threePointArc((xl0+a, top-a), (xl0, top-r)).close())
    h = profile().extrude(HOOK_W).translate((0, 0, -HOOK_W/2))
    # outside the tank the hook is as wide as the box (2*BZ), so its sides line up with the box sides.
    # The lip inside the tank stays HOOK_W (tank width not measured), and the wide part starts at the box top (YB1)
    # so the lid / door grooves and the lid stop in the roof are unchanged.
    wide = profile().extrude(2*BZ).translate((0, 0, -BZ))
    wide = wide.intersect(bx(xl0-1, BX1+1, YB1, top+1, -BZ-1, BZ+1)).cut(bx(xl0-1, 0.0, YB1-1, RIM, -BZ-1, BZ+1))
    h = h.union(wide)
    try:
        h = h.edges(cq.selectors.BoxSelector((xl0-2, top-0.01, -BZ-1), (BX1+2, top+0.01, BZ+1))).fillet(HOOK_EDGE_R)
    except Exception as e:
        print("hook top-edge fillet skipped:", e)
    for s in (1, -1):                                      # two snap fingers, rooted in the box roof
        z0, z1 = sorted((s*8.0, s*18.0))
        fy1 = RIM - FL_T - 0.3
        fing = bx(FX0, FX1, YB1-0.8, fy1, z0, z1)
        tooth = (cq.Workplane("XY").polyline([(FX0+0.01, fy1), (FL_W-0.83, fy1), (FL_W-0.83, fy1-0.3), (FX0+0.01, fy1-2.2)])
                 .close().extrude(z1-z0).translate((0, 0, z0)))   # flat top catches the flange, ramp below for the click
        tab_z0, tab_z1 = sorted((s*18.0, s*25.0))
        tab = bx(FX0, FX1+0.6, fy1-6.0, fy1, tab_z0, tab_z1)                # release tab: push it outward (+x)
        h = h.union(fing).union(tooth).union(tab)
    return h

def top_frame():
    f = bx(BX0, BX1, YB0, YB1, -BZ, BZ).cut(bx(BX0+TX, BX1-TX, YB0+T, YB1-T, -BZ-1, BZ-T))   # open on the -z (front) side
    # sliding-lid grooves in the front and back walls, a slot in the floor to slide the lid in from below, stop in the roof
    gz0, gz1 = -BZ+1.2, -BZ+3.4
    f = f.cut(bx(TX-1.2, TX+0.01, YB0-1, YB1-T+1.2, gz0, gz1)).cut(bx(BX1-TX-0.01, BX1-TX+1.2, YB0-1, YB1-T+1.2, gz0, gz1))
    f = f.cut(bx(TX-1.2, BX1-TX+1.2, YB0-1, YB0+T+0.01, gz0, gz1)).cut(bx(TX+0.01, BX1-TX-0.01, YB0-1, YB0+T+0.01, -BZ-1, gz1))  # floor slot, open to the outside so the lid can lift
    f = f.cut(bx(TX-1.5, TX-1.19, YB0+2.8, YB0+6.2, gz0, gz1)).cut(bx(BX1-TX+1.19, BX1-TX+1.5, YB0+2.8, YB0+6.2, gz0, gz1))  # click notches
    for k in range(LID_TABS):                                           # slide-and-lift: windows in the outer groove lips
        w0 = LID_T0 + LID_P*k - LID_SLIDE - 0.5
        f = f.cut(bx(TX-1.2, TX+0.01, w0, w0+LID_TL+1.0, -BZ-1, gz0+0.01)).cut(bx(BX1-TX-0.01, BX1-TX+1.2, w0, w0+LID_TL+1.0, -BZ-1, gz0+0.01))
    f = f.union(hook())
    ix0, ix1 = BX0+TX, BX1-TX                 # inside, x (tank side .. machine-wall side)
    zin = gz1 + 0.3                           # inside face of the lid (machine-front side)
    zb = BZ - T                               # inside face of the back wall (machine-back side)
    # ---- everything sits toward the machine BACK (+z). ATOM at the top, ports toward the back wall,
    # 8 mm in front of the ports for the Grove plug (4.38) and its bend; the Grove cable drops straight down
    # through the shelf to the Wagos. A door in the back wall (below the USB window) gives access to the Wagos.
    ax0 = ix1 - ATOM[0] - 0.1                 # ATOM against the machine-wall side (LED at its window); free gap on the tank side
    ay0 = YB1 - T - ATOM[1] - 0.5
    ze = zb - ATOM_GAP; za = ze - ATOM[2]
    f = f.union(bx(ix0, ix1, ay0-T, ay0, zin, zb))                                      # shelf
    for yy in (ay0, ay0+ATOM[1]-2.0):
        f = f.union(bx(ix0-0.01, ax0, yy, yy+2.0, za, zb))                                # rails on the tank side (the gap between them stays free)
        f = f.union(bx(ax0, ax0+ATOM[0]+0.1, yy, yy+2.5, ze, ze+1.5))                     # port-side stops at the corners
    usb_x = ax0 + ATOM[0] - 2.15              # USB-C port centre (button half of the ATOM)
    # window centred on the port, open through the corner on the machine-wall side so a thick plug fits
    win = bx(usb_x-USB_HALF_X, BX1+1, ay0+12-USB_W/2, ay0+12+USB_W/2, zb-1, BZ+1).edges("|Z and <X").fillet(2.5)
    f = f.cut(win)
    f = f.cut(bx(ix1-0.01, BX1+1, ay0+12-USB_W/2, ay0+12+USB_W/2, ze+SIDE_CUT_BACK, BZ+1))   # machine-wall side open, 2 mm less than before
    lz = (za+ze)/2
    f = f.cut(bx(ix1-1, BX1+1, ay0+12-LED_SLOT[1]/2, ay0+12+LED_SLOT[1]/2, lz-LED_SLOT[0]/2, lz+LED_SLOT[0]/2)
              .edges("|X").fillet(LED_SLOT_R))   # LED window: narrow slot, corners rounded (almost a pill)
    f = f.cut(bx(ix0+0.2, ix1-0.2, ay0-T-1, ay0+1, zin+8.5, zin+8.5+GPLUG[1]))          # Grove plug drop-through, 8 mm in from the shelf edge, over the cable-storage area
    # ---- door in the back wall, from the floor up to the shelf (slide-and-lift, same as the lid)
    dz0, dz1 = BZ-3.4, BZ-1.2
    yd1 = ay0 - T
    f = f.cut(bx(ix0, ix1, YB0-1, yd1, dz0-0.1, BZ+1))                                   # opening
    f = f.cut(bx(TX-1.2, TX+0.01, YB0-1, yd1, dz0, dz1)).cut(bx(BX1-TX-0.01, BX1-TX+1.2, YB0-1, yd1, dz0, dz1))   # grooves
    f = f.cut(bx(TX-1.2, BX1-TX+1.2, YB0-1, YB0+T+0.01, dz0, dz1))                       # floor slot
    f = f.cut(bx(TX-1.5, TX-1.19, YB0+2.8, YB0+6.2, dz0, dz1)).cut(bx(BX1-TX+1.19, BX1-TX+1.5, YB0+2.8, YB0+6.2, dz0, dz1))  # click notches
    for k in range(DOOR_TABS):
        w0 = LID_T0 + LID_P*k - LID_SLIDE - 0.5
        f = f.cut(bx(TX-1.2, TX+0.01, w0, w0+LID_TL+1.0, dz1-0.01, BZ+1)).cut(bx(BX1-TX-0.01, BX1-TX+1.2, w0, w0+LID_TL+1.0, dz1-0.01, BZ+1))
    # ---- 3 Wago lying flat on the tank-side wall, stacked, wire entries facing the door
    wz1 = dz0 - WIRE_ROOM                                                                 # wire-entry face
    wz0 = wz1 - WAGO[1]                                                                   # back end
    # each Wago has its own track: full-length rails below and above it (they never touch each other),
    # small bumps near the entry end click over the Wago when it is pushed in, a stop wall behind
    wy = [YB0 + T + PASS_H + RIB_T + i*(WAGO[2] + 0.1 + RIB_T) for i in range(3)]   # free passage under the lowest one
    # the Wagos sit 1 mm into the tank-side wall (wall 1.4 mm there), so 4 mm stay free above them
    # for the sensor cable to pass to the storage space behind them, without making the box thicker
    f = f.cut(bx(ix0-WAGO_RECESS, ix0+0.01, YB0+T, wy[-1]+WAGO[2]+0.1+RIB_T, wz0-1.6, BZ-3.5))   # recess runs up to the door groove
    ix0 = ix0 - WAGO_RECESS
    f = f.union(bx(ix0, ix0+WAGO[0]-1.0, wy[0]-RIB_T, wy[-1]+WAGO[2]+0.1+RIB_T, wz0-1.6, wz0))  # stop wall behind them (passages stay open)
    rails_y = [wy[0]-RIB_T] + [w + WAGO[2] + 0.1 for w in wy]
    for k, y0 in enumerate(rails_y):
        f = f.union(bx(ix0, ix0+RIB_H, y0, y0+RIB_T, wz0, wz1))
        if k > 0:                                                                         # bump into the Wago below
            f = f.union(bx(ix0, ix0+RIB_H, y0-0.25, y0, wz1-2.0, wz1-0.6))
        if k < 3:                                                                         # bump into the Wago above
            f = f.union(bx(ix0, ix0+RIB_H, y0+RIB_T, y0+RIB_T+0.25, wz1-2.0, wz1-0.6))
    for w in wy:                                                                          # push-out slot through the inner stop wall,
        f = f.cut(bx(ix0+1.0, ix0+6.0, w+WAGO[2]/2-1.8, w+WAGO[2]/2+1.8, wz0-2.0, wz0+0.01))  # from the cable-storage side, one per Wago
    # ---- sensor cable: comes straight up between the rails into a round hole in the floor, right into the
    # passage under the lowest Wago; a thick C clip under the floor holds it
    f = f.cut(cq.Workplane().add(cq.Solid.makeCylinder(CAB_HOLE/2, T+2, cq.Vector(CAB_X, YB0-1, 0), cq.Vector(0, 1, 0))))
    clip = bx(CAB_X-4.6, CAB_X+4.0, YB0-CLIP_L, YB0+0.01, -4.5, 4.5).edges("|Y").fillet(1.0)
    clip = clip.cut(cq.Workplane().add(cq.Solid.makeCylinder(CLIP_D/2, CLIP_L+2, cq.Vector(CAB_X, YB0-CLIP_L-1, 0), cq.Vector(0, 1, 0))))
    f = f.union(clip)
    for s in (1, -1):                                                    # joint stubs: clearance holes for the M6 thumb screws
        z0, z1 = sorted((s*JZ0, s*RZ1))
        st = bx(JM, JB, YB0-LAP, YB0+0.01, z0, z1)
        for yy in (YB0-5.5, YB0-16.0):
            st = st.cut(cyl(SCREW_CLR, "x", (JM-1, yy, s*(JZ0+RZ1)/2), JB-JM+2))
        f = f.union(st)
    if NAME:
        f = f.cut(name_cutter())
    return f

# Branding (branding.py draws it flat in 2D, grown so every stroke prints), engraved NAME_D deep in the LED face.
# Flat drawing (u right, v up) -> face: u -> -z (reads left to right when you face that side), v -> +y.
# Coloured pieces (printed with the AMS): their pocket is COLOR_POCKET deep and the colour fills it up to COLOR_SUNK
# under the surface, so they stay sunk with the colour at the bottom.
COLORS = {"drop_ring": "turquoise", "water": "turquoise", "name": "turquoise"}      # piece -> colour part; everything else stays a plain engraving
COLOR_POCKET, COLOR_SUNK = 1.0, 0.4
def _branding():
    import branding
    return branding, branding.layout(NAME_FONT, BYLINE_FONT, NAME, NAME_W, NAME_GROW, BYLINE, BYLINE_GROW,
                                     (DROP_R, DROP_TIP, DROP_LINE), GAPS)
def _slab(shape, x0, x1):
    branding, _ = _branding.cache
    yc = NAME_YC
    def w3(coords):
        return cq.Wire.makePolygon([cq.Vector(x0, yc + v, -u) for u, v in list(coords)[:-1]], close=True)
    sol = None
    for p in branding.polygons(shape):
        if p.is_empty:
            continue
        face = cq.Face.makeFromWires(w3(p.exterior.coords), [w3(i.coords) for i in p.interiors])
        s = cq.Solid.extrudeLinear(face, cq.Vector(x1 - x0, 0, 0))
        sol = s if sol is None else sol.fuse(s)
    return cq.Workplane().add(sol.clean())
def name_cutter():
    if not hasattr(_branding, "cache"):
        _branding.cache = _branding()
    branding, (allshape, pieces) = _branding.cache
    from shapely.ops import unary_union
    c = _slab(allshape, BX1 - NAME_D, BX1 + 0.3)
    deep = unary_union([pieces[k] for k in COLORS])
    return c.union(_slab(deep, BX1 - COLOR_POCKET, BX1 + 0.3))
def color_parts():
    if not hasattr(_branding, "cache"):
        _branding.cache = _branding()
    branding, (allshape, pieces) = _branding.cache
    from shapely.ops import unary_union
    out = {}
    for col in sorted(set(COLORS.values())):
        sh = unary_union([pieces[k] for k, c in COLORS.items() if c == col])
        out[f"brand_{col}"] = _slab(sh, BX1 - COLOR_POCKET, BX1 - COLOR_SUNK)
    return out

# ---------------- sliding lid (front, -z side) ----------------
def lid():
    # Slide-and-lift lid: 4 tabs per edge run in the grooves. Pull the finger tab down 8 mm (past the click),
    # the tabs line up with the windows in the groove lips, and the lid lifts straight off. No need to move the sensor.
    gz0, gz1 = -BZ+1.2, -BZ+3.4
    y1 = YB1 - T - 0.2
    p = bx(TX+0.15, BX1-TX-0.15, YB0, y1, gz0+0.1, gz1-0.1)                              # plate, fits between the walls
    for k in range(LID_TABS):
        t0 = LID_T0 + LID_P*k
        p = p.union(bx(TX-1.0, TX+0.2, t0, t0+LID_TL, gz0+0.1, gz1-0.1)).union(bx(BX1-TX-0.2, BX1-TX+1.0, t0, t0+LID_TL, gz0+0.1, gz1-0.1))
    p = p.union(bx(TX-1.25, TX-1.0, YB0+3.0, YB0+6.0, gz0+0.1, gz1-0.1)).union(bx(BX1-TX+1.0, BX1-TX+1.25, YB0+3.0, YB0+6.0, gz0+0.1, gz1-0.1))  # click bumps
    p = p.union(bx(5.0, 11.0, YB0-5.0, YB0+0.0, -BZ, gz1-0.1))                         # finger tab below the box
    return p

def door():
    # Same slide-and-lift idea as the lid, on the machine-back wall, from the floor up to the shelf.
    dz0, dz1 = BZ-3.4, BZ-1.2
    ay0 = YB1 - T - ATOM[1] - 0.5
    y1 = ay0 - T - 0.2
    p = bx(TX+0.15, BX1-TX-0.15, YB0, y1, dz0+0.1, dz1-0.1)
    for k in range(DOOR_TABS):
        t0 = LID_T0 + LID_P*k
        p = p.union(bx(TX-1.0, TX+0.2, t0, t0+LID_TL, dz0+0.1, dz1-0.1)).union(bx(BX1-TX-0.2, BX1-TX+1.0, t0, t0+LID_TL, dz0+0.1, dz1-0.1))
    p = p.union(bx(TX-1.25, TX-1.0, YB0+3.0, YB0+6.0, dz0+0.1, dz1-0.1)).union(bx(BX1-TX+1.0, BX1-TX+1.25, YB0+3.0, YB0+6.0, dz0+0.1, dz1-0.1))
    p = p.union(bx(5.0, 11.0, YB0-5.0, YB0+0.0, dz0+0.1, BZ))                           # finger tab
    return p

def atom_key():
    # Spacer that goes in behind the ATOM (from the lid side) after the ATOM is in. Pushing a USB plug in
    # presses the ATOM against it, and the lid holds it. Open the lid, pull it, and the ATOM can be pushed out.
    gz1 = -BZ+3.4
    ay0 = YB1 - T - ATOM[1] - 0.5
    ze = BZ - T - ATOM_GAP; za = ze - ATOM[2]
    k = bx(BX1-TX-ATOM[0]-0.1, BX1-TX-0.6, ay0+2.3, ay0+ATOM[1]-2.3, gz1+0.1, za-0.15)   # leaves the tank-side gap free for the Grove cable
    k = k.cut(bx(BX1-TX-ATOM[0]+1.9, BX1-TX-2.6, ay0+4.3, ay0+ATOM[1]-4.3, gz1-1, za+1))
    return k

# ---------------- lower rails + crossbar + pad ----------------
FOOT_Y0, FOOT_Y1, FOOT_SY = 3.0, 17.0, 11.0      # foot block height range and the set-screw height
FOOT_ZO = 33.0                                   # foot outer face (thick side walls for the M6 set-screw thread)
RAIL_Y0 = FOOT_Y0                                # rails run through the foot

def lower_rails():
    r = None
    for s in (1, -1):
        z0, z1 = sorted((s*RZ0, s*RZ1))
        rail = bx(RX0, RX1, RAIL_Y0, YB0-LAP, z0, z1)
        zj0, zj1 = sorted((s*JZ0, s*RZ1))
        rail = rail.union(bx(JF, JM, JY0, YB0-0.3, zj0, zj1))            # threaded joint block (M6 holes cut on the mesh)
        rail = rail.union(bx(JF, RX1, JY0, YB0-LAP, zj0, zj1))           # transition into the rail
        zf = s*RZ1
        y = RAIL_Y0 + 24.0 - 1.6                                         # first notch: sleeves still fully on the rails (no foot any more)
        y = 13.2 + 5*int(np.ceil((y - 13.2)/5))
        while y + 1.6 + 24.0 <= JY0 - 0.5:                               # notches only where the carriage can reach
            rail = rail.cut(bx(RX0-1, RX1+1, y, y+2.0, zf-0.8 if s > 0 else zf-0.01, zf+0.01 if s > 0 else zf+0.8))
            y += 5
        r = rail if r is None else r.union(rail)
    return r

def foot():
    # A bridge between the two rails that slides on them: the rails pass right through it, so it can sit at the
    # bottom or anywhere higher, and one M6 thumb set-screw per side (thread along z, cut on the mesh) clamps it.
    # It stays inside the rails' depth: nothing sticks out toward the tank.
    f = bx(SX0, SX1, FOOT_Y0, FOOT_Y1, -FOOT_ZO, FOOT_ZO).edges("|Y").fillet(1.5)
    for s in (1, -1):
        z0, z1 = sorted((s*(RZ0-0.2), s*(RZ1+0.2)))
        f = f.cut(bx(RX0-0.2, RX1+0.2, FOOT_Y0-1, FOOT_Y1+1, z0, z1))
    return f

# ---------------- carriage (origin = sensor centre height) ----------------
SX0, SX1 = RX0-2.7, RX1+2.7
PIV_X = 0.3 + 9.25
def carriage():
    c = None
    for s in (1, -1):
        zi0, zi1 = RZ0-SLIDE_CL, RZ1+SLIDE_CL
        z0, z1 = sorted((s*(zi0-2.5), s*(zi1+2.5)))
        sl = bx(SX0, SX1, -24, 24, z0, z1)                             # sleeves as long as the carriage: flush with both bridges
        ch0, ch1 = sorted((s*zi0, s*zi1))
        sl = sl.cut(bx(RX0-SLIDE_CL, RX1+SLIDE_CL, -25, 25, ch0, ch1))
        w0, w1 = sorted((s*(zi0-2.5), s*zi0))
        sl = sl.cut(cyl(SEAT_D, "z", (PIV_X, 0, w0-0.5), (w1-w0)+1))    # trunnion seat (snug: holds the angle)
        # head slides in from the FRONT (tank side): open slot, a ramp, then a narrow neck that the 4 mm peg has to
        # squeeze through (stronger click than before), then the round seat. Installed, the tank wall also blocks it.
        prof = (cq.Workplane("XY").polyline([(SX0-1, -2.05), (PIV_X-4.4, -2.05), (PIV_X-2.6, -NECK_W/2), (PIV_X, -NECK_W/2),
                                             (PIV_X, NECK_W/2), (PIV_X-2.6, NECK_W/2), (PIV_X-4.4, 2.05), (SX0-1, 2.05)]).close()
                .extrude(w1 - w0 + 1.0).translate((0, 0, w0 - 0.5)))
        sl = sl.cut(prof)
        c = sl if c is None else c.union(sl)
    c = c.union(bx(SX0, SX1, 20, 24, -(RZ0-SLIDE_CL), RZ0-SLIDE_CL))    # upper bridge (between the rails)
    c = c.union(bx(SX0, SX1, -24, -20, -(RZ0-SLIDE_CL), RZ0-SLIDE_CL))  # lower bridge, full depth like the upper one (the cable now goes up)
    zo0, zo1 = RZ1+SLIDE_CL, RZ1+SLIDE_CL+2.5                            # latch tongue on +z sleeve
    for cut in ((5.7, 6.5, -2.8, 14), (13.5, 14.3, -2.8, 14), (5.7, 14.3, -2.8, -2.0)):
        c = c.cut(bx(cut[0], cut[1], cut[2], cut[3], zo0-0.1, zo1+0.1))
    d = SLIDE_CL + TOOTH_IN                                              # tooth: 0.45 mm into the notch, ramped both ways
    tooth = (cq.Workplane("YZ").polyline([(-1.8, zo0), (-1.3, zo0-d), (-0.3, zo0-d), (0.2, zo0)]).close().extrude(6).translate((7, 0, 0)))
    c = c.union(tooth)
    c = c.union(bx(7, 13, -2.0, 1.0, zo1, zo1+1.8))                      # finger tab
    # the sensor cable leaves the head at the top and goes straight up: the upper bridge is a C clip for it
    c = c.cut(cq.Workplane().add(cq.Solid.makeCylinder(BRIDGE_BORE/2, 6, cq.Vector(CAB_HEAD_X, 19, 0), cq.Vector(0, 1, 0))))   # loose ring, cable moves freely
    c = c.cut(cq.Workplane().add(cq.Solid.makeCylinder(BRIDGE_BORE/2, 6, cq.Vector(CAB_HEAD_X-1.5, 19, 0), cq.Vector(0, 1, 0))))   # oval toward the floor hole
    c = c.cut(bx(CAB_HEAD_X-1.5, CAB_HEAD_X, 19, 25, -BRIDGE_BORE/2, BRIDGE_BORE/2))
    # closed ring (no snap slot): the cable is threaded through (per Igal)
    return c

# ---------------- sensor head (origin = pivot height) ----------------
def head():
    # Sensor is pushed in from the front, narrow end first; the wide sensing face stays exposed, flush with the front.
    # A slot in the bottom runs from the front face back to the cable and stops there (closed behind the cable).
    x0, x1, h = 0.3, 0.3+19.0, 17.0
    hd = bx(x0, x1, -h, h, -h, h).edges("|X").fillet(2)
    SCL = 0.085                                                      # +0.17 on diameter (0.3 per side printed too loose)
    fr, br = FD/2 + SCL, BD/2 + SCL
    hd = hd.cut(cyl(2*fr, "x", (x0-1, 0, 0), FT+1))                  # flange pocket, open at the front, face flush
    bo0 = x0 + FT
    hd = hd.cut(cyl(2*br, "x", (bo0-0.01, 0, 0), TOT-FT+0.2+0.01))    # body bore, closed at the back
    xc = x0 + TOT - CAB_FROM_BACK                                    # cable centre when seated
    w = CAB + 0.5
    # cable leaves through the top: straight up through the carriage bridge clip to the box
    hd = hd.cut(bx(x0-1, xc, 0, 30, -w/2, w/2))                     # cable slot from the front ...
    hd = hd.cut(cq.Workplane().add(cq.Solid.makeCylinder(w/2, 30, cq.Vector(xc, 0, 0), cq.Vector(0, 1, 0))))   # ... round end at the cable
    for ang in (30, 150, 270):                                       # 3 crush ribs grip the body (0.15 each), away from the slot
        rib = bx(bo0+1.0, x0+TOT-0.5, br-0.23, br+0.2, -0.6, 0.6).rotate((0, 0, 0), (1, 0, 0), ang - 90)
        hd = hd.union(rib)
    for s in (1, -1):
        hd = hd.union(cyl(4.0, "z", (PIV_X, 0, h-0.5 if s > 0 else -h-2.8), 3.3))
    return hd

def pin():
    return cq.Workplane("XY").circle(PIN_D/2).extrude(8.0).edges().chamfer(0.3)

parts = {"top_frame": top_frame(), "lid": lid(), "door": door(), "atom_key": atom_key(), "lower_rails": lower_rails(), "foot": foot(),
         "carriage": carriage(), "sensor_head": head()}
if __name__ == "__main__":
    import json
    out = {}
    for n, p in parts.items():
        bb = p.val().BoundingBox()
        out[n] = [round(bb.xlen,1), round(bb.ylen,1), round(bb.zlen,1)]
        cq.exporters.export(p, f"asm_{n}.stl", tolerance=0.03, angularTolerance=0.15)
    for n, p in color_parts().items():                      # AMS colour inlays for the top frame (same coordinates)
        cq.exporters.export(p, f"asm_{n}.stl", tolerance=0.01, angularTolerance=0.1)
        out[n] = "colour inlay"
    print(json.dumps(out))
