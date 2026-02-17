from Scripts.Modules.Feed import feed
from Scripts.Modules.Data import project_data
from pathlib import Path
import cv2
from cv2.typing import Matlike

class Feed(feed.Feed):
    '''
    A class for processing camera feeds of dice rolls.
    '''
    def __init__(
            self, 
            cam_index: int = 0, 
            logging: bool = False,
            data: project_data.ProjectData = None,
        ) -> None:
        super().__init__(
            logging=logging,
            data=data
        )
        self.cam_index: int = cam_index
        self.frame: Matlike = None
        self.cap = None
        self.open_source()
        
        if self.logging:
            print(f"Initialized Camera Feed with index {self.cam_index}")

    def open_source(self):
        """Open the feed source based on the feed type."""
        self.cap = cv2.VideoCapture(self.cam_index)
        # This initializes a whole suite of values storing the initial cam settings
        self.read_in_default_cam_settings()
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera source with index: {self.cam_index}")
        if self.logging:
            print(f"Opened camera source with index: {self.cam_index}")

    def close_source(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def capture_frame(self):
        """Capture a frame from the camera feed."""
        if self.cap is None:
            raise ValueError("Camera source is not opened.")
        ret, self.frame = self.cap.read()
        if not ret:
            raise ValueError("Could not read frame from camera source.")
        if self.logging:
            print(f"Captured frame from camera source with index: {self.cam_index}")

    def read_in_default_cam_settings(self):
        self.focus_default = self.cap.get(cv2.CAP_PROP_FOCUS)
        self.exposure_default = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        self.brightness_default = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        self.contrast_default = self.cap.get(cv2.CAP_PROP_CONTRAST)
        self.saturation_default = self.cap.get(cv2.CAP_PROP_SATURATION)
        self.hue_default = self.cap.get(cv2.CAP_PROP_HUE)
        self.sharpness_default = self.cap.get(cv2.CAP_PROP_SHARPNESS)
        self.gain_default = self.cap.get(cv2.CAP_PROP_GAIN)
        self.white_balance_default = self.cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)
        self.focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        self.exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        self.brightness = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        self.contrast = self.cap.get(cv2.CAP_PROP_CONTRAST)
        self.saturation = self.cap.get(cv2.CAP_PROP_SATURATION)
        self.hue = self.cap.get(cv2.CAP_PROP_HUE)
        self.sharpness = self.cap.get(cv2.CAP_PROP_SHARPNESS)
        self.gain = self.cap.get(cv2.CAP_PROP_GAIN)
        self.white_balance = self.cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)
        #print a statement showing me the value for each of these now
        print(f"Focus: {self.focus_default}")
        print(f"Exposure: {self.exposure_default}")
        print(f"Brightness: {self.brightness_default}")
        print(f"Contrast: {self.contrast_default}")
        print(f"Saturation: {self.saturation_default}")
        print(f"Hue: {self.hue_default}")
        print(f"Sharpness: {self.sharpness_default}")
        print(f"Gain: {self.gain_default}")
        print(f"White Balance: {self.white_balance_default}")

    def reset_cam_settings(self):
        # TODO: Verify settings work correctly
        self.cap.set(cv2.CAP_PROP_FOCUS, self.focus_default)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure_default)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness_default)
        self.cap.set(cv2.CAP_PROP_CONTRAST, self.contrast_default)
        self.cap.set(cv2.CAP_PROP_SATURATION, self.saturation_default)
        self.cap.set(cv2.CAP_PROP_HUE, self.hue_default)
        self.cap.set(cv2.CAP_PROP_SHARPNESS, self.sharpness_default)
        self.cap.set(cv2.CAP_PROP_GAIN, self.gain_default)
        self.cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, self.white_balance_default)
    
    def adjust_cam_setting(self, setting: str, value: int):
        """Adjust a camera setting."""
        if self.cap:
            if setting == "focus":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                else:
                    self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                    self.cap.set(cv2.CAP_PROP_FOCUS, value)
                    print(f"Focus set to: {self.cap.get(cv2.CAP_PROP_FOCUS)}")
            elif setting == "exposure":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
                else:
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
                    self.cap.set(cv2.CAP_PROP_EXPOSURE, value)
            elif setting == "brightness":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
                else:
                    self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)
            elif setting == "contrast":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_CONTRAST, self.contrast)
                else:
                    self.cap.set(cv2.CAP_PROP_CONTRAST, value)
            elif setting == "saturation":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_SATURATION, self.saturation)
                else:
                    self.cap.set(cv2.CAP_PROP_SATURATION, value)
            elif setting == "gain":
                print('Setting gain is currently disabled')
                # self.cap.set(cv2.CAP_PROP_GAIN, value)
            elif setting == "hue":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_HUE, self.hue)
                else:
                    self.cap.set(cv2.CAP_PROP_HUE, value)
            elif setting == "sharpness":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_SHARPNESS, self.sharpness)
                else:
                    self.cap.set(cv2.CAP_PROP_SHARPNESS, value)
            elif setting == "white_balance":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_AUTO_WB, 1.0)
                else:
                    self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
                    self.cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, value)
            cv2.waitKey(100)  # Wait for the camera to adjust settings

    def open_cam_adjust_window(self):
        self.adjustment_window = "Camera Adjustments"
        self.get_cam_defaults()
        cv2.namedWindow(self.adjustment_window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.adjustment_window, 640, 50)
        cv2.createTrackbar("Focus", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("focus", x))
        cv2.createTrackbar("Exposure", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("exposure", x))
        cv2.createTrackbar("Brightness", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("brightness", x))
        cv2.createTrackbar("Contrast", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("contrast", x))
        cv2.createTrackbar("Saturation", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("saturation", x))
        cv2.createTrackbar("Gain", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("gain", x))
        cv2.createTrackbar("Hue", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("hue", x))
        cv2.createTrackbar("Sharpness", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("sharpness", x))
        cv2.createTrackbar("White Balance", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("white_balance", x))
        cv2.waitKey(1)  # Brief pause to ensure window is ready

    def close_adjustment_window(self):
        """Close the camera adjustment window."""
        if self.adjustment_window:
            cv2.destroyWindow(self.adjustment_window)
            cv2.waitKey(1)  # Brief pause to ensure window closes
            self.adjustment_window = None

    def destroy(self):
        """Release camera resources and close any open windows."""
        super().destroy()  # This will close the feed window if it's open
        self.close_source()
        self.close_adjustment_window()
