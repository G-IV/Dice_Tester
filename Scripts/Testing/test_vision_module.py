'''
Testing for vision module.
'''
import cv2
import pytest
from Scripts.Modules import vision
from pathlib import Path

IMAGE = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/1_Images/roll_1_20260125_133620_frame0000.jpg')
VIDEO = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/2_Video/roll_1_20260125_133620.mp4')
MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/3_Model/best.pt')

class TestFeedInitialization:
    def test_feed_invalid_type_raises_typeerror(self):
        """Test that TypeError is raised when an incorrect FeedType is used."""
        with pytest.raises(TypeError):
            vision.Feed(invalid_feed_type="not_a_feedtype")

    def test_feed_none_feedtype_raises_valueerror(self):
        """Test that ValueError is raised when FeedType is None."""
        with pytest.raises(TypeError):
            vision.Feed(feed_type=None)

    def test_feed_type_camera(self):
        """Test that Feed initializes correctly with valid FeedType."""
        # Replace with actual valid FeedType from your vision module
        feed = vision.Feed(feed_type=vision.Feed.FeedType.CAMERA)
        assert isinstance(feed, vision.Feed)

    def test_cam_feed_with_neg_index_raises_valueerror(self):
        """Test that ValueError is raised when an invalid camera index is used."""
        with pytest.raises(ValueError):
            vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=-1)

    def test_cam_feed_with_filepath_raises_valueerror(self):
        """Test that ValueError is raised when an invalid camera index is used."""
        with pytest.raises(ValueError):
            vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=IMAGE)

    def test_image_feed_with_invalid_filepath_raises_file_not_found_error(self):
        """Test that FileNotFoundError is raised when an invalid image path is used."""
        with pytest.raises(FileNotFoundError):
            vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=Path('invalid_path.jpg'))

    def test_video_feed_with_invalid_filepath_raises_file_not_found_error(self):
        """Test that FileNotFoundError is raised when an invalid video path is used."""
        with pytest.raises(FileNotFoundError):
            vision.Feed(feed_type=vision.Feed.FeedType.VIDEO, source=Path('invalid_path.mp4'))
    
    def test_image_feed_with_invalid_filetype_raises_valueerror(self):
        """Test that ValueError is raised when a non-image file is used for image feed."""
        with pytest.raises(ValueError):
            vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=Path('invalid_path.mp3'))
    
    def test_image_feed_with_empty_filetype_raises_valueerror(self):
        """Test that ValueError is raised when a non-image file is used for image feed."""
        with pytest.raises(ValueError):
            vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=Path(''))

    def test_image_feed_with_valid_filepath(self):
        """Test that Feed initializes correctly with a valid image path."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=IMAGE)
        assert isinstance(feed, vision.Feed)

    def test_video_feed_with_valid_filepath(self):
        """Test that Feed initializes correctly with a valid video path."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.VIDEO, source=VIDEO)
        assert isinstance(feed, vision.Feed)

    def test__open_source_camera_fails_with_bad_id(self):
        """Test that open_source works correctly for CAMERA feed type."""
        with pytest.raises(ValueError):
            feed = vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=9999)
    
    def test_open_source_image_succeeds_with_valid_id(self):
        """Test that open_source works correctly for IMAGE feed type."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=0)
        cap = feed.open_source()
        assert cap.isOpened()
        cap.release()

    def test_open_source_video_succeeds_with_valid_path(self):
        """Test that open_source works correctly for VIDEO feed type."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.VIDEO, source=VIDEO)
        cap = feed.open_source()
        assert cap.isOpened()
        cap.release()

    def test_open_window_creates_window_video(self):
        """Test that open_window creates a window."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=0)
        window_name = feed.open_window()
        assert window_name == 'Die Tester - Camera Feed'
        cv2.destroyWindow(window_name)

    def test_open_window_creates_window_image(self):
        """Test that open_window creates a window."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=IMAGE)
        window_name = feed.open_window()
        assert window_name == 'Die Tester - Camera Feed'
        cv2.destroyWindow(window_name) 
    
    def test_close_source_releases_cap(self):
        """Test that close_source releases the video capture."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.VIDEO, source=VIDEO)
        feed.close_source()
        assert feed.cap is None

    def test_frame_grab_from_camera(self):
        """Test that a frame can be grabbed from the camera feed."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=0)
        ret, frame = feed.cap.read()
        assert ret is True
        assert frame is not None
        feed.close_source()

    def test_frame_grab_from_image(self):
        """Test that a frame can be grabbed from the image feed."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=IMAGE)
        ret, frame = feed.cap.read()
        assert ret is True
        assert frame is not None
        feed.close_source()

    def test_frame_grab_from_video(self):
        """Test that a frame can be grabbed from the video feed."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.VIDEO, source=VIDEO)
        ret, frame = feed.cap.read()
        assert ret is True
        assert frame is not None
        feed.close_source()

    def test_second_frame_grab_from_image_fails(self):
        """Test that a second frame grab from an image feed fails."""
        feed = vision.Feed(feed_type=vision.Feed.FeedType.IMG, source=IMAGE)
        ret1, frame1 = feed.cap.read()
        ret2, frame2 = feed.cap.read()
        assert ret1 is True
        assert frame1 is not None
        assert ret2 is False
        assert frame2 is None
        feed.close_source()

    def test_empty_string_model_path_raises_valueerror(self):
        """Test that ValueError is raised when an empty model path is provided."""
        with pytest.raises(ValueError):
            vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=0, model_path='')

    def test_none_model_path_raises_valueerror(self):
        """Test that ValueError is raised when an empty model path is provided."""
        with pytest.raises(ValueError):
            vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=0)

    def test_bad_model_path_raises_filepatherror(self):
        """Test that ValueError is raised when an empty model path is provided."""
        with pytest.raises(FileNotFoundError):
            vision.Feed(feed_type=vision.Feed.FeedType.CAMERA, source=0, model_path='invalid/path')
