import bpy
import bpy_extras
import os
from mathutils import Vector

# === SETTINGS ===
base_dir = "/Users/irodaibrohimova/Desktop/birdYolo/down" # change the file direction according to your setting here
boid_name = "Object_25" # change the name according to your setting here
scene = bpy.context.scene
camera = scene.camera

image_dir = os.path.join(base_dir, "images")
label_dir = os.path.join(base_dir, "labels")
os.makedirs(image_dir, exist_ok=True)
os.makedirs(label_dir, exist_ok=True)

# === FIXED BOUNDING BOX FUNCTION ===
def get_yolo_box_from_instance(inst):
    coords_2d = []
    obj = inst.instance_object
    if not obj:
        return None

    for corner in obj.bound_box:
        world_corner = inst.matrix_world @ Vector(corner)
        ndc = bpy_extras.object_utils.world_to_camera_view(scene, camera, world_corner)
        if ndc.z < 0:
            continue
        coords_2d.append((ndc.x, ndc.y))

    if not coords_2d:
        return None

    xs, ys = zip(*coords_2d)
    xmin = max(min(xs), 0.0)
    xmax = min(max(xs), 1.0)
    ymin = max(min(ys), 0.0)
    ymax = min(max(ys), 1.0)

    if xmax <= xmin or ymax <= ymin:
        return None

    shrink = 0.9  

    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    width = (xmax - xmin) * shrink
    height = (ymax - ymin) * shrink


    return (x_center, y_center, width, height)

# === MAIN LOOP ===
start_frame = 300
end_frame = 7900
step = 5

for frame in range(start_frame, end_frame + 1, step):
    scene.frame_set(frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    boxes = []

    for inst in depsgraph.object_instances:
        if not inst.is_instance:
            continue
        if not inst.instance_object or boid_name not in inst.instance_object.name:
            continue

        box = get_yolo_box_from_instance(inst)
        if box:
            boxes.append(box)

    # === SAVE IMAGE ===
    image_path = os.path.join(image_dir, f"frame_{frame:04d}.png")
    scene.render.filepath = image_path
    bpy.ops.render.render(write_still=True)

    # === SAVE LABELS ===
    label_path = os.path.join(label_dir, f"frame_{frame:04d}.txt")
    with open(label_path, "w") as f:
        for x, y, w, h in boxes:
            f.write(f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

    print(f"✅ Frame {frame}: Saved {len(boxes)} boxes")
  