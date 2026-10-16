"""Original nonbilling Blender 5+ product-style still.
No Scenario/Hugging Face calls, credentials, external assets or network access.
UNTESTED IN A LIVE BLENDER RUNTIME; inspect before use.
"""
import argparse
import pathlib
import sys

import bpy
from mathutils import Vector


def material(name, rgba, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = rgba
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = roughness
    return mat


def bevel(obj, width, segments=4):
    modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    normal = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return modifier, normal


def aim_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="./output")
    parser.add_argument("--size", type=int, default=768)
    cfg = parser.parse_args(args)

    outdir = pathlib.Path(cfg.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    body_mat = material("Fictional body / petrol", (0.035, 0.26, 0.31, 1), 0.45, 0.23)
    cap_mat = material("Fictional cap / bronze", (0.58, 0.30, 0.11, 1), 0.68, 0.27)
    stage_mat = material("Original stage / slate", (0.085, 0.11, 0.15, 1), 0.15, 0.5)
    floor_mat = material("Backdrop / warm gray", (0.25, 0.24, 0.23, 1), 0, 0.75)

    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.83, depth=1.7, location=(0, 0, 1.10))
    body = bpy.context.object
    body.name = "FICTIONAL PRODUCT | unbranded cylinder"
    body.data.materials.append(body_mat)
    bevel(body, 0.13)

    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.72, depth=0.18, location=(0, 0, 2.03))
    cap = bpy.context.object
    cap.name = "Fictional closure"
    cap.data.materials.append(cap_mat)
    bevel(cap, 0.045)

    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1.58, depth=0.25, location=(0, 0, 0.12))
    stage = bpy.context.object
    stage.name = "Original display stage"
    stage.data.materials.append(stage_mat)
    bevel(stage, 0.06)

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.015))
    floor = bpy.context.object
    floor.name = "Original matte background"
    floor.data.materials.append(floor_mat)

    bpy.ops.object.light_add(type="AREA", location=(0.5, -3.0, 5.5))
    key = bpy.context.object
    key.name = "Large soft key"
    key.data.energy = 550
    key.data.shape = "DISK"
    key.data.size = 4.0
    aim_at(key, (0, 0, 1))

    bpy.ops.object.light_add(type="AREA", location=(-3, 2, 4))
    rim = bpy.context.object
    rim.name = "Subtle rim"
    rim.data.energy = 300
    rim.data.size = 3.0
    aim_at(rim, (0, 0, 1))

    bpy.ops.object.camera_add(location=(3.6, -5.2, 3.1))
    camera = bpy.context.object
    camera.name = "Product camera"
    aim_at(camera, (0, 0, 1.1))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 4.2
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.render.resolution_x = cfg.size
    scene.render.resolution_y = cfg.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.28, 0.30, 0.35, 1)
            bg.inputs["Strength"].default_value = 0.5

    blend_path = outdir / "fictional_product_source.blend"
    render_path = outdir / "fictional_product_1x1.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    scene.render.filepath = str(render_path)
    bpy.ops.render.render(write_still=True)
    print("PILOT_NATIVE_RENDER_COMPLETE", render_path, blend_path)


if __name__ == "__main__":
    main()
