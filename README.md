# Aruco speed up
我们在面对视频处理任务时，在如标题所示的条件下，对Aruco进行检测，我们发现检测速度非常缓慢。通过对不同光照条件的测试，我们发现Aruco的识别精度依然很高，但是检测速度会非常缓慢。我通过对Aruco的检测原理分析得出，影响速度的主要原因是由于低光照的噪点产生的。

In video processing tasks, we encountered a problem where the detection speed of Aruco was very slow under the conditions described in the title. Through testing under different lighting conditions, we found that while the recognition accuracy of Aruco remained high, the detection speed was significantly slowed down. After analyzing the detection principle of Aruco, I concluded that the main factor affecting the speed was the noise caused by low lighting conditions.

针对这个原因，我认为可以提供一个快速预处理的函数模块对检测的图片进行处理，提高Aruco的检测速度，以此满足视频处理任务中即时性的要求，同时对于一些正常光照条件下的任务可以提高鲁棒性。

To address this issue, I believe a fast preprocessing function module can be introduced to process the images being detected, improving Aruco's detection speed. This would help meet the real-time requirements of video processing tasks, while also enhancing robustness for tasks under normal lighting conditions.

通过一系列的实验，我找到了一些办法来解决速度的性能问题，同时希望抛出这个问题来引发社区的讨论，对并当前的方法进行改进。

Through a series of experiments, I have found some solutions to address the performance issues with speed, and I would like to raise this issue to spark discussion within the community, as well as to improve the current methods.

方案一：AI去噪 对图片的噪声进行修复可以在一定程度上抑制噪点，通过这样的方式我们可以加速检测速度，但是AI-denoise模型进行检测需要花费1-2s的时间，这样的时间消耗同样是我们视频处理任务中不能容忍的。

Solution 1: AI Denoising Denoising the image can reduce the noise to some extent and thus speed up detection. However, applying an AI denoise model takes 1-2 seconds, which is still unacceptable in real-time video processing tasks.

方案二：yolo+aruco 通过对yolo进行训练，通过大量的样本数据集对aruco标记进行训练我们可以在光线条件较差的环境中依然快速进行检测和识别。这个方法的成本较高，首先需要对数据集进行整理，其次对yolo进行训练，并通过识别检测的方式提取出四边形四个顶点的位置，需要对aruco中原本的函数进行大量的自定义操作，最后获取具有顺序的顶点坐标序列。检测时间大概在100ms/张。由于yolo方法的实现成本较高，且OpenCV社区Aruco以传统图像处理方法居多，所以我们在尝试其他的方案，此方案进行备选。

Solution 2: YOLO + Aruco By training YOLO on a large dataset of Aruco markers, we can still achieve fast detection and recognition in low-light environments. However, this method has a high cost: it requires organizing the dataset, training YOLO, and extracting the four corner coordinates of the quadrilateral through detection. It also requires extensive custom modifications to the original Aruco functions to obtain the ordered sequence of corner coordinates. The detection time is around 100ms per frame. Since the implementation cost of the YOLO method is high and the OpenCV community primarily uses traditional image processing methods for Aruco, we are considering alternative solutions, with this one as a backup.

方案三：视频记录点 在视频采集的过程当中，我注意到Aruco标记过程中具有连续性质的特点，即记录当前帧的aruco的位置，在下一帧不会出现大范围的移动。首先，aruco标记码属于小目标检测的范围，这代表着大部分的图片中的其他位置都是无关信息，而其中又充斥着大量的噪点负面信息。所以利用上述连续性的特质，我们可以对检测的部分进行划定。即绿色是当前当前帧检测出来的位置区域范围，红色往外拓展的为下一帧的参考范围，范围的缩小可以极大程度上加快aruco代码的检测速度。我们需要保存上帧不同id的aruco码的位置，然后在下一帧的时候框出小区域进行检测就可以实现此效果，当然我们需要设定相应的边界条件。

Solution 3: Video Tracking Points During video capture, I noticed that Aruco markers have a continuous property, meaning that the position of Aruco in the current frame doesn't move significantly in the next frame. First, Aruco markers are small target detections, which means that most of the other areas in the image are irrelevant, often filled with noise. By leveraging this continuity, we can focus detection on certain areas. The green region represents the detected area in the current frame, and the red region extends outward to form a reference for the next frame. Reducing the area can significantly speed up Aruco code detection. We need to save the positions of different Aruco markers in the previous frame and then define a small region for detection in the next frame, of course with appropriate boundary conditions.

方案四：方案四的设计是基于方案三中进行改进，我们发现都是对图片中感兴趣的区域进行检测，并且舍弃大部分的区域来加快aruco的检测速度。但是，方案三的实现较为复杂，其中涉及到了部分的aruco点的存取读写操作，同时视频处理任务中有多线程实现的需求，针对前后序列帧可能不在同一线程中运行需要进一步对线程代码进行修改处理，由此方案四应运而生。

Solution 4: Solution 4 is based on improvements made to Solution 3. We found that both solutions focus on detecting areas of interest in the image and discarding most of the irrelevant regions to speed up Aruco detection. However, Solution 3 is relatively complex, involving read/write operations for some Aruco points. Additionally, video processing tasks often require multi-threading, and frames in the sequence might not be processed in the same thread. This requires further modifications to the thread handling code, giving rise to Solution 4.

我们发现在图片中aruco具有较为明显的边界条件，基于此我们可以通过canny边界＋膨胀核的做法膨胀出感兴趣的区域，但是需要注意我们的背景不能是非常复杂的环境，不然的效果可能不如yolo训练出来的效果好！这也是我希望进行讨论的关键点，因为这一加速方法需要在背景条件并不复杂的情况才会有好的效果。在我目前项目中已经可以满足任务需求了，但是社区可以基于此进行讨论和功能的改进。

We found that Aruco markers in images have clear boundary conditions. Based on this, we can use the Canny edge detection algorithm combined with a dilation kernel to expand the area of interest. However, it is important to note that this method works best in simple backgrounds; if the environment is too complex, the results may not be as good as those achieved with a YOLO-trained model. This is a key point I hope to discuss, as this acceleration method works well only in scenarios with less complex backgrounds. It meets the needs of my current project, but I invite the community to discuss and improve upon this approach.
 
