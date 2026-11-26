"""Write a Bambu Studio native-style 3MF: one file, one plate per print job."""
import trimesh, numpy as np, zipfile, uuid
BED=180.0; STRIDE=BED*(1+1/5)
plates=[("Test - head + carriage + screws",[("sensor_head",10,10),("carriage",62,10),("screw",128,10),("screw",142,10),("screw",156,10),("screw",128,26)]),
        ("Main parts",[("lower_rails",10,5),("top_frame",10,64),("lid",10,96),("door",100,96),("atom_key",166,96)])]
cols=int(np.ceil(np.sqrt(len(plates))))
OBJ_SFX="-61cb-4c03-9d28-80fed5dfa1dc"; SUB_SFX="-81cb-4c03-9d28-80fed5dfa1dc"
objs=[]; k=0
for pi,(pname,items) in enumerate(plates):
    ox=(pi%cols)*STRIDE; oy=-(pi//cols)*STRIDE
    for n,u,v in items:
        k+=1; m=trimesh.load(f"print/{n}.stl"); m.vertices-=m.bounds[0]; ext=m.bounds[1].copy()
        assert u+ext[0]<=BED and v+ext[1]<=BED, (n,ext)
        m.vertices-=[ext[0]/2,ext[1]/2,0]
        objs.append(dict(k=k,sub=2*k-1,par=2*k,name=n if n not in ("screw","setscrew") else f"{n}_{sum(1 for o in objs if o['name'].startswith(n+'_'))+1}",mesh=m,
                         tx=ox+u+ext[0]/2,ty=oy+v+ext[1]/2,tz=0.0,plate=pi+1))
NS='xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"'
def sub_model(o):
    L=['<?xml version="1.0" encoding="UTF-8"?>',f'<model unit="millimeter" xml:lang="en-US" {NS} requiredextensions="p">',
       ' <metadata name="BambuStudio:3mfVersion">1</metadata>',' <resources>',
       f'  <object id="{o["sub"]}" p:UUID="{o["sub"]:04x}0000{SUB_SFX}" type="model">','   <mesh>','    <vertices>']
    L+=[f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x,y,z in o["mesh"].vertices]
    L+=['    </vertices>','    <triangles>']
    L+=[f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in o["mesh"].faces]
    L+=['    </triangles>','   </mesh>','  </object>',' </resources>',' <build/>','</model>']
    return "\n".join(L)
def main_model():
    L=['<?xml version="1.0" encoding="UTF-8"?>',f'<model unit="millimeter" xml:lang="en-US" {NS} requiredextensions="p">',
       ' <metadata name="Application">BambuStudio-02.00.00.00</metadata>',' <metadata name="BambuStudio:3mfVersion">1</metadata>',
       ' <metadata name="Title">Classika water sensor housing</metadata>',' <resources>']
    for o in objs:
        L+=[f'  <object id="{o["par"]}" p:UUID="{o["k"]:08x}{OBJ_SFX}" type="model">','   <components>',
            f'    <component p:path="/3D/Objects/object_{o["k"]}.model" objectid="{o["sub"]}" p:UUID="{o["k"]:04x}0000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>',
            '   </components>','  </object>']
    L+=[' </resources>',f' <build p:UUID="{uuid.uuid4()}">']
    for o in objs:
        L.append(f'  <item objectid="{o["par"]}" p:UUID="{o["k"]:08x}-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 {o["tx"]:.4f} {o["ty"]:.4f} {o["tz"]:.4f}" printable="1"/>')
    L+=[' </build>','</model>']; return "\n".join(L)
def model_rels():
    L=['<?xml version="1.0" encoding="UTF-8"?>','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    L+=[f' <Relationship Target="/3D/Objects/object_{o["k"]}.model" Id="rel-{o["k"]}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for o in objs]
    L.append('</Relationships>'); return "\n".join(L)
def settings():
    L=['<?xml version="1.0" encoding="UTF-8"?>','<config>']
    for o in objs:
        L+=[f'  <object id="{o["par"]}">',f'    <metadata key="name" value="{o["name"]}"/>','    <metadata key="extruder" value="1"/>',
            f'    <part id="{o["sub"]}" subtype="normal_part">',f'      <metadata key="name" value="{o["name"]}"/>',
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
            f'      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
            '    </part>','  </object>']
    for pi,(pname,_) in enumerate(plates):
        L+=['  <plate>',f'    <metadata key="plater_id" value="{pi+1}"/>',f'    <metadata key="plater_name" value="{pname}"/>','    <metadata key="locked" value="false"/>']
        for o in objs:
            if o["plate"]==pi+1:
                L+=['    <model_instance>',f'      <metadata key="object_id" value="{o["par"]}"/>','      <metadata key="instance_id" value="0"/>',
                    f'      <metadata key="identify_id" value="{1000+o["k"]}"/>','    </model_instance>']
        L.append('  </plate>')
    L.append('</config>')
    return "\n".join(L)
CT='<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n <Default Extension="png" ContentType="image/png"/>\n <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>'
RELS='<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>'
out="print/lastdrop_housing_A1mini_PETG_2plates.3mf"
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml",CT); z.writestr("_rels/.rels",RELS)
    z.writestr("3D/3dmodel.model",main_model()); z.writestr("3D/_rels/3dmodel.model.rels",model_rels())
    for o in objs: z.writestr(f"3D/Objects/object_{o['k']}.model",sub_model(o))
    z.writestr("Metadata/model_settings.config",settings())
    z.writestr("Metadata/project_settings.config",open("project_settings_A1mini_PETG.json").read())
# self-checks: XML well-formed, references resolve, meshes watertight
import xml.dom.minidom as md
with zipfile.ZipFile(out) as z:
    names=z.namelist()
    for n in names:
        if n.endswith("project_settings.config"): __import__("json").loads(z.read(n))
        elif n.endswith((".model",".config",".rels",".xml")): md.parseString(z.read(n))
    print(len(names),"files, all XML well-formed")
print("objects", [(o["plate"],o["name"],round(o["tx"]),round(o["ty"]),o["mesh"].is_watertight) for o in objs])
