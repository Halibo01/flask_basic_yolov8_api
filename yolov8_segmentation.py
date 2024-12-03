import cv2
import numpy as np
import os
import time


def checktime(loc, minutes):
    timer = int(time.time())
    for i in [i for i in os.listdir(loc) if i.endswith(".txt")]:
        file_p = os.path.join(loc, i)
        with open(file_p, "r") as file:
            time2 = file.read()
        if timer - int(time2) >= minutes * 60:
            os.remove(file_p)
            os.remove(file_p[:-3] + "png")

def getpersonsegmentation(model, imagepath, destination):
    os.makedirs(destination, exist_ok=True)
    image = cv2.imread(imagepath)
    print(imagepath)
    os.remove(imagepath)
    results = model(image, verbose=False, conf=0.6)  
    kernel = np.ones((7, 7), np.uint8)  
    try:
        masks = results[0].masks.data.cpu().numpy() 
    except:
        return False
    
    classes = results[0].boxes.cls.cpu().numpy()
    person_class_id = 0 

    # find 'person' class
    person_mask_indices = [i for i, cls in enumerate(classes) if int(cls) == person_class_id]
    person_masks = [masks[i] for i in person_mask_indices]
    # If person not detected
    if person_masks:
        combined_mask = np.zeros_like(person_masks[0]) 
        for mask in person_masks:
            combined_mask = np.logical_or(combined_mask, mask > 0.5)  
    else:
        return False

    binary_mask = combined_mask.astype(np.uint8)
    binary_mask_resized = cv2.resize(binary_mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    
    
    binary_mask_resized = cv2.erode(binary_mask_resized, kernel=kernel, iterations=4)
    binary_mask_resized = cv2.GaussianBlur(binary_mask_resized, (151, 151), 0)
    binary_mask_resized = binary_mask_resized[:, :, np.newaxis]  

    
    rgba_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA) 
    rgba_image[:, :, 3] = binary_mask_resized[:, :, 0] * 255

    
    rgba_image[rgba_image[:, :, 3] == 0] = [0, 0, 0, 0]
    
    filename = os.path.join(destination, os.path.basename(imagepath).split(".")[0] + ".png")
    cv2.imwrite(filename, rgba_image)
    with open(filename[:-3] + "txt", "w") as file:
        file.write(str(int(time.time())))
    return filename.replace("\\", "/")

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return list(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def changebgcolor(pngimagepath:str, hex:str, destination:str):
    pngimage = cv2.imread(pngimagepath, cv2.IMREAD_UNCHANGED)
    r, g, b = hex_to_rgb(hex)
    rgbcode = [b, g, r]
    pngimage[pngimage[:, :, 3] == 0] = rgbcode + [255]
    bgrimage = cv2.cvtColor(pngimage, cv2.COLOR_BGRA2BGR)
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    cv2.imwrite(destination, bgrimage)

def delete_all_png_files(folder_path):
    
    for filename in os.listdir(folder_path):
        
        if filename.endswith(".png"):
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                ...