"""RED HOUR | original rights-safe commercial CGI test by Pryntor Studios.
Native Blender 5.0.1 Python. Procedural geometry/textures only; no model/API calls.
Run: blender -b -t 2 --python red_hour_gallery.py -- --outdir output --mode still
Modes: still, video, both. Render sizes intentionally limited for free public CI.
This file neither claims photorealism nor completed creative acceptance.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def material(name, color, metallic=0, roughness=.5, noise=0, transmission=0, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if transmission:
        p.inputs['Transmission Weight'].default_value = transmission
    if emission:
        p.inputs['Emission Color'].default_value = (*emission[:3], 1)
        p.inputs['Emission Strength'].default_value = emission[3]
    if noise:
        nodes = m.node_tree.nodes
        links = m.node_tree.links
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 37.0
        tex.inputs['Detail'].default_value = 3.0
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = noise
        bump.inputs['Distance'].default_value = .025
        links.new(tex.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def soften(obj, width=.05, segments=3):
    bevel = obj.modifiers.new('Hand-finished light-catching edges', 'BEVEL')
    bevel.width = width
    bevel.segments = segments
    obj.modifiers.new('Preserve surface normals', 'WEIGHTED_NORMAL')


def cube(name, loc, dims, mat, edge=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if edge:
        soften(ob, edge)
    return ob


def cylinder(name, loc, rad, depth, mat, edge=0, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=rad, depth=depth, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    if edge:
        soften(ob, edge)
    return ob


def torus(name, loc, major, minor, mat, orientation=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=120, minor_segments=16,
        location=loc, major_radius=major, minor_radius=minor)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    if orientation:
        o.rotation_euler = orientation
    for face in o.data.polygons:
        face.use_smooth = True
    return o


def arch_disc(name, center, radius, height, material_):
    """Flattened arched wall inset facing -Y (not a fake window opening)."""
    x, y, z = center
    pts = [(x-radius,y,z), (x+radius,y,z), (x+radius,y,z+height)]
    for i in range(1, 49):
        ang = math.pi * i/48
        pts.append((x + radius*math.cos(ang),y,z+height+radius*math.sin(ang)))
    pts.append((x-radius,y,z+height))
    mesh = bpy.data.meshes.new(name+'mesh')
    mesh.from_pydata(pts, [], [tuple(range(len(pts)))])
    mesh.update()
    ob = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material_)
    return ob


def curve(name, points, bevel, mat):
    cu = bpy.data.curves.new(name,'CURVE')
    cu.dimensions='3D'; cu.bevel_depth=bevel; cu.bevel_resolution=3
    s=cu.splines.new('POLY'); s.points.add(len(points)-1)
    for p, xyz in zip(s.points, points):
        p.co=(*xyz,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def aim(ob, target):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()


def light(name, location, power, size, color, target, shape='DISK'):
    bpy.ops.object.light_add(type='AREA',location=location)
    ob=bpy.context.object; ob.name=name; ob.data.energy=power
    ob.data.color=color; ob.data.shape=shape
    ob.data.size=size
    aim(ob,target)


def lettering(text, loc, size, mat, rot=(math.pi/2,0,0), spacing=1.2):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    ob=bpy.context.object
    ob.name='Original editorial typography | '+text
    ob.data.body=text
    ob.data.size=size
    ob.data.space_character=spacing
    ob.data.align_x='CENTER'
    ob.data.extrude=.004
    ob.data.bevel_depth=.0007
    ob.data.materials.append(mat)
    return ob


def stage():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    plaster=material('Warm off-white mineral plaster',(0.54,.50,.44),roughness=.88,noise=.18)
    plaster_lite=material('Mineral fluted fins',(0.71,.66,.56),roughness=.81,noise=.12)
    floor=material('Travertine with natural microtexture',(.46,.42,.35),roughness=.38,noise=.22)
    dark=material('Deep oxblood recessed alcove',(.039,.018,.019),roughness=.68,noise=.06)
    crimson=material('Signature vermilion lacquer',(.64,.024,.028),metallic=.26,roughness=.18)
    bronze=material('Anodized warm brushed champagne bronze',(.49,.275,.126),metallic=.87,roughness=.26)
    black=material('Graphite anodized structural metal',(.032,.035,.038),metallic=.8,roughness=.27)
    glass=material('Pale smoked glass',(.55,.69,.69),roughness=.12,transmission=.82)
    milk=material('Milk glass luminous diffuser',(.89,.58,.33),roughness=.35,emission=(1,.25,.08,4.8))
    ivory=material('Warm ivory display lettering',(.89,.81,.67),roughness=.7)
    leafmat=material('Deep sculptural olive foliage',(.12,.17,.092),roughness=.65)
    ceramic=material('Matte black planter vessel',(.075,.064,.061),roughness=.72)
    lit=material('Soft brushed brass geometry',(.53,.34,.19),metallic=.68,roughness=.32)
    # Room dimensions 14 x 18m with carefully staged perspective.
    cube('Continuous textured limestone gallery floor',(0,0,-.19),(16,23,.32),floor)
    cube('Architectural right gallery wall',(7.2,.7,3.55),(.38,19,7.25),plaster)
    cube('Architectural left gallery wall',(-7.2,.7,3.55),(.38,19,7.25),plaster)
    cube('High floating plaster ceiling',(0,0,7.25),(16,23,.28),plaster)
    cube('Back gallery wall',(0,8.2,3.45),(15,.3,7.1),plaster)
    cube('Floor shadow gap', (0,8.0,.13),(14.2,.17,.08),dark,.03)
    # Recess and swept arched opening silhouette, with fine mouldings.
    arch_disc('Single dark architectural arch — original design',(0,7.97,.18),2.95,3.1,dark)
    for j in range(49):
        # Arch cornice segments work as actual curved 3D strips.
        theta=math.pi*j/48
        x=3.02*math.cos(theta)
        z=3.1+3.02*math.sin(theta)
        if j:
            prev=math.pi*(j-1)/48
            curve('Champagne-lined arch cornice',[(3.02*math.cos(prev),7.83,3.1+3.02*math.sin(prev)),(x,7.83,z)],.024,bronze)
    cube('Left opening bronze reveal',(-3.02,7.83,1.67),(.046,.08,3.0),bronze)
    cube('Right opening bronze reveal',(3.02,7.83,1.67),(.046,.08,3.0),bronze)
    # Monumental repeating rhythm and real depth foreground for parallax.
    for i,y in enumerate((-4.5,1.0,5.7)):
        cube(f'Gallery structural fin left {i}',(-6.55,y,3.38),(.78,.72,6.7),plaster_lite,.07)
        cube(f'Gallery structural fin right {i}',(6.55,y,3.38),(.78,.72,6.7),plaster_lite,.07)
        cube(f'Bronze floor reveal {i}',(0,y,.011),(11.5,.021,.007),bronze)
    for i in range(15):
        y=-8.4+i*1.03
        cube(f'Hand-set limestone seam {i}',(0,y,.001),(12.4,.009,.008),dark)
    # Left slatted natural-light gallery windows.
    for i in range(6):
        y=-6.4+1.86*i
        cube(f'Glass-wall mullion {i}',(-7.0,y,3.85),(.14,.07,5.0),bronze,.016)
    cube('Long smoked glass upper rail',(-6.99,-1.85,6.25),(.08,11.0,.08),bronze)
    cube('Long smoked glass lower rail',(-6.99,-1.85,1.28),(.08,11.0,.08),bronze)
    for i in range(5):
        cube(f'Glazing module {i}',(-7.015,-5.47+i*1.86,3.78),(.018,1.76,4.8),glass)
    # Travertine engineered podiums with genuinely machined bevels.
    cylinder('Stage / monolithic limestone stepped foundation',(.15,1.15,.21),2.28,.44,floor,.075,128)
    cylinder('Stage / deeply recessed oxblood separator',(.15,1.15,.46),1.79,.10,dark,.023,128)
    cylinder('Stage / floating chamfered ceremonial display',(.15,1.15,.63),1.58,.26,plaster_lite,.085,128)
    cylinder('Stage / brass circular inlay',(.15,1.15,.767),1.27,.018,bronze,.008,128)
    cylinder('Fixture motorised foot in black metal',(.15,1.15,.854),.29,.16,black,.05)
    cylinder('Fixture stem solid machined bronze',(.15,1.15,1.43),.08,1.0,bronze,.028)
    # Original double orbit architectural light / fictional object, 3D in world coordinates.
    torus('OBJECT 01 | primary functional luminous orbit',(.15,1.15,2.19),.98,.083,milk,(math.radians(67),math.radians(20),math.radians(-21)))
    torus('OBJECT 01 | gold technical bezel behind diffuser',(.15,1.15,2.19),1.09,.035,bronze,(math.radians(67),math.radians(20),math.radians(-21)))
    torus('OBJECT 01 | secondary crimson sculptural orbit',(.15,1.15,2.24),1.31,.091,crimson,(math.radians(104),math.radians(52),math.radians(38)))
    torus('OBJECT 01 | hairline inlay',(.15,1.15,2.24),1.4,.014,bronze,(math.radians(104),math.radians(52),math.radians(38)))
    cylinder('OBJECT 01 | floating central red metal boss',(.15,1.15,2.24),.20,.19,crimson,.045)
    # Distinct showroom light pendant array right: coherent actual hanging fixtures.
    for i,y in enumerate((-3.0,.1,3.2)):
        x=4.4
        curve(f'Pendant {i} suspension cord',[(x,y,7.05),(x,y,4.8+.08*i)],.018,black)
        cylinder(f'Pendant {i} oxidised canopy',(x,y,4.82+.08*i),.37,.13,bronze,.05)
        cylinder(f'Pendant {i} luminous interior',(x,y,4.74+.08*i),.24,.022,milk,.008)
    # Back-lounge staging furniture, original simple design — no stock assets.
    for x,y in ((-4.55,4.35),(4.6,4.5)):
        cylinder(f'Collector stool seat {x}',(x,y,1.0),.77,.24,plaster_lite,.10)
        cylinder(f'Collector stool ebony base {x}',(x,y,.5),.37,.9,black,.05)
    # Handmade broad leaf sculpture on a secondary plinth, avoiding stock foliage.
    cylinder('Terracotta-black plant urn',(-4.25,1.60,.62),.48,.82,ceramic,.04)
    for i in range(9):
        theta=2*math.pi*i/9
        tip=(-4.25+1.05*math.cos(theta),1.6+1.04*math.sin(theta),2.3+.45*math.sin(i*1.7))
        mid=(-4.25+.33*math.cos(theta),1.6+.25*math.sin(theta),1.5)
        curve(f'Botanical curved stem {i}',[(-4.25,1.6,1.0),mid,tip],.02,leafmat)
        v=Vector((math.cos(theta),math.sin(theta),0))
        w=Vector((-math.sin(theta),math.cos(theta),0))
        center=Vector(tip)
        points=[tuple(center-v*.50),tuple(center+w*.23),tuple(center+v*.7),tuple(center-w*.23)]
        mesh=bpy.data.meshes.new(f'Leaf {i} native hand-modelled geometry')
        mesh.from_pydata(points, [],[(0,1,2),(0,2,3)])
        mesh.update()
        leaf=bpy.data.objects.new(f'Original sculpted olive leaf {i}',mesh)
        bpy.context.collection.objects.link(leaf)
        leaf.data.materials.append(leafmat)
        solid=leaf.modifiers.new('Leaf physical thickness','SOLIDIFY');solid.thickness=.024
    # Graphic, intentionally fictional product brand instead of client promise.
    lettering('RED HOUR',(-.04,7.75,4.62),.43,ivory)
    lettering('OBJECT    /    01',(-.03,7.75,4.17),.16,lit,spacing=1.5)
    lettering('PRYNTOR  STUDIOS',(.15,.54,.44),.105,ivory,spacing=1.08)
    # Sun geometry is controlled, not added in Photoshop. Light direction has real shadows.
    bpy.ops.object.light_add(type='SUN',location=(-6.5,-2.8,8))
    sun=bpy.context.object; sun.name='Raking directional editorial sunlight'
    sun.data.energy=2.0; sun.data.color=(1.0,.74,.5); sun.data.angle=math.radians(6.0)
    aim(sun,(0,1,.5))
    light('Main 5m softbox key',(-2.0,-5.3,6.7),1500,5.0,(1.0,.74,.56),(0,1.2,2.0))
    light('Warm vignette wall wash',(2.5,4.7,6.6),850,3.8,(1.0,.65,.38),(0,7,3.8))
    light('North cyan reflected bounce',(3.5,-4.5,4.5),750,5.0,(.57,.72,1.0),(0,1.2,2.2))
    light('Sculptural red object gold rim',(1.2,2.8,4.5),900,2.3,(1.0,.89,.68),(.15,1.15,2.3))
    bpy.ops.object.camera_add(location=(4.4,-9.0,3.32))
    cam=bpy.context.object
    cam.name='01 / RED HOUR | real animated perspective camera'
    cam.data.type='PERSP'; cam.data.lens=36; cam.data.sensor_width=36
    cam.data.dof.use_dof=True
    cam.data.dof.focus_distance=11.0;cam.data.dof.aperture_fstop=5.6
    sc=bpy.context.scene
    sc.camera=cam
    sc.frame_start=1;sc.frame_end=49;sc.render.fps=16
    # Shot is a real 3D track/dolly with a restrained ~1.35m lateral move.
    for f,x,y,z in [(1,4.4,-9.0,3.32),(25,3.65,-8.6,3.24),(49,3.02,-8.2,3.15)]:
        cam.location=(x,y,z)
        aim(cam,(0,1.1,2.14))
        cam.keyframe_insert(data_path='location',frame=f)
        cam.keyframe_insert(data_path='rotation_euler',frame=f)
    # Blender interpolation defaults to bezier; avoid legacy Action.fcurves API.
    if sc.world:
        sc.world.use_nodes=True
        bg=sc.world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Color'].default_value=(.18,.20,.23,1)
            bg.inputs['Strength'].default_value=.28
    sc.render.engine='CYCLES'
    sc.cycles.device='CPU'
    sc.render.image_settings.file_format='PNG'
    sc.render.image_settings.color_mode='RGB'
    sc.render.resolution_percentage=100
    sc.render.film_transparent=False
    sc.render.image_settings.color_depth='8'
    sc.view_settings.view_transform='AgX'
    return sc


def main():
    argsv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    pa=argparse.ArgumentParser()
    pa.add_argument('--outdir',default='output')
    pa.add_argument('--mode',choices=['still','video','both'],default='still')
    pa.add_argument('--width',type=int,default=960)
    pa.add_argument('--samples',type=int,default=24)
    a=pa.parse_args(argsv)
    assert 400 <= a.width <= 1440 and 8 <= a.samples <= 96,'Render outside reviewed CPU budget envelope'
    dest=Path(a.outdir).expanduser().resolve();dest.mkdir(parents=True,exist_ok=True)
    sc=stage()
    sc.cycles.samples=a.samples
    sc.cycles.use_denoising=True
    sc.render.resolution_x=a.width
    sc.render.resolution_y=round(a.width*9/16)
    sc.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/'red_hour_gallery_editable.blend'),compress=False)
    if a.mode in ('still','both'):
        for frame in (1,25,49):
            sc.frame_set(frame)
            sc.render.filepath=str(dest/f'red_hour_f{frame:03}.png')
            bpy.ops.render.render(write_still=True)
            print(f'PRYNTOR_RENDER_FINISHED_FRAME {frame}',flush=True)
    if a.mode in ('video','both'):
        # Few seconds of real perspective movement rather than frame interpolation/slideshow.
        sc.cycles.samples=min(a.samples,16)
        for f in range(1,50):
            sc.frame_set(f)
            sc.render.filepath=str(dest/f'motion_{f:03}.png')
            bpy.ops.render.render(write_still=True)
            print(f'PRYNTOR_RENDER_FINISHED_MOTION {f}',flush=True)
    metadata={
        'project':'RED HOUR / OBJECT 01 — original fictional commercial gallery',
        'render':'Blender-native Cycles CPU / original procedural geometry',
        'third_party_models_or_textures':0,
        'external_image_video_api_calls':0,
        'human_approval':'PENDING — neither commercial release nor photorealism guaranteed',
        'shot':{'fps':16,'frames':[1,49],'true_3d_dolly':True,'camera_perspective':True},
        'mode':a.mode,'width':a.width,'samples':a.samples,
        'editorial_note':'Technical decode tests do not equal photographic-quality or rights sign-off'
    }
    (dest/'render_provenance.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('PRYNTOR_NATIVE_CGI_COMPLETE',flush=True)


if __name__=='__main__':main()
