"""Runs every geometric check on the current assembled model and prints one line per check."""
import trimesh, numpy as np, json
exec(open("build.py").read().split("def cyl")[0])
L = lambda n: trimesh.load(f"asm_{n}.stl")
def ov(a, b): return trimesh.boolean.intersection([a, b], engine="manifold").volume
def box(x0,x1,y0,y1,z0,z1):
    b = trimesh.creation.box(extents=(x1-x0, y1-y0, z1-z0)); b.apply_translation(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)); return b
def mv(m, d): m = m.copy(); m.apply_translation(d); return m
top, lid, door, rails, car, head = (L(n) for n in ("top_frame","lid","door","lower_rails","carriage","sensor_head"))
foot = trimesh.creation.box(extents=(1,1,1)); foot.apply_translation((0,-500,0))   # the foot was removed (per Igal)
res = []
def chk(name, val, ok): res.append((name, round(float(val), 3), bool(ok))); print(f"{'OK ' if ok else 'BAD'} {name}: {val:.3f}")
TX_, T_ = 2.4, 1.6
ix0, ix1 = TX_, BX1-TX_; zb = BZ-T_; ay0 = YB1-T_-24-0.5; ze = zb-4.5; za = ze-24
ax0 = ix1-9.6
atom = box(ax0+0.05, ax0+9.5, ay0+0.05, ay0+24, za, ze)
grove = box(ax0+0.3, ax0+4.4, ay0+7, ay0+17, ze, ze+4.38)
usb_x = ix1-9.6+9.5-2.15
usb_metal = box(usb_x-1.3, usb_x+1.3, ay0+12-4.2, ay0+12+4.2, ze, ze+6.6)
import cadquery as cq, tempfile, os
def rbox(x0,x1,y0,y1,z0,z1,r):
    w = cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0).edges("|Z").fillet(r).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    f = tempfile.mktemp(suffix=".stl"); cq.exporters.export(w, f); m = trimesh.load(f); os.remove(f); return m
usb_over = rbox(usb_x-4.5, usb_x+4.5, ay0+12-6.25, ay0+12+6.25, ze+6.6, ze+30, 2.0)
chk("ATOM in its place vs frame", ov(atom, top), ov(atom, top) < 0.01)
chk("Grove plug on the ATOM vs frame", ov(grove, top), ov(grove, top) < 0.01)
chk("thick USB-C plug (12.5 x 9, corner r2) vs frame", ov(usb_over, top) + ov(usb_metal, top), ov(usb_over, top) + ov(usb_metal, top) < 0.01)
chk("USB-C plug vs Grove plug", ov(usb_over, grove) + ov(usb_metal, grove), ov(usb_over, grove) + ov(usb_metal, grove) < 0.01)
worst = max(ov(mv(atom, (0, 0, -d)), top) for d in (5, 10, 20, 30, 45))
chk("ATOM slides in from the lid side (worst overlap on the way)", worst, worst < 0.01)
dz0 = BZ-3.4; wz1 = dz0-15.0; wz0 = wz1-WAGO[1]
wy = [YB0+T_+PASS_H+1.6+i*(WAGO[2]+0.1+1.6) for i in range(3)]
wagos = [box(ix0-1.0+0.05, ix0-1.0+WAGO[0], y, y+WAGO[2], wz0+0.05, wz1) for y in wy]
for i, w in enumerate(wagos):
    v = ov(w, top); chk(f"Wago {i+1} in its track (only the click bumps touch)", v, v < 6)
w_on_path = max([ov(mv(wagos[1], (1.0, 0, d)), top) for d in (40, 30, 21, 15)] + [ov(mv(wagos[1], (0.5, 0, 14)), top), ov(mv(wagos[1], (0, 0, 13)), top)])
pushers = [box(ix0+1.2, ix0+5.0, w+6.55-1.5, w+6.55+1.5, wz0-12, wz0-0.1) for w in wy]
pv = sum(ov(p, top) for p in pushers)
chk("screwdriver through the inner wall reaches the back of each Wago", pv, pv < 0.01)
chk("Wago in through the door, pressed against the wall, slid in (only the bumps touch)", w_on_path, w_on_path < 2.8)
for n, p in (("lid", lid), ("door", door)):
    chk(f"{n} closed vs frame", ov(p, top), ov(p, top) < 0.01)
    sgn = -1 if n == "lid" else 1
    lift = max(ov(mv(p, (0, -8, sgn*z)), top) for z in (1, 3, 6))
    chk(f"{n}: slide 8 mm down, then lift off", lift, lift < 0.01)
    blocked = ov(mv(p, (0, 0, sgn*1.5)), top)
    chk(f"{n}: cannot lift without sliding", blocked, blocked > 1)
    for w in wagos:
        pass
chk("door closed vs Wagos", sum(ov(door, w) for w in wagos), sum(ov(door, w) for w in wagos) < 0.01)
bad = []
NOTCH_H = []
_y = 13.2 + 5*int(np.ceil((3.0 + 24.0 - 1.6 - 13.2)/5))
while _y + 1.6 + 24.0 <= JY0 - 0.5: NOTCH_H.append(_y + 1.6); _y += 5
for H in NOTCH_H:
    c, h = mv(car, (0, H, 0)), mv(head, (0, H, 0))
    v = sum(ov(a, b) for a, b in ((c, rails), (h, rails), (h, c), (c, top), (h, top), (c, foot), (h, foot)))
    if v > 0.01: bad.append(H)
chk(f"sensor heights {NOTCH_H[0]:.0f}-{NOTCH_H[-1]:.0f} mm, all {len(NOTCH_H)} notches, all parts", len(bad), not bad)
for a in (-10, 10):
    h = head.copy(); h.apply_transform(trimesh.transformations.rotation_matrix(np.radians(a), (0, 0, 1), (9.55, 0, 0)))
    chk(f"head tilted {a} deg vs carriage", ov(h, car), ov(h, car) < 0.01)
sc = [L(f"screw_{i}") for i in range(1, 5)]
v = sum(ov(s, top) for s in sc[:4]); chk("thumb screws vs top frame", v, v < 0.01)
chk("rails vs top frame", ov(rails, top), ov(rails, top) < 0.01)
under = box(ix0+0.2, ix1-0.2, YB0+T_+0.3, YB0+T_+PASS_H-0.3, -BZ+4, dz0-0.2)
chk("cable passage under the lowest Wago, door side to the back", ov(under, top), ov(under, top) < 0.01)
over = box(ix0+0.2, ix1-0.2, wy[2]+WAGO[2]+0.1+1.6+0.3, ay0-T_-0.3, -BZ+4, dz0-0.2)
chk("cable passage over the top Wago, door side to the back", ov(over, top), ov(over, top) < 0.01)
key = L("atom_key")
gch = box(ix0+0.1, ax0-0.1, ay0+3, ay0+20, za-24, ze)
chk("Grove cable channel behind the ATOM stays free (incl. spacer)", ov(gch, top)+ov(gch, L("atom_key")), ov(gch, top)+ov(gch, L("atom_key")) < 0.01)
gp = box(ix0+0.6, ix0+0.6+10.0, ay0-T_-3, ay0+1, -BZ+3.4+0.3+8.8, -BZ+3.4+0.3+8.8+5.0)
chk("white Grove plug (10 x 5) passes the shelf opening, lid side", ov(gp, top), ov(gp, top) < 0.01)
chk("ATOM spacer vs frame / lid / ATOM", ov(key, top)+ov(key, lid)+ov(key, atom), ov(key, top)+ov(key, lid)+ov(key, atom) < 0.01)
gap = (-BZ+3.4-0.1) - key.bounds[0][2]
chk("lid holds the spacer (gap lid -> spacer, mm)", abs(key.bounds[0][2] - (-BZ+3.4+0.1)), abs(key.bounds[0][2] - (-BZ+3.4+0.1)) < 0.05)
bad = []
for H in [y for y in np.arange(14.8, 140, 5.0)]:
    c, h = mv(car, (0, H, 0)), mv(head, (0, H, 0))
    if ov(c, rails) > 0.01: continue
    p0 = np.array([0.3+16.73-5.0, H+17.2, 0.0]); p1 = np.array([CAB_X, YB0-CLIP_L-1.0, 0.0]); p2 = np.array([CAB_X, YB0+T_+1, 0.0])
    cab = trimesh.boolean.union([trimesh.creation.cylinder(radius=1.82, segment=[p0, p1], sections=32),
                                 trimesh.creation.cylinder(radius=1.82, segment=[p1, p2], sections=32)], engine="manifold")
    parts_hit = {n: round(ov(cab, m), 2) for n, m in (("top", top), ("rails", rails), ("carriage", c), ("foot", foot))}
    if sum(parts_hit.values()) > 0.01: bad.append((round(H,1), parts_hit))
chk("sensor cable from the head, through the carriage ring, into the floor hole, every height", len(bad), not bad)
if bad: print(bad[:3])
store = box(ix0+0.3, ix1-0.3, wy[0], wy[2]+WAGO[2], -BZ+3.4+0.6, wz0-1.6-0.3)
chk("storage space for the spare sensor cable behind the Wagos", ov(store, top), ov(store, top) < 0.01)
rim = min(CAB_X-CAB_HOLE/2, BX1-(CAB_X+CAB_HOLE/2))
chk("floor around the sensor-cable hole is at least the hole size (mm)", rim, rim >= CAB_HOLE-0.01)
json.dump(res, open("verify_results.json", "w"))
