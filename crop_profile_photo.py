import os
from PIL import Image

# Path to the backup of your original uncropped photo
backup_path = 'bhaiyya_website/bhaiyaa website/final_lady_original_backup.jpeg'

# Path to the active cropped photo displayed on the website
output_path = 'bhaiyya_website/bhaiyaa website/final_lady.jpeg'

# EDIT THIS NUMBER: How many pixels to cut off from the top of the original image
# 390 was too much (cut off the head slightly). Let's try 320.
TOP_CROP_PIXELS = 200

if not os.path.exists(backup_path):
    print(f"Error: Original backup file not found at {backup_path}")
    print("Please make sure the backup image exists.")
else:
    # Load original image
    img = Image.open(backup_path)
    width, height = img.size
    print(f"Original size: {width}x{height} pixels.")

    # Crop box dimensions: (left, top, right, bottom)
    crop_box = (0, TOP_CROP_PIXELS, width, height)
    cropped_img = img.crop(crop_box)

    # Save over the website image
    cropped_img.save(output_path, quality=95)
    print(f"Success! Cut off {TOP_CROP_PIXELS} pixels from the top.")
    print(f"New image saved to: {output_path} (size: {cropped_img.size})")
