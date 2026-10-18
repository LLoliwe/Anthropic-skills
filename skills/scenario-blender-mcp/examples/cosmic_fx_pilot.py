"""Pryntor Studios: original native cosmic FX plus optional approved Nebulapunk Free.

This script does not contain Nebulapunk code, proprietary shaders, or vendor files.
Run Blender -b --disable-autoexec -t 2 --python cosmic_fx_pilot.py -- --outdir output
"""
import argparse
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector
from nebulapunk_intake import validate_vendor_asset, sha256_file


def emission(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    shader = nodes.new("ShaderNodeEmission")
    shader.inputs["Color"].default_value = (*color, 1)
    shader.inputs["Strength"].default_value = strength
    output = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(shader.outputs[0], output.inputs["Surface"])
    return mat


def cloud_material(name, color, seed):
    """Original procedural node arrangement. Not the publisher's shader."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    links = mat.node_tree.links
    tex = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0 + seed * 1.7
    noise.inputs["Detail"].default_value = 4.0
    distance = nodes.new("ShaderNodeVectorMath")
    distance.operation = "DISTANCE"
    distance.inputs[1].default_value = (0.5, 0.5, 0.5)
    radial = nodes.new("ShaderNodeMapRange")
    radial.inputs["From Min"].default_value = 0.05
    radial.inputs["From Max"].default_value = 0.70
    radial.inputs["To Min"].default_value = 1.0
    radial.inputs["To Max"].default_value = 0.0
    mask = nodes.new("ShaderNodeMath")
    mask.operation = "MULTIPLY"
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.08
    ramp.color_ramp.elements[1].position = 0.32
    clear = nodes.new("ShaderNodeBsdfTransparent")
    light = nodes.new("ShaderNodeEmission")
    light.inputs["Color"].default_value = (*color, 1)
    light.inputs["Strength"].default_value = 2.0
    mix = nodes.new("ShaderNodeMixShader")
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    links.new(tex.outputs["Generated"], distance.inputs[0])
    links.new(distance.outputs["Value"], radial.inputs["Value"])
    links.new(noise.outputs["Fac"], mask.inputs[0])
    links.new(radial.outputs["Result"], mask.inputs[1])
    links.new(mask.outputs[0], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], mix.inputs[0])
    links.new(clear.outputs[0], mix.inputs[1])
    links.new(light.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs["Surface"])
    return mat


def original_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Pryntor studio night")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (.002, .004, .018, 1)
        bg.inputs["Strength"].default_value = 0.2
    sheets = [
        ("Original cobalt cloud", (-1.9, -.2, -1.5), (4.7, 2.0, .07), (.05, .17, 1.), 0),
        ("Original cyan ribbon", (1.5, .0, -1.), (3.2, 1.1, .06), (.02, .85, .95), 1),
        ("Original ultraviolet vapor", (.7, 1., -1.8), (4.6, 1.75, .05), (.48, .09, .83), 2),
        ("Original amber cloud", (1.2, -.7, -2.), (2.2, .65, .05), (1., .35, .08), 3),
    ]
    for name, loc, scale, hue, seed in sheets:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=16, location=loc)
        ob = bpy.context.object
        ob.name = name
        ob.scale = scale
        ob.rotation_euler.z = math.radians(seed * 27 - 15)
        ob.data.materials.append(cloud_material(name + " | native node math", hue, seed))
    white = emission("Original star ivory", (.77, .87, 1.), 3)
    warm = emission("Original star gold", (1., .7, .36), 2)
    rng = random.Random(20261018)
    for i in range(112):
        radius = rng.choice((.011, .013, .016, .023, .03))
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1, radius=radius,
            location=(rng.uniform(-7, 7), rng.uniform(-4.1, 4.1), -.3))
        ob = bpy.context.object
        ob.name = "Original star %03d" % i
        ob.data.materials.append(white if rng.random() < .85 else warm)
    metal = emission("Original copper beacon", (1., .42, .1), 1.2)
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=8,
        location=(0, -.1, .4), major_radius=1.1, minor_radius=.016)
    ring = bpy.context.object
    ring.name = "Original space beacon"
    ring.rotation_euler = (math.radians(30), math.radians(63), math.radians(10))
    ring.data.materials.append(metal)
    bpy.ops.object.camera_add(location=(0, 0, 17))
    camera = bpy.context.object
    camera.name = "Cosmic FX preview camera"
    camera.rotation_euler = (Vector((0, 0, -1)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 14
    scene.camera = camera
    scene.view_settings.view_transform = "AgX"
    return scene


def attach_licensed_collection(args):
    record = validate_vendor_asset(
        args.vendor_file, args.vendor_receipt, args.vendor_sha256, args.vendor_collection)
    with bpy.data.libraries.load(str(Path(args.vendor_file).expanduser().resolve()),
                                 link=False) as (source, dest):
        if args.vendor_collection not in source.collections:
            raise ValueError("Named vendor collection absent; inspect actual free asset first")
        dest.collections = [args.vendor_collection]
    for collection in dest.collections:
        if collection is None:
            raise ValueError("Vendor collection load failed")
        bpy.context.scene.collection.children.link(collection)
    return record


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="output")
    parser.add_argument("--size", type=int, default=384)
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--vendor-file")
    parser.add_argument("--vendor-receipt")
    parser.add_argument("--vendor-sha256")
    parser.add_argument("--vendor-collection")
    args = parser.parse_args(argv)
    if not 256 <= args.size <= 960 or not 2 <= args.samples <= 16:
        raise ValueError("R0 render limit exceeded")
    inputs = (args.vendor_file, args.vendor_receipt, args.vendor_sha256, args.vendor_collection)
    if any(inputs) and not all(inputs):
        raise ValueError("Incomplete vendor licence or source: refuse to import")
    if all(inputs):
        validate_vendor_asset(*inputs)
    out = Path(args.outdir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    scene = original_scene()
    vendor = attach_licensed_collection(args) if all(inputs) else None
    scene.render.resolution_x = args.size
    scene.render.resolution_y = round(args.size * 9 / 16)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = args.samples
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(out / "cosmic_fx_study.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "cosmic_fx_study.blend"))
    bpy.ops.render.render(write_still=True)
    evidence = {
        "status": "render-created-not-artist-approved",
        "vendor_asset_loaded": bool(vendor),
        "vendor_asset": vendor,
        "native_original_effect": True,
        "blender_version": bpy.app.version_string,
        "dimensions": [scene.render.resolution_x, scene.render.resolution_y],
        "artistic_approval": False,
        "commercial_release_approved": False,
        "outputs": {f: sha256_file(out / f) for f in
                    ("cosmic_fx_study.png", "cosmic_fx_study.blend")}
    }
    (out / "cosmic_fx_evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PRYNTOR_COSMIC_FX_RENDER_COMPLETE", evidence["dimensions"], "vendor=", bool(vendor))


if __name__ == "__main__":
    main()
