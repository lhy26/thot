try:
    import md5
    md5 = md5.new
except ImportError:
    from hashlib import md5

from thotus import settings

import cv2

class CalibrationData(object):

    def __init__(self):
        self.width = 0
        self.height = 0

        self._camera_matrix = None
        self._distortion_vector = None
        self._roi = None
        self._dist_camera_matrix = None
        self._weight_matrix = None

        self._md5_hash = None

        self.laser_planes = [settings.Attribute() for _ in range(settings.LASER_COUNT)]
        self.platform_rotation = None
        self.platform_translation = None

    def set_resolution(self, width, height):
        if self.width != width or self.height != height:
            self.width = width
            self.height = height
            self._compute_weight_matrix()

    def undistort_image(self, image):
        cam_matrix , roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.distortion_vector, image.shape[:2], 1, image.shape[:2])
        dst = cv2.undistort(image,
                self.camera_matrix,
                self.distortion_vector,
                None,
                cam_matrix)
        x, y, w, h = roi
        dst = dst[x:x+w,y:y+h]
        return dst

    @property
    def camera_matrix(self):
        return self._camera_matrix

    @camera_matrix.setter
    def camera_matrix(self, value):
        self._camera_matrix = value
        self._compute_dist_camera_matrix()

    @property
    def distortion_vector(self):
        return self._distortion_vector

    @distortion_vector.setter
    def distortion_vector(self, value):
        self._distortion_vector = value
        self._compute_dist_camera_matrix()

    @property
    def dist_camera_matrix(self):
        return self._dist_camera_matrix

    @property
    def weight_matrix(self):
        return self._weight_matrix

    def _compute_dist_camera_matrix(self):
        if self._camera_matrix is not None and self._distortion_vector is not None:
            self._dist_camera_matrix, self._roi = cv2.getOptimalNewCameraMatrix(
                self._camera_matrix, self._distortion_vector,
                (int(self.width), int(self.height)), alpha=1)
            self._md5_hash = md5()
            self._md5_hash.update(self._camera_matrix)
            self._md5_hash.update(self._distortion_vector)
            self._md5_hash = self._md5_hash.hexdigest()

    def md5_hash(self):
        return self._md5_hash