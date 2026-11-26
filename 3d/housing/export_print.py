import trimesh, numpy as np, os
os.makedirs("print", exist_ok=True)
def L(n): return trimesh.load(f"asm_{n}.stl")
def orient(m, M):
    m=m.copy(); v=m.vertices; m.vertices=np.c_[M(v)]; 
    if np.linalg.det(np.array([[1,0,0],[0,1,0],[0,0,1]]))<0: pass
    m.fix_normals(); m.vertices -= m.bounds[0]; return m
# bed coords (u, v, Z up)
P = {}
P["top_frame"]   = orient(L("top_frame"),   lambda v: np.c_[v[:,1], v[:,0], -v[:,2]])         # closed back (+z) side down, long axis along u
P["lid"]         = orient(L("lid"),         lambda v: np.c_[v[:,1], v[:,0], -v[:,2]])          # flat top face (plate + tab) down
P["lower_rails"] = orient(L("lower_rails"), lambda v: np.c_[v[:,1], -v[:,2], -v[:,0]])        # back face (x=14) down
P["door"]        = orient(L("door"),        lambda v: np.c_[v[:,1], -v[:,0], v[:,2]])         # inner face down
P["atom_key"]    = orient(L("atom_key"),    lambda v: np.c_[v[:,0], v[:,1], v[:,2]])          # frame standing
P["foot"]        = orient(L("foot"),        lambda v: np.c_[v[:,2], v[:,0], v[:,1]])          # pockets up, flat bottom down
P["carriage"]    = orient(L("carriage"),    lambda v: np.c_[v[:,1], v[:,2], v[:,0]])          # front face down
P["sensor_head"] = orient(L("sensor_head"), lambda v: np.c_[v[:,1], -v[:,2], -v[:,0]])        # closed back down, open front up
pin = trimesh.load("screw_local.stl"); pin.vertices -= pin.bounds[0]
place = {"lower_rails":(8,4),"top_frame":(8,64),"carriage":(120,64),"sensor_head":(8,94),"lid":(50,94),"foot":(100,94),"door":(140,4),"atom_key":(150,60)}
scene = trimesh.Scene()
for n,(u,v) in place.items():
    m=P[n].copy(); m.apply_translation((u,v,0)); m.export(f"print/{n}.stl"); scene.add_geometry(m, node_name=n, geom_name=n)
for i in range(4):
    m=pin.copy(); m.apply_translation((50+i*13,140,0)); scene.add_geometry(m, node_name=f"screw_{i+1}", geom_name=f"screw_{i+1}")
pin.export("print/screw.stl")
ss = trimesh.load("setscrew_local.stl"); ss.vertices -= ss.bounds[0]; ss.export("print/setscrew.stl")
scene.export("print/classika_housing_A1mini_plate.3mf")
for n,m in P.items(): print(n, m.bounds[1].round(1).tolist(), "watertight", m.is_watertight, "vol", round(m.volume))
b=np.vstack([g.bounds for g in scene.dump()]); print("plate extents", b.min(0).round(1).tolist(), b.max(0).round(1).tolist())
