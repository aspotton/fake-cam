import cv2
import fcntl
import numpy as np

from imutils.video.webcamvideostream import WebcamVideoStream
from v4l2 import *

# Via: https://github.com/umlaeute/v4l2loopback/issues/32#issuecomment-52293220
def ConvertToYUYV(image):
    imsize = image.shape[0] * image.shape[1] * 2
    buff = np.zeros((imsize), dtype=np.uint8)

    img = cv2.cvtColor(image, cv2.COLOR_RGB2YUV).ravel()

    Ys = np.arange(0, img.shape[0], 3)
    Vs = np.arange(1, img.shape[0], 6)
    Us = np.arange(2, img.shape[0], 6)

    BYs = np.arange(0, buff.shape[0], 2)
    BUs = np.arange(1, buff.shape[0], 4)
    BVs = np.arange(3, buff.shape[0], 4)

    buff[BYs] = img[Ys]
    buff[BUs] = img[Us]
    buff[BVs] = img[Vs]

    return buff

class EnhancedWebcamVideoStream(WebcamVideoStream):
    def __init__(self, src=0, width=640, height=480, flip_vertical=True):
        super().__init__(src)

        self.width = width
        self.height = height
        self.flip_vertical = flip_vertical

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self._stream_read()
 
    def update(self):
        # keep looping infinitely until the thread is stopped
        while not self.stopped:
            self._stream_read()
 
    def _stream_read(self):
            (grabbed, frame) = self.stream.read()

            if self.flip_vertical:
                frame = cv2.flip(frame, 1)

            (self.grabbed, self.frame) = grabbed, frame

class OutputWebcamVideoStream:
    def __init__(self, device='/dev/video1', width=640, height=480, flip_horizontal=True):
        self.device_name = device
        self.width = width
        self.height = height
        self.flip_horizontal = flip_horizontal

        self.device = open(device, 'wb', 0)
        capability = v4l2_capability()
        fcntl.ioctl(self.device, VIDIOC_QUERYCAP, capability)

        fmt = V4L2_PIX_FMT_YUYV

        format = v4l2_format()
        format.type = V4L2_BUF_TYPE_VIDEO_OUTPUT
        format.fmt.pix.pixelformat = fmt
        format.fmt.pix.width = self.width
        format.fmt.pix.height = self.height
        format.fmt.pix.field = V4L2_FIELD_NONE
        format.fmt.pix.bytesperline = self.width * 3
        format.fmt.pix.sizeimage = self.width * self.height
        format.fmt.pix.colorspace = V4L2_COLORSPACE_SRGB

        fcntl.ioctl(self.device, VIDIOC_S_FMT, format)

    def write(self, image):
        if image.shape != (self.width, self.height, 3):
            image = cv2.resize(image, (self.width, self.height))

        if self.flip_horizontal:
            image = cv2.flip(image, 1)

        buff = ConvertToYUYV(image)
        self.device.write(buff)

# Via: https://stackoverflow.com/questions/40895785/using-opencv-to-overlay-transparent-image-onto-another-image
def overlay_transparent(background, overlay, x, y):

    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background

# Via: https://stackoverflow.com/questions/44650888/resize-an-image-without-distortion-opencv
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized

if __name__ == '__main__':
    width, height = 864, 480
    in_video = EnhancedWebcamVideoStream(src=0, width=width, height=height).start()
    out_video = OutputWebcamVideoStream(device='/dev/video1', width=width, height=height)

    holidays = cv2.imread('holidays.png', -1)
    holidays = image_resize(holidays, width=width)

    while True:
        frame = in_video.read().copy()

        # Do image manipulation
        frame = overlay_transparent(frame, holidays, 0, 0)

        out_video.write(frame)

    cv2.destroyAllWindows()
    in_video.stop()
