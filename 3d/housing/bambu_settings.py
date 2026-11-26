"""Bambu Studio project settings block for a multi-filament A1 mini PETG project.

Bambu Studio only accepts a multi-filament project block in its own exact layout. So: start from a 2-filament
A1 mini block that Bambu Studio itself saved (project_settings_multicolour_template.json), keep its key set, take
every value from our PETG project (project_settings_A1mini_PETG.json), and size the per-filament lists to the
number of colours."""
import json

GREY, TURQUOISE, YELLOW = "#D3D3D3", "#1FB5AC", "#F5C518"


def project_settings(colours):
    t = json.load(open("project_settings_multicolour_template.json"))
    o = json.load(open("project_settings_A1mini_PETG.json"))
    n = len(colours)
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
    # purge per colour change (mm3), row = from, column = to. Grey (filament 1) to a colour: 160; a colour to grey or
    # to another colour: 260 (dark to light needs more). The purge goes into the hidden infill first.
    flush = [0 if i == j else (160 if i == 0 else 260) for i in range(n) for j in range(n)]
    d.update({
        "filament_colour": [c + "FF" for c in colours], "filament_multi_colour": [c + "FF" for c in colours],
        "filament_self_index": [str(i + 1) for i in range(n)], "filament_ids": ["GFG99"] * n,   # Generic PETG
        "filament_settings_id": ["Generic PETG @BBL A1M"] * n, "filament_map": ["1"] * n,
        "flush_volumes_matrix": [str(x) for x in flush],
        "flush_volumes_vector": ["140"] * (2 * n),               # Bambu saves 2 per filament
        "flush_into_infill": "1",
        "wipe_tower_x": ["140"] * len(t["wipe_tower_x"]), "wipe_tower_y": ["20"] * len(t["wipe_tower_y"]),
        "different_settings_to_system": [o["different_settings_to_system"][0] + ";curr_bed_type;outer_wall_speed;outer_wall_acceleration"] + [""] * n + [""],
        # 2026-11-26: outer wall 200 mm/s was capped by PETG's 8 mm3/s, so it sped up and slowed down all the time and
        # every layer came out a different shade (stripes on the LED face). A steady, slower outer wall fixes that.
        "outer_wall_speed": ["60"] * len(t["outer_wall_speed"]),
        "outer_wall_acceleration": ["2000"] * len(t["outer_wall_acceleration"]),
        "curr_bed_type": "Textured PEI Plate", "enable_prime_tower": "1", "from": "project", "name": "project_settings",
        "version": o.get("version", t["version"]),
    })
    return json.dumps(d, indent=4)
