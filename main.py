import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, img_as_float, img_as_ubyte

# 读取图像并转换为float类型[0,1]
image = img_as_float(io.imread('2.png', as_gray=True))
image_8bit = img_as_ubyte(image)



# 检测边缘（Canny）
blurred = cv2.GaussianBlur(image_8bit, (5, 5), 1)  # 先模糊以减少梯度噪声
edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

# 膨胀边缘
kernel = np.ones((25, 25), np.uint8)  # 5x5膨胀核
edges_dilated = cv2.dilate(edges, kernel, iterations=1)

# 创建权重图（边缘膨胀区域为1，其他区域为模糊权重）
edges_weight = edges_dilated / 255.0  # 边缘区域为1，非边缘区域为0
non_edge_weight = 1 - edges_weight    # 非边缘区域为1，边缘区域为0

# 模糊非边缘区域
blurred_image = cv2.GaussianBlur(image_8bit, (9, 9), 3)  # 强模糊
# median_filtered = cv2.medianBlur(image_8bit, 11)  
enhanced_image = edges_weight * image_8bit + non_edge_weight * blurred_image

# 转换为8位图像以进行显示
enhanced_image_8bit = np.clip(enhanced_image, 0, 255).astype(np.uint8)

# 显示结果
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1, 5, figsize=(25, 5))

ax1.imshow(image, cmap='gray')
ax1.set_title("Original")
ax1.axis('off')

ax2.imshow(image_8bit, cmap='gray')
ax2.set_title("Median Filtered (Salt&Pepper Removed)")
ax2.axis('off')

ax3.imshow(edges, cmap='gray')
ax3.set_title("Canny Edges")
ax3.axis('off')

ax4.imshow(edges_dilated, cmap='gray')
ax4.set_title("Dilated Edges")
ax4.axis('off')

ax5.imshow(enhanced_image_8bit, cmap='gray')
ax5.set_title("Edge-Guided Smoothing")
ax5.axis('off')

plt.tight_layout()
plt.show()

# 可选：保存结果
io.imsave('edge_guided.png', image_8bit)
io.imsave('edge_guided_smoothing_no_salt_pepper.png', enhanced_image_8bit)
