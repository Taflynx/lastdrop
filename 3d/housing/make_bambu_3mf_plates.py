"""The whole housing as one Bambu Studio 3MF for the A1 mini + AMS lite, one plate per print job, coloured:
  filament 1 grey       the frame, rails, lid, door, ATOM key
  filament 2 turquoise  the slider (carriage), the sensor head, and the logo + name on the top frame
  filament 3 yellow     the four thumb screws
Plates 1 to 3 use one colour each (no colour changes while printing). Plate 4 is the top frame with its turquoise
logo, which changes colour on the layers that carry the logo.
Run after build.py and export_print.py (needs print/*.stl and asm_top_frame.stl / asm_brand_turquoise.stl)."""
import trimesh, numpy as np, zipfile, uuid, json
import xml.dom.minidom as md
from bambu_settings import project_settings, GREY, TURQUOISE, YELLOW

COLOURS = [GREY, TURQUOISE, YELLOW]
OUT = "print/lastdrop_housing_A1mini_PETG_AMS_4plates.3mf"
BED = 180.0; STRIDE = BED * (1 + 1/5)
OBJECT_SETTINGS = {"wall_loops": "3", "top_shell_layers": "5", "bottom_shell_layers": "5", "sparse_infill_density": "25%",
                   "sparse_infill_pattern": "gyroid", "enable_support": "1", "support_type": "tree(auto)",
                   "support_on_build_plate_only": "1"}

def stl(n):
    m = trimesh.load(f"print/{n}.stl"); m.vertices -= m.bounds[0]; return m

def top_frame_parts():
    """Top frame + its logo part in print orientation (as export_print.py: closed back side down), one shared offset."""
    M = lambda v: np.c_[v[:, 1], v[:, 0], -v[:, 2]]
    parts = []
    for name, path, ext in [("top_frame", "asm_top_frame.stl", 1), ("logo_name_turquoise", "asm_brand_turquoise.stl", 2)]:
        m = trimesh.load(path); m.vertices = M(m.vertices); m.fix_normals(); parts.append((name, m, ext))
    lo = parts[0][1].bounds[0].copy()
    for _, m, _ in parts: m.vertices -= lo
    return parts

# plate name, [(object name, [(part name, mesh, filament)], u, v)]
plates = [
    ("1 Turquoise - sensor head + slider", [("sensor_head", [("sensor_head", stl("sensor_head"), 2)], 10, 10),
                                            ("carriage", [("carriage", stl("carriage"), 2)], 62, 10)]),
    ("2 Yellow - 4 thumb screws", [(f"screw_{i+1}", [(f"screw_{i+1}", stl("screw"), 3)], 20 + 22*(i % 2), 20 + 22*(i // 2))
                                   for i in range(4)]),
    ("3 Grey - rails, lid, door, ATOM key", [("lower_rails", [("lower_rails", stl("lower_rails"), 1)], 10, 5),
                                             ("lid", [("lid", stl("lid"), 1)], 10, 96),
                                             ("door", [("door", stl("door"), 1)], 100, 96),
                                             ("atom_key", [("atom_key", stl("atom_key"), 1)], 166, 96)]),
    ("4 Grey + turquoise - top frame with logo", [("top_frame", top_frame_parts(), 8, 100)]),
]

cols = int(np.ceil(np.sqrt(len(plates))))
objs = []; nid = 0
for pi, (pname, items) in enumerate(plates):
    ox = (pi % cols) * STRIDE; oy = -(pi // cols) * STRIDE
    for oname, parts, u, v in items:
        hi = np.max([m.bounds[1] for _, m, _ in parts], axis=0)
        assert u + hi[0] <= BED and v + hi[1] <= BED, (oname, hi)
        ps = []
        for name, m, ext in parts:
            m = m.copy(); m.vertices -= [hi[0]/2, hi[1]/2, 0]; nid += 1; ps.append(dict(id=nid, name=name, mesh=m, ext=ext))
        nid += 1
        objs.append(dict(par=nid, k=len(objs) + 1, name=oname, parts=ps, tx=ox + u + hi[0]/2, ty=oy + v + hi[1]/2, plate=pi + 1))

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"')
SUB = "-81cb-4c03-9d28-80fed5dfa1dc"
def sub_model(o):
    L = ['<?xml version="1.0" encoding="UTF-8"?>', f'<model unit="millimeter" xml:lang="en-US" {NS} requiredextensions="p">',
         ' <metadata name="BambuStudio:3mfVersion">1</metadata>', ' <resources>']
    for p in o["parts"]:
        L += [f'  <object id="{p["id"]}" p:UUID="{p["id"]:04x}0000{SUB}" type="model">', '   <mesh>', '    <vertices>']
        L += [f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in p["mesh"].vertices]
        L += ['    </vertices>', '    <triangles>']
        L += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in p["mesh"].faces]
        L += ['    </triangles>', '   </mesh>', '  </object>']
    L += [' </resources>', ' <build/>', '</model>']
    return "\n".join(L)
def main_model():
    L = ['<?xml version="1.0" encoding="UTF-8"?>', f'<model unit="millimeter" xml:lang="en-US" {NS} requiredextensions="p">',
         ' <metadata name="Application">BambuStudio-02.00.00.00</metadata>', ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
         ' <metadata name="Title">Lastdrop housing, colour</metadata>', ' <resources>']
    for o in objs:
        L += [f'  <object id="{o["par"]}" p:UUID="{o["k"]:08x}-61cb-4c03-9d28-80fed5dfa1dc" type="model">', '   <components>']
        for p in o["parts"]:
            L.append(f'    <component p:path="/3D/Objects/object_{o["k"]}.model" objectid="{p["id"]}" '
                     f'p:UUID="{p["id"]:04x}0000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
        L += ['   </components>', '  </object>']
    L += [' </resources>', f' <build p:UUID="{uuid.uuid4()}">']
    for o in objs:
        L.append(f'  <item objectid="{o["par"]}" p:UUID="{o["k"]:08x}-b1ec-4553-aec9-835e5b724bb4" '
                 f'transform="1 0 0 0 1 0 0 0 1 {o["tx"]:.4f} {o["ty"]:.4f} 0" printable="1"/>')
    L += [' </build>', '</model>']
    return "\n".join(L)
def model_rels():
    L = ['<?xml version="1.0" encoding="UTF-8"?>', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    L += [f' <Relationship Target="/3D/Objects/object_{o["k"]}.model" Id="rel-{o["k"]}" '
          'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for o in objs]
    L.append('</Relationships>')
    return "\n".join(L)
def settings():
    L = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for o in objs:
        L += [f'  <object id="{o["par"]}">', f'    <metadata key="name" value="{o["name"]}"/>',
              f'    <metadata key="extruder" value="{o["parts"][0]["ext"]}"/>']
        L += [f'    <metadata key="{k}" value="{v}"/>' for k, v in OBJECT_SETTINGS.items()]
        for p in o["parts"]:
            L += [f'    <part id="{p["id"]}" subtype="normal_part">', f'      <metadata key="name" value="{p["name"]}"/>',
                  '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
                  f'      <metadata key="extruder" value="{p["ext"]}"/>',
                  '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
                  '    </part>']
        L.append('  </object>')
    for pi, (pname, _) in enumerate(plates):
        L += ['  <plate>', f'    <metadata key="plater_id" value="{pi+1}"/>', f'    <metadata key="plater_name" value="{pname}"/>',
              '    <metadata key="locked" value="false"/>']
        for o in objs:
            if o["plate"] == pi + 1:
                L += ['    <model_instance>', f'      <metadata key="object_id" value="{o["par"]}"/>',
                      '      <metadata key="instance_id" value="0"/>', f'      <metadata key="identify_id" value="{1000+o["k"]}"/>',
                      '    </model_instance>']
        L.append('  </plate>')
    L.append('</config>')
    return "\n".join(L)

CT = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
      ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
      ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>')
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT); z.writestr("_rels/.rels", RELS)
    z.writestr("3D/3dmodel.model", main_model()); z.writestr("3D/_rels/3dmodel.model.rels", model_rels())
    for o in objs: z.writestr(f"3D/Objects/object_{o['k']}.model", sub_model(o))
    z.writestr("Metadata/model_settings.config", settings())
    z.writestr("Metadata/project_settings.config", project_settings(COLOURS))
with zipfile.ZipFile(OUT) as z:
    for n in z.namelist():
        if n.endswith("project_settings.config"): json.loads(z.read(n))
        elif n.endswith((".model", ".config", ".rels", ".xml")): md.parseString(z.read(n))
print(OUT, "ok;", [(o["plate"], o["name"], [p["ext"] for p in o["parts"]], all(p["mesh"].is_watertight for p in o["parts"])) for o in objs])
