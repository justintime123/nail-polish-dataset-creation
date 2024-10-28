
import cv2
import numpy as np
import colorsys
import math
import os
import pandas as pd
from scipy.stats import false_discovery_control


def gaussian_blur(image, kernel_size):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def box_blur(image, kernel_size):
    return cv2.blur(image, (kernel_size, kernel_size))

def bilateral_blur(image, d, sigma_color, sigma_space):
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

def median_blur(image, kernel_size):
    return cv2.medianBlur(image, kernel_size)

def get_image(img_path):
    return cv2.imread(img_path)

def crop_image(img):
    # Return cropped image according to preset proportions
    # https://stackoverflow.com/questions/15589517/how-to-crop-an-image-in-opencv-using-python
    # Take certain proportion from left, right, top and bottom
    # Use same proportions for all images
    # I figured out what proportions to cut for morgan taylor to remove whitespace, and will apply same proportional cropping to OPI

    # how much to crop relative to total x and y
    x_crop = 295 / 1680
    y_crop = 305 / 1680
    length, width, _ = img.shape

    crop_length = int(x_crop * length)
    crop_width = int(y_crop * width)
    x_max = int(length - crop_length)
    y_max = int(width - crop_width)

    # Dimensions
    #print('Original dimensions: ', img.shape)
    img = img[crop_length:x_max, crop_width:y_max]
    return img

def apply_blur(img):
    # Polish finishes such as metallic, pearls and shimmers have extra particles that makes color classification harder
    # I tried some image blurring techniques to make these images less noisy
    # Median or Gaussian Blur had the best results
    # I used code from this Medium article: https://medium.com/@henriquevedoveli/blur-in-image-processing-an-introductory-guide-88a9550985e7
    return gaussian_blur(img, 15)

def get_dominant_color_using_k_means(img):
    # Use K-means to find dominant color
    # https://stackoverflow.com/a/50900494
    data = np.reshape(img, (-1, 3))
    #print(data.shape)
    data = np.float32(data)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)

    return centers[0].astype(np.int32)

def transform_image(img):
    #Crop image to remove most of white background in Morgan Taylor images
    img_crop = crop_image(img)
    #Convert from gbr to rgb
    img_rgb = cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB)
    #Apply blur to reduce noise in shimmers and other polishes with particles
    #Blur will make it easier to identify underlying base color/hue
    img_blur = apply_blur(img_rgb)
    return img_blur


def get_dominant_color_in_image(img_path):
    img = get_image(img_path)
    img_transform = transform_image(img)
    dominant_color = get_dominant_color_using_k_means(img_transform)
    #Return dominant color in RGB
    return dominant_color

def convert_rgb_to_hsl(rgb_value):
    # First convert to HSL values, where h is in degrees and l,s are in %
    # HSL is easier for distinguishing between neutrals and non-neutrals
    r, g, b = rgb_value
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)

    # Set-up for calculation
    # Convert hue to number of degrees
    hue = hue * 360

    return hue, saturation, lightness

def convert_hsl_to_color_name(hsl_value):

    hue,saturation,lightness = hsl_value

    #In HSL model, "neutrals" are considered low saturation
    #moving luma to the lower end adds black to color, while the higher end adds white
    #https://vanseodesign.com/web-design/hue-saturation-and-lightness/#:~:text=Saturation%20refers%20to%20how%20pure,to%20a%2075%25%20saturated%20hue.:
    #saturation determines amount of gray in an image, where 1 is no gray (pure) and 0 is all gray

    #Inspo code: https://stackoverflow.com/questions/75838909/how-to-get-rough-boundaries-to-classify-colors-into-named-colors
    #Changed code from luna to saturation
    #Color vs. Saturation: https://munsell.com/color-blog/difference-chroma-saturation/
    #https://photo.stackexchange.com/questions/14820/what-do-hue-chroma-saturation-value-tones-tints-shade-etc-mean
    #I used this website to help determine color ranges: https://hslpicker.com/#c93644c7

    unsaturated = saturation < 0.15
    if unsaturated:
        if lightness < 0.1:
            return "black (neutral)"
        elif lightness < 0.9:
            return "gray (neutral)"
        else:
            return "white (neutral)"

    color = ""

    #Determining color for non-neutrals, using hue
    #if lightness = 0.5, the color is considered saturated
    #increasing lightness adds white/makes color lighter
    #e.g., adding white to red range creates pink
    if hue < 8:
        color = "red"
    elif hue <37:
        if lightness < 0.15:
            color =  "brown"
        else:
            color =  "orange"
    elif hue < 71:
        color = "yellow"
    elif hue < 173:
        color = "green"
    elif hue < 263:
        color = "blue"
    elif hue < 300:
        color = "purple"
    elif hue < 335:
        #formerly 330
        #For simplicity, I'll assume magenta is pink
        color = "pink (magenta)"
    else:
        color = "red"

    #Classification: pink is either magenta (hot pink) or a lighter shade of red (white added to red)
    #for pink, high lightness and certain range of saturation below 0.5
    #pink is a lighter shade of red, rose or magenta
    #TODO: Add in magenta range (see High Voltage)
    #https://simple.wikipedia.org/wiki/Magenta
    #https://en.wikipedia.org/wiki/Shades_of_magenta#:~:text=Magenta%20is%20a%20color%20made,a%20hue%20of%20300%C2%B0.
    #https://www.google.com/search?q=how+to+get+pink+from+magenta+in+hsl&sca_esv=26201d1b1489b96d&sxsrf=ADLYWILt-7jvj2_d1sAQnUJUa4j1c634NQ%3A1730009547380&ei=y9kdZ7f0Fv-p5NoPkZyw0AY&ved=0ahUKEwj3hZ7k862JAxX_FFkFHREODGoQ4dUDCBA&uact=5&oq=how+to+get+pink+from+magenta+in+hsl&gs_lp=Egxnd3Mtd2l6LXNlcnAiI2hvdyB0byBnZXQgcGluayBmcm9tIG1hZ2VudGEgaW4gaHNsMgcQIRigARgKMgcQIRigARgKMgcQIRigARgKMgcQIRigARgKMgcQIRigARgKSKQRUNoCWLsPcAF4AZABAJgBhQGgAcEFqgEDNC4zuAEDyAEA-AEBmAIIoALiBcICChAAGLADGNYEGEfCAgYQABgWGB7CAggQABgWGB4YD8ICCxAAGIAEGIYDGIoFwgIIEAAYgAQYogTCAggQABgWGAoYHsICCBAAGKIEGIkFwgIFECEYoAHCAgUQIRirAsICBRAhGJ8FmAMAiAYBkAYIkgcDNS4zoAfaKQ&sclient=gws-wiz-serp
    #https://www.google.com/search?q=is+magenta+and+pink+same&oq=is+magenta+and+pink&gs_lcrp=EgZjaHJvbWUqBwgAEAAYgAQyBwgAEAAYgAQyBggBEEUYOTIICAIQABgWGB4yCAgDEAAYFhgeMggIBBAAGBYYHjIICAUQABgWGB4yCAgGEAAYFhgeMggIBxAAGBYYHjIICAgQABgWGB4yCAgJEAAYFhge0gEINDA5MGowajmoAgCwAgE&sourceid=chrome&ie=UTF-8
    if color== "red" and lightness>=0.65 and not unsaturated:
        color = "pink (light red)"

    return color


def classify_dominant_color_in_img(image_path):
    file_name = image_path.split("/")[-1]
    product_name = file_name.partition("-SWATCH")[0]
    original_color_name = image_path.split("/")[-2]

    dominant_rgb_color = get_dominant_color_in_image(image_path)
    dominant_hsl_color = convert_rgb_to_hsl(dominant_rgb_color)
    new_color_name = convert_hsl_to_color_name(dominant_hsl_color)

    return {'product_name': product_name, 'dominant_color_rgb': dominant_rgb_color, 'dominant_color_hsl': dominant_hsl_color,
            'original_color_name': original_color_name, 'new_color_name': new_color_name}

def list_files(dir):
    #https://stackoverflow.com/questions/19932130/iterate-through-folders-then-subfolders-and-print-filenames-with-path-to-text-f
    r = []
    subdirs = [x[0] for x in os.walk(dir)]
    for subdir in subdirs:
        files = os.walk(subdir).__next__()[2]
        if (len(files) > 0):
            for file in files:
                r.append(os.path.join(subdir, file))
    return r


def test_classification_on_sample_images():
    opi_image_path = 'sample_images/opi/'
    morgan_taylor_path = 'sample_images/morgan_taylor/'

    file_list = list_files(morgan_taylor_path)
    results = []
    for file in file_list:
        if ".webp" in file:
            res = classify_dominant_color_in_img(file)
            results.append(res)

    #save results to an Excel file
    #will add extra column to keep track of correct vs. incorrect classifications
    df = pd.DataFrame(results)
    print(df)
    df.to_excel('ImageClassificationTest.xlsx')
    pass


#Sources:
#https://stackoverflow.com/questions/32034344/accurately-detect-color-regions-in-an-image-using-k-means-clustering
#https://stackoverflow.com/questions/75838909/how-to-get-rough-boundaries-to-classify-colors-into-named-colors
#https://engineering.empathy.co/image-color-recognition-a-practical-example/

if __name__=='__main__':
    test_classification_on_sample_images()
   #
   #  #Apply blur to reduce noise in shimmers and other polishes with particles
   #  #https://medium.com/@henriquevedoveli/blur-in-image-processing-an-introductory-guide-88a9550985e7
   #  img_gaussian_blur = gaussian_blur(img, 15)
   #  # img_box_blur = box_blur(img, 15)
   #  # img_bilateral_blur = bilateral_blur(img, d=9, sigma_color=75, sigma_space=75)
   #  img_median_blur = median_blur(img, 5)
   #
   #  #Resize
   #  #img_gaussian_blur = cv2.resize(img_gaussian_blur, (50, 50))
   #  #cv2.imshow('Gaussian', img_gaussian_blur)
   #
   #  #open_cv_image = np.array(img_gaussian_blur)
   #  #open_cv_image = open_cv_image[:, :, ::-1].copy()
   #  #img = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB)
   #
   #  #resize_factor = 0.75
   #  # k_means = KMeans(n_clusters=4)
   #  # k_means.fit(img_gaussian_blur)
   #  #
   #  # colors = np.asarray(k_means.cluster_centers_, dtype='uint8')
   #
   #
   #  cv2.imshow('Original', img)
   #  cv2.imshow('Gaussian', img_gaussian_blur)
   # # cv2.imshow('Box', img_box_blur)
   #  # cv2.imshow('Bilateral', img_bilateral_blur)
   #  cv2.imshow('Median', img_median_blur)
   #
   #  cv2.waitKey(0)
   #  cv2.destroyAllWindows()

