from skimage.metrics import structural_similarity as ssim
import numpy as np
import cv2
import matplotlib.pyplot as plt
import numpy
from PIL import Image


def compare_images(i1, i2):

    open_cv_image = numpy.array(i1)
    # Convert RGB to BGR
    i1 = open_cv_image[:, :, ::-1].copy()
    open_cv_image = numpy.array(i2)
    # Convert RGB to BGR
    i2 = open_cv_image[:, :, ::-1].copy()

    w1, w2 = i1.shape[0], i1.shape[1]
    w3, w4 = i2.shape[0], i2.shape[1]

    # print(w1,w2,w3,w4)

    if(w1*w2 > w3*w4):
        i1 = cv2.resize(i1, (w4, w3), interpolation=cv2.INTER_AREA)
    else:
        i2 = cv2.resize(i2, (w2, w1), interpolation=cv2.INTER_AREA)

    hist_img1 = cv2.calcHist([i1], [0, 1, 2], None, [
                             256, 256, 256], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist_img1, hist_img1, alpha=0,
                  beta=1, norm_type=cv2.NORM_MINMAX)
    hist_img2 = cv2.calcHist([i2], [0, 1, 2], None, [
                             256, 256, 256], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist_img2, hist_img2, alpha=0,
                  beta=1, norm_type=cv2.NORM_MINMAX)

    # Color Histogram similarity
    clr_metric = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_CORREL)

    i1 = cv2.cvtColor(i1, cv2.COLOR_BGR2GRAY)
    i2 = cv2.cvtColor(i2, cv2.COLOR_BGR2GRAY)
    # SSIM similarity
    ssim_metric = ssim(i1, i2)

    print("Color Similarity: ", clr_metric)
    print("SSIM Similarity: ", ssim_metric)

    if (ssim_metric >= 0.95 and clr_metric >= 0.95):
        return True
    else:
        return False


# i1 = cv2.imread("i.jpeg")
# i2 = cv2.imread("icomp.jpeg")

# '''
# fig = plt.figure("Images")
# images = ("i1", i1), ("i2", i2)
# for (i, (name, image)) in enumerate(images):
# 	ax = fig.add_subplot(1, 3, i + 1)
# 	ax.set_title(name)
# 	plt.imshow(image, cmap = plt.cm.viridis)
# 	plt.axis("off")
# plt.show()
# '''

# compare_images(i1, i2)  # if true, images are sufficiently similar
