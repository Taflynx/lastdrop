"""Checks the housing against the tank (wall + rim flange) along the install path."""
import trimesh, cadquery as cq, numpy as np, importlib.util
spec=importlib.util.spec_from_file_location('b','build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def bx(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
tank=bx(-b.TW,0,0,b.RIM,-50,50).union(bx(-b.TW,b.FL_W,b.RIM-b.FL_T,b.RIM,-50,50))
cq.exporters.export(tank,"_tank_tmp.stl"); T=trimesh.load("_tank_tmp.stl"); T.apply_translation((-0.02,-0.02,0))
H=60
parts={n:trimesh.load(f"asm_{n}.stl") for n in ("top_frame","lower_rails","carriage","sensor_head","lid","door","screw_1","screw_2","screw_3","screw_4")}
for n in ("carriage","sensor_head"): parts[n].apply_translation((0,H,0))
OFF=8.6
path=[(OFF,OFF+ y) for y in (120,60,20,0)] + [(x,OFF) for x in np.linspace(OFF,0,9)] + [(0,y) for y in np.linspace(OFF,0,9)]
for dx,dy in path:
    hits={}
    for n,m in parts.items():
        mm=m.copy(); mm.apply_translation((dx,dy,0))
        v=trimesh.boolean.intersection([mm,T],engine="manifold").volume
        if v>0.01: hits[n]=round(v,2)
    print(f"offset x={dx:5.2f} y={dy:6.2f}", hits if hits else "clear")
