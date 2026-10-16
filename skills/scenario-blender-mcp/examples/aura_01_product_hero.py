"""Pryntor Studios: original fictional AURA/01 ceramic product hero.
Native Blender only. No vendor inference, external textures, keys, network,
customer assets or Scenario GPL code. Does not represent a real client.
"""
import argparse
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


def matte(name, color, metallic=0, roughness=.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def soften(obj, width=.05, segments=5):
    mod = obj.modifiers.new("Light-catching softened bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    obj.modifiers.new("Weighted normal", "WEIGHTED_NORMAL")


def cylinder(name, loc, rad, depth, mat, width):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=rad, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if width:
        soften(obj, width)
    return obj


def point(obj, at):
    obj.rotation_euler = (Vector(at) - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_light(name, at, power, size, color, target):
    bpy.ops.object.light_add(type="AREA", location=at)
    l = bpy.context.object
    l.name = name
    l.data.energy = power
    l.data.shape = "DISK"
    l.data.size = size
    l.data.color = color
    point(l, target)


def front_type(content, height, size, surface_radius, mat, normal, tracking=1.02):
    bpy.ops.object.text_add()
    label = bpy.context.object
    label.name = "Original lettering / " + content
    label.data.body = content
    label.data.size = size
    label.data.align_x = "CENTER"
    label.data.align_y = "CENTER"
    label.data.space_character = tracking
    label.data.resolution_u = 20
    label.data.extrude = .001
    label.data.materials.append(mat)
    n = Vector(normal).normalized()
    tangent = Vector((-n.y, n.x, 0))
    # Text x-axis follows the cylinder tangent; y-axis stays upright.
    # Local +z points toward the camera, preventing mirror lettering.
    basis = Matrix(((tangent.x, 0, n.x),
                    (tangent.y, 0, n.y),
                    (0, 1, 0)))
    label.rotation_euler = basis.to_euler()
    label.location = (n.x * surface_radius, n.y * surface_radius, height)
    return label


def render_all(outdir, requested_size, selected):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    ceramic = matte("AURA 01 | deep marine ceramic", (.014, .14, .18), .2, .23)
    collar = matte("AURA 01 | fine copper foil", (.66, .36, .18), .82, .22)
    enamel = matte("AURA 01 | glazed edge", (.045, .28, .33), .45, .21)
    letter = matte("AURA 01 | mineral ivory print", (.93, .87, .73), .12, .28)
    plinth = matte("Sculpted circular podium", (.073, .099, .11), .24, .38)
    seamless = matte("Neutral studio cyclorama", (.12, .115, .115), .0, .68)

    cylinder("Fictional cosmetic product | body", (0, 0, 1.05), .72, 1.55, ceramic, .12)
    cylinder("Copper metallic collar", (0, 0, 1.86), .685, .085, collar, .025)
    cylinder("Copper cap", (0, 0, 2.02), .665, .22, collar, .055)
    cylinder("Closure crown enamel", (0, 0, 2.146), .61, .025, enamel, .012)
    cylinder("Presentation pedestal | round", (0, 0, .14), 1.38, .27, plinth, .062)
    cylinder("Inset podium top", (0, 0, .283), 1.22, .014, collar, .004)

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.01))
    floor = bpy.context.object
    floor.name = "Seamless studio floor"
    floor.data.materials.append(seamless)

    # Front-facing marks are fully original and intentionally fictional.
    # Camera is offset to right; align print with its radial view.
    n = Vector((2.9, -5.3, 0)).normalized()
    front_type("AURA", 1.37, .23, .723, letter, n)
    front_type("0 1", 1.02, .115, .727, letter, n)
    front_type("OBJECT STUDY", .79, .071, .73, letter, n)

    add_light("Large amber beauty key", (1.1, -3.9, 5.0), 640, 4.6, (1.0, .82, .67), (0, 0, 1))
    add_light("Cool wraparound fill", (-3.6, -2.1, 3.1), 400, 3.2, (.54, .74, 1.0), (0, 0, 1))
    add_light("Rim and metallic edge", (-.1, 2.7, 4.5), 830, 2.0, (1.0, .86, .64), (0, 0, 1.2))

    bpy.ops.object.camera_add(location=(2.9, -5.3, 3.0))
    camera = bpy.context.object
    camera.name = "Editorial product hero | orthographic camera"
    point(camera, (0, 0, 1.15))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.95
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 18
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (.18, .19, .22, 1)
            bg.inputs["Strength"].default_value = .32

    outdir.mkdir(parents=True, exist_ok=True)
    scene.render.resolution_x = requested_size
    scene.render.resolution_y = requested_size
    bpy.ops.wm.save_as_mainfile(filepath=str(outdir / "aura_01_editable_source.blend"))

    ratios = [
        ("aura_01_1x1", 1, 1),
        ("aura_01_4x5", 4, 5),
        ("aura_01_9x16", 9, 16),
        ("aura_01_16x9", 16, 9),
    ]
    for name, rw, rh in ratios:
        if selected != "all" and name != "aura_01_" + selected:
            continue
        w = round(requested_size * rw / min(rw, rh))
        h = round(requested_size * rh / min(rw, rh))
        # Cropping is native-camera recomposition rather than stretched pixels.
        scene.render.resolution_x = w
        scene.render.resolution_y = h
        camera.data.ortho_scale = 3.95 if rw == rh else (4.25 if rh > rw else 4.0)
        scene.render.filepath = str(outdir / (name + ".png"))
        bpy.ops.render.render(write_still=True)
        print(f"PILOT_OUTPUT_VERIFIED_SOURCE {name}.png {w}x{h}")

    print("BLENDER_RENDER_FINISHED", str(outdir))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="output")
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--format", choices=["all", "1x1", "4x5", "9x16", "16x9"], default="all")
    args = parser.parse_args(argv)
    assert 256 <= args.size <= 1600, "Render size outside tested cost envelope"
    render_all(Path(args.outdir).expanduser().resolve(), args.size, args.format)


if __name__ == "__main__":
    main()
