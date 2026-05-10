import cv2
import threading
from queue import Queue

class CameraCapture:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.frame_queue = Queue(maxsize=1)
        self.running = False
        self.thread = None

    def start(self):
        """Start camera capture in background thread"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera")

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        """Continuously capture frames"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Keep only latest frame
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
                self.frame_queue.put(frame)

    def get_frame(self):
        """Get latest frame"""
        try:
            return self.frame_queue.get_nowait()
        except:
            return None

    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
