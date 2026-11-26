"""Top frame with the Lastdrop branding in colour, for the A1 mini with the AMS lite.
One object, two parts: the light grey frame (filament 1) and the turquoise drop logo (outline and water) and "Lastdrop" (filament 2).
The small text is a plain engraving in the frame colour. The colour part sits in its pocket, 0.4 mm under the surface.
Run after build.py (needs asm_top_frame.stl and asm_brand_*.stl)."""
import json, zipfile, uuid, numpy as np, trimesh
import xml.dom.minidom as md

PARTS = [("top_frame", "asm_top_frame.stl", 1), ("logo_name_turquoise", "asm_brand_turquoise.stl", 2)]
COLOURS = ["#D3D3D3", "#1FB5AC"]                     # light grey, turquoise (match them to the AMS slots)
OUT = "print/lastdrop_top_frame_colour_A1mini_PETG_AMS.3mf"
# the project's own changes from the system profiles (see project_settings_A1mini_PETG.json), set on the object
OBJECT_SETTINGS = {"wall_loops": "3", "top_shell_layers": "5", "bottom_shell_layers": "5", "sparse_infill_density": "25%",
                   "sparse_infill_pattern": "gyroid", "enable_support": "1", "support_type": "tree(auto)",
                   "support_on_build_plate_only": "1"}
BED = 180.0

# same print orientation as export_print.py: closed back (+z) side down, long axis along u. One shared offset for all parts.
M = lambda v: np.c_[v[:, 1], v[:, 0], -v[:, 2]]
meshes = []
for name, path, ext in PARTS:
    m = trimesh.load(path); m.vertices = M(m.vertices); m.fix_normals()
    meshes.append([name, m, ext])
lo = meshes[0][1].bounds[0].copy(); hi = meshes[0][1].bounds[1]
size = hi - lo
for p in meshes:
    p[1].vertices -= lo + np.r_[size[0]/2, size[1]/2, 0]     # centre the frame's footprint on the object origin
tx, ty = 8 + size[0]/2, 100 + size[1]/2                       # leave room at the front for the prime tower
assert tx + size[0]/2 <= BED and ty + size[1]/2 <= BED

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"')
def sub_model():
    L = ['<?xml version="1.0" encoding="UTF-8"?>', f'<model unit="millimeter" xml:lang="en-US" {NS} requiredextensions="p">',
         ' <metadata name="BambuStudio:3mfVersion">1</metadata>', ' <resources>']
    for i, (name, m, _) in enumerate(meshes):
        L += [f'  <object id="{i+1}" p:UUID="{i+1:04x}0000-81cb-4c03-9d28-80fed5dfa1dc" type="model">', '   <mesh>', '    <vertices>']
        L += [f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in m.vertices]
        L += ['    </vertices>', '    <triangles>']
        L += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces]
        L += ['    </triangles>', '   </mesh>', '  </object>']
    L += [' </resources>', ' <build/>', '</model>']
    return "\n".join(L)
PAR = len(meshes) + 1
def main_model():
    L = ['<?xml version="1.0" encoding="UTF-8"?>', f'<model unit="millimeter" xml:lang="en-US" {NS} requiredextensions="p">',
         ' <metadata name="Application">BambuStudio-02.00.00.00</metadata>', ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
         ' <metadata name="Title">Lastdrop top frame, colour</metadata>', ' <resources>',
         f'  <object id="{PAR}" p:UUID="00000001-61cb-4c03-9d28-80fed5dfa1dc" type="model">', '   <components>']
    for i in range(len(meshes)):
        L.append(f'    <component p:path="/3D/Objects/object_1.model" objectid="{i+1}" p:UUID="{i+1:04x}0000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
    L += ['   </components>', '  </object>', ' </resources>', f' <build p:UUID="{uuid.uuid4()}">',
          f'  <item objectid="{PAR}" p:UUID="00000001-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 {tx:.4f} {ty:.4f} 0" printable="1"/>',
          ' </build>', '</model>']
    return "\n".join(L)
def settings():
    L = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>', f'  <object id="{PAR}">',
         '    <metadata key="name" value="top_frame_lastdrop"/>', '    <metadata key="extruder" value="1"/>']
    L += [f'    <metadata key="{k}" value="{v}"/>' for k, v in OBJECT_SETTINGS.items()]
    for i, (name, _, ext) in enumerate(meshes):
        L += [f'    <part id="{i+1}" subtype="normal_part">', f'      <metadata key="name" value="{name}"/>',
              '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
              f'      <metadata key="extruder" value="{ext}"/>',
              '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
              '    </part>']
    L += ['  </object>', '  <plate>', '    <metadata key="plater_id" value="1"/>',
          '    <metadata key="plater_name" value="Top frame Lastdrop colour"/>', '    <metadata key="locked" value="false"/>',
          '    <model_instance>', f'      <metadata key="object_id" value="{PAR}"/>', '      <metadata key="instance_id" value="0"/>',
          '      <metadata key="identify_id" value="1001"/>', '    </model_instance>', '  </plate>', '</config>']
    return "\n".join(L)
def project_settings():
    """Bambu Studio only accepts a multi-filament project block in its own exact layout. So: start from a 2-filament
    A1 mini block that Bambu Studio itself saved (project_settings_multicolour_template.json), keep its key set, take
    every value from our PETG project (project_settings_A1mini_PETG.json), and grow the per-filament lists to 3."""
    t = json.load(open("project_settings_multicolour_template.json"))
    o = json.load(open("project_settings_A1mini_PETG.json"))
    n = len(COLOURS)
    nt = len(t["filament_colour"])                                # filaments in the template (2)
    fil = [k for k, v in t.items() if isinstance(v, list) and len(v) == nt
           and not k.startswith("machine_") and k != "start_end_points"]
    d = {}
    for k, v in t.items():
        if k in fil:
            src = o[k] if isinstance(o.get(k), list) and o[k] else v
            d[k] = [src[0]] * n
        elif k in o and k not in ("version",):
            d[k] = o[k]
        else:
            d[k] = v
    d.update({
        "filament_colour": [c + "FF" for c in COLOURS], "filament_multi_colour": [c + "FF" for c in COLOURS],
        "filament_self_index": [str(i + 1) for i in range(n)], "filament_ids": ["GFG99"] * n,   # Generic PETG
        "filament_settings_id": ["Generic PETG @BBL A1M"] * n, "filament_map": ["1"] * n,
        # purge per colour change (mm3), row = from, column = to: grey->turquoise 160, turquoise->grey 260 (dark to light
        # needs more). The purge goes into the hidden infill first (flush_into_infill), so less ends up on the prime tower.
        "flush_volumes_matrix": [str(0 if i == j else (160 if i == 0 else 260)) for i in range(n) for j in range(n)],
        "flush_into_infill": "1",
        "flush_volumes_vector": ["140"] * (2 * n),               # Bambu saves 2 per filament
        "wipe_tower_x": ["140"] * len(t["wipe_tower_x"]), "wipe_tower_y": ["20"] * len(t["wipe_tower_y"]),
        "different_settings_to_system": [o["different_settings_to_system"][0] + ";curr_bed_type"] + [""] * n + [""],
        "curr_bed_type": "Textured PEI Plate", "enable_prime_tower": "1", "from": "project", "name": "project_settings",
        "version": o.get("version", t["version"]),
    })
    return json.dumps(d, indent=4)

def project_settings_old():
    d = json.load(open("project_settings_A1mini_PETG.json"))
    n = len(COLOURS)
    # filament settings (list from Bambu's own filament profiles, filament_keys.json): repeat the whole list once per
    # filament. Some have several values per filament (e.g. AMS drying temperatures), so repeat the list, not one value.
    for k in json.load(open("filament_keys.json")):
        if isinstance(d.get(k), list):
            d[k] = d[k] * n
    d["filament_colour"] = COLOURS
    d["filament_map"] = ["1"] * n
    d["flush_volumes_vector"] = ["140", "140"]                    # one pair per extruder (the A1 mini has one)
    d["flush_volumes_matrix"] = [str(0 if i == j else (380 if i == 0 else 220)) for i in range(n) for j in range(n)]
    d["inherits_group"] = [d["inherits_group"][0]] + [d["inherits_group"][1]] * n + [d["inherits_group"][-1]]
    d["different_settings_to_system"] = [d["different_settings_to_system"][0]] + [""] * n + [""]
    d["enable_prime_tower"] = "1"
    return json.dumps(d, indent=4)

CT = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
      ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
      ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>')
MRELS = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
         ' <Relationship Target="/3D/Objects/object_1.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>')
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT); z.writestr("_rels/.rels", RELS)
    z.writestr("3D/3dmodel.model", main_model()); z.writestr("3D/_rels/3dmodel.model.rels", MRELS)
    z.writestr("3D/Objects/object_1.model", sub_model())
    z.writestr("Metadata/model_settings.config", settings())
    z.writestr("Metadata/project_settings.config", project_settings())
with zipfile.ZipFile(OUT) as z:
    for n in z.namelist():
        if n.endswith("project_settings.config"): json.loads(z.read(n))
        elif n.endswith((".model", ".config", ".rels", ".xml")): md.parseString(z.read(n))
print(OUT, "ok;", [(n, ext, m.is_watertight, round(m.volume, 1)) for n, m, ext in meshes], "footprint", size.round(1).tolist())
