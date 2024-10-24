#Polish finishes such as metallic, pearls and shimmers have extra particles that makes color classification harder
#I tried some image blurring techniques to make these images less noisy
#Median or Gaussian Blur had the best results
import cv2
import numpy as np
import colorsys
import math
import os
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
    #Return image with applied Gaussian blur
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

def convert_rgb_to_color_name(rgb_value):
    #First convert to HSL values, where h is in degrees and l,s are in %
    #HSL is easier for distinguishing between neutrals and non-neutrals
    r,g,b = rgb_value
    r,g,b = r/255.0, g/255.0, b/255.0
    hue,lightness,saturation = colorsys.rgb_to_hls(r,g,b)

    #Set-up for calculation
    # Convert hue to number of degrees
    hue = hue * 360

    print(f"HSL colors: {hue, saturation, lightness}")

    #In HSL model, "neutrals" are considered low saturation
    #moving luma to the lower end adds black to color, while the higher end adds white
    #https://vanseodesign.com/web-design/hue-saturation-and-lightness/#:~:text=Saturation%20refers%20to%20how%20pure,to%20a%2075%25%20saturated%20hue.:
    #saturation determines amount of gray in an image, where 1 is no gray (pure) and 0 is all gray

    #Changed the inspo code:
    #Color vs. Saturation: https://munsell.com/color-blog/difference-chroma-saturation/
    #https://photo.stackexchange.com/questions/14820/what-do-hue-chroma-saturation-value-tones-tints-shade-etc-mean
    #used this website to help determine color ranges: https://hslpicker.com/#c93644c7

    #https://stackoverflow.com/questions/75838909/how-to-get-rough-boundaries-to-classify-colors-into-named-colors
    unsaturated = saturation < 0.15
    if unsaturated:
        if lightness < 0.1:
            return "black"
        elif lightness < 0.9:
            return "gray"
        else:
            return "white"

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
    elif hue < 293:
        color = "purple"
    else:
        color = "red"

    #Classification: pink is either magenta (hot pink) or a lighter shade of red (white added to red)
    #for pink, high lightness and certain range of saturation below 0.5
    if color== "red" and lightness>0.7 and saturation > 0.5:
        color = "pink"

    return color


def classify_dominant_color_in_img(image_path):
    print(f"***** {image_path} *****")
    dominant_img = get_dominant_color_in_image(image_path)
    print('Dominant color is: rgb({})'.format(dominant_img))
    print("Color name: ", convert_rgb_to_color_name(dominant_img))

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



#Sources:
#https://stackoverflow.com/questions/32034344/accurately-detect-color-regions-in-an-image-using-k-means-clustering
#https://stackoverflow.com/questions/75838909/how-to-get-rough-boundaries-to-classify-colors-into-named-colors
#https://engineering.empathy.co/image-color-recognition-a-practical-example/

if __name__=='__main__':
    opi_image_path = 'sample_images/opi/'
    morgan_taylor_path = 'sample_images/morgan_taylor/'

    file_list = list_files(morgan_taylor_path)
    for file in file_list:
        if ".webp" in file:
            classify_dominant_color_in_img(file)

    # #https://stackoverflow.com/questions/72649116/best-way-to-loop-through-files
    # for img_name in morgan_taylor_imgs:
    #     image_path = morgan_taylor_path + img_name
    #     print(f"***** {img_name} *****")
    #     dominant_img = get_dominant_color_in_image(image_path)
    #     print('Dominant color is: rgb({})'.format(dominant_img))
    #     print("Color name: ", convert_rgb_to_color_name(dominant_img))
    #
    # for img_name in opi_imgs:
    #     image_path = opi_image_path + img_name
    #     print(f"***** {img_name} *****")
    #     dominant_img = get_dominant_color_in_image(image_path)
    #     print('Dominant color is: rgb({})'.format(dominant_img))
    #     print("Color name: ", convert_rgb_to_color_name(dominant_img))

    # image_path = morgan_taylor_path + 'shine_on_morgan_taylor.webp'
    # dominant_img = get_dominant_color_in_image(image_path)
    # print('Dominant color is: rgb({})'.format(dominant_img))
    # print("Color name: ", convert_rgb_to_color_name(dominant_img))
   #  # img = cv2.imread(image_path)
   #
   #
   #
   #  #Switch from BGR to RGB
   #  #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
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

