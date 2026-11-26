"""Printed metric thread geometry as watertight meshes (trimesh + manifold3d)."""
import numpy as np, trimesh

def thread_rod(R, P, L, depth=None, nt=72, nz_per_pitch=18, tip=0.0, base_flat=0.0):
    """Threaded rod along +z from z=0 to z=L. R = crest radius. Trapezoid profile.
    tip: chamfer length at z=L. base_flat: plain (minor radius) start length."""
    depth = depth if depth is not None else 0.6*P
    nz = int(np.ceil(L/P*nz_per_pitch)) + 1
    zs = np.linspace(0, L, nz); th = np.linspace(0, 2*np.pi, nt, endpoint=False)
    Z, T = np.meshgrid(zs, th, indexing="ij")
    u = np.mod(Z/P - T/(2*np.pi), 1.0)
    prof = np.interp(u, [0, 0.38, 0.5, 0.88, 1.0], [0, 1, 1, 0, 0])      # 0 = root, 1 = crest
    r = (R - depth) + depth*prof
    if tip > 0:
        lim = (R - depth) + depth*np.clip((L - Z)/tip, 0, 1)
        r = np.where(Z > L - tip, np.minimum(r, lim), r)
    V = np.stack([r*np.cos(T), r*np.sin(T), Z], -1).reshape(-1, 3)
    F = []
    idx = lambda i, j: i*nt + (j % nt)
    for i in range(nz-1):
        for j in range(nt):
            a, b, c, d = idx(i, j), idx(i, j+1), idx(i+1, j+1), idx(i+1, j)
            F += [[a, b, c], [a, c, d]]
    c0 = len(V); c1 = c0 + 1
    V = np.vstack([V, [0, 0, 0], [0, 0, L]])
    for j in range(nt):
        F.append([c0, idx(0, j+1), idx(0, j)])
        F.append([c1, idx(nz-1, j), idx(nz-1, j+1)])
    m = trimesh.Trimesh(V, np.array(F), process=True)
    m.fix_normals()
    return m

def place(m, origin, axis):
    """Move a +z rod so it starts at origin and runs along axis (unit vector)."""
    m = m.copy()
    T = trimesh.geometry.align_vectors([0, 0, 1], axis)
    m.apply_transform(T); m.apply_translation(origin); return m

def knob(D=13.0, H=5.0, ribs=12):
    k = trimesh.creation.cylinder(radius=D/2, height=H, sections=96); k.apply_translation((0, 0, H/2))
    cut = []
    for i in range(ribs):
        a = 2*np.pi*i/ribs
        c = trimesh.creation.cylinder(radius=0.9, height=H+2, sections=24)
        c.apply_translation((D/2*np.cos(a), D/2*np.sin(a), H/2)); cut.append(c)
    k = trimesh.boolean.difference([k] + cut, engine="manifold")
    return k

if __name__ == "__main__":
    r = thread_rod(3.0, 1.0, 12, tip=1.0)
    print(r.is_watertight, r.volume, r.bounds)
