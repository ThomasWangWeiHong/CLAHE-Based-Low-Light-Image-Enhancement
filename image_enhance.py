import cv2
import numpy as np


clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize = (8, 8))

def low_light_enhance(image, clahe):
	# Conversion from RGB Color Space to HSV Color Space
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	# Inversion of Intensity Image
	v = hsv[:, :, 2]
	I = 255 - v

	# Contrast Limited Adaptive Histogram Equalization (CLAHE) for Inverted Intensity Image
	clahe_I = clahe.apply(I)

	# Gamma-Enhanced Image
	clahe_I_norm = clahe_I / 255
	gamma_5_I = np.power(clahe_I_norm, 5)

	# Morphological Top-Hat Transformation Operation on Gamma-Enhanced Image with Gamma = 5
	gamma_5_I_top = np.clip(gamma_5_I * 255, 0, 255).astype('uint8')
	structuring_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
	tophat_image = cv2.morphologyEx(gamma_5_I_top, cv2.MORPH_TOPHAT, structuring_element)
	tophat_image = tophat_image / 255

	# Image Fusion
	tophat_image_flat = tophat_image.reshape(-1, 1)
	clahe_I_flat = clahe_I_norm.reshape(-1, 1)
	x = np.hstack((clahe_I_flat, tophat_image_flat))
	c = np.cov(x, rowvar = False)
	eigenvalues, eigenvectors = np.linalg.eig(c)
	max_index = np.argmax(eigenvalues)
	max_vector = eigenvectors[:, max_index]
	w1 = max_vector[0] / sum(max_vector)
	w2 = max_vector[1] / sum(max_vector)
	f = w1 * clahe_I_norm + w2 * tophat_image
	f = np.clip(f, 0, 1)

	# Inversion of Fused Image
	f_inv = 1 - f

	# Replacement of Original Intensity Channel with New Fused Image
	hsv[:, :, 2] = (f_inv * 255).astype(np.uint8)

	# Conversion from HSV Color Space Back to RGB Color Space
	return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
