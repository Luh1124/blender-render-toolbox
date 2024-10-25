# import blenderproc as bproc

import json
import os
import sys

import imageio.v2 as imageio
import cv2

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toolbox import SceneHandler, rgba_to_rgb
from toolbox.camera import get_camera_positions_on_sphere

scener = SceneHandler()

# Initialize the render engine
# scener.init_render_engine("BLENDER_EEVEE")
scener.init_render_engine("CYCLES")

# Initialize the camera
# import ipdb; ipdb.set_trace()

cam_default = scener.init_camera()

# Import the object, preprocess it and normalize the scene into [-1, 1]

obj_path = "/pfs/mt-1oY5F7/lihong/nips/GenTexture/rendering/examples/1a57a0d6609145b486ed5b1d3e9ec7fb.glb"

scener.import_object(
    # "vertex_colored",
    # "assets/objects/vertex_colored.obj",
    # vertex_color=(0.52941, 0.80784, 0.92157),
    "glb",
    obj_path,
    # "/pfs/mt-1oY5F7/ss-3d/objaverse/hf-objaverse-v1/glbs/000-000/001abb1a3f4c412fbd707239acb68cd6.glb"
)


scener.preprocess_objs()
scener.normalize_scene(range=2)

# Set the environment light
# scener.set_env_light(env_light=1.0)
scener.set_env_light(env_path="assets/env_textures/brown_photostudio_02_1k.exr")

# Prepare camera layout and add to the scene
distance = 3

cam_positions, cam_mats, eles, azis = get_camera_positions_on_sphere(
    center=(0, 0, 0), radius=distance, elevations=[0], num_per_layer=20
)


for camera_matrix in cam_mats:
    scener.add_camera(camera_matrix)

# Set rendering output and render
base_name = os.path.basename(obj_path).split(".")[0]
output_dir = "outputs_512/" + base_name
width, height = 512, 512
scener.set_output(
    output_dir=output_dir,
    width=width,
    height=height,
    # output_types=["color", "normal", "depth", "albedo", "pbr"], #[color, normal, depth, albedo, pbr, position, UV, alpha, ]
    # output_types=["color", "normal", "depth", "albedo", "pbr", "position", "UV", "alpha", "word_normal"],
    # output_types=["color", "normal", "depth", "albedo", "word_normal", "pbr", "alpha"],
    output_types=["color", "normal", "depth", "albedo", "word_normal", "pbr"],
)
scener.render()

# Prepare and save meta info
fov_x = cam_default.data.angle_x
meta_info = {
    "distance": distance,
    "sensor_width_mm": cam_default.data.sensor_width,
    "focal_length_mm": cam_default.data.lens,
    "fov_x": fov_x,
    "width": width,
    "height": height,
    "locations": [],
    "scale_mat": scener.scale_mat,
}
for i in range(len(cam_positions)):
    index = "{0:04d}".format(i)
    meta_info["locations"].append(
        {
            "index": index,
            "elevation": eles[i],
            "azimuth": azis[i],
            "transform_matrix": cam_mats[i].tolist(),
        }
    )
with open(os.path.join(output_dir, "meta.json"), "w") as f:
    json.dump(meta_info, f, indent=4)

# Save rendered color images to video
rgb_images = []
mask_images = []
color_output_dir = os.path.join(output_dir, "color")
for f in sorted(os.listdir(color_output_dir)):
    if f.startswith("render_"):
        img = imageio.imread(os.path.join(color_output_dir, f))
        mask_images.append(img[:, :, 3])
        rgb_images.append(rgba_to_rgb(img))

# save mask to dir
mask_output_dir = os.path.join(output_dir, "mask")
os.makedirs(mask_output_dir, exist_ok=True)
for i, mask in enumerate(mask_images):
    imageio.imwrite(os.path.join(mask_output_dir, f"mask_{i:04d}.png"), mask)
    # cv2.imwrite(os.path.join(mask_output_dir, f"mask_{i:04d}.png"), mask)

video_path = os.path.join(output_dir, "render.mp4")
imageio.mimsave(video_path, rgb_images, fps=24)
print(f"Video saved to {video_path}")
