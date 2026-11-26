"""Cut M6 printed threads into the rail joint blocks and make the 4 thumb screws (run after build.py)."""
import trimesh, numpy as np
from threads import thread_rod, place, knob
exec(open("build.py").read().split("def cyl")[0])            # constants only
JF, JM, JB, JZ0 = 1.0, 8.0, 15.5, 13.0
P, R_SCREW, R_TAP, KD, KH = 1.0, 2.9, 3.15, 10.0, 5.0
SHANK = (JB - JF) - 0.5                                     # 14.0: tip ends 1.5 mm behind the front face
pos = [(yy, s*(JZ0+RZ1)/2) for s in (1, -1) for yy in (YB0-5.5, YB0-16.0)]

rails = trimesh.load("asm_lower_rails.stl")
taps = [place(thread_rod(R_TAP, P, JM-JF+2, tip=0), (JF-1, y, z), (1, 0, 0)) for y, z in pos]
rails = trimesh.boolean.difference([rails] + taps, engine="manifold")
rails.export("asm_lower_rails.stl")

def screw():
    k = knob(KD, KH)
    rod = thread_rod(R_SCREW, P, SHANK + 0.6, tip=1.0); rod.apply_translation((0, 0, KH - 0.6))
    return trimesh.boolean.union([k, rod], engine="manifold")
sc = screw(); sc.export("screw_local.stl")                   # knob on z=0, thread up +z (print orientation)
for i, (y, z) in enumerate(pos):
    m = place(sc, (JB + KH, y, z), (-1, 0, 0)); m.export(f"asm_screw_{i+1}.stl")
# foot: one M6 set-screw per side along z, presses into the rail dimple
foot = trimesh.load("asm_foot.stl")
FX, FY, FZO = (RX0+RX1)/2, 11.0, 33.0
ftaps = [place(thread_rod(R_TAP + 0.1, P, 8.0), (FX, FY, s*(FZO+1)), (0, 0, -s)) for s in (1, -1)]
foot = trimesh.boolean.difference([foot] + ftaps, engine="manifold"); foot.export("asm_foot.stl")
def setscrew():
    k = knob(KD, KH)
    rod = thread_rod(R_SCREW, P, 6.8 + 0.6, tip=1.0); rod.apply_translation((0, 0, KH - 0.6))
    return trimesh.boolean.union([k, rod], engine="manifold")
ss = setscrew(); ss.export("setscrew_local.stl")
for i, s in enumerate((1, -1)):
    m = place(ss, (FX, FY, s*(FZO + KH)), (0, 0, -s)); m.export(f"asm_setscrew_{i+1}.stl")
print("foot watertight", foot.is_watertight, "setscrew", ss.is_watertight, ss.bounds[1][2])
print("rails watertight", rails.is_watertight, "screw watertight", sc.is_watertight, "screw len", sc.bounds[1][2])
