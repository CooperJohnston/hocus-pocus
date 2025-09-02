### focuspocus

## Gaze Tracker
A Python-based gaze tracking tool that uses computer vision to estimate where a user is looking on the screen. Built with OpenCV and MediaPipe FaceMesh, this tracker can be integrated into interactive applications such as focus measurement systems, learning companions, or screenmate assistants.
Features
Real-time eye and gaze detection using MediaPipe FaceMesh.
Polynomial regression and homography mapping to calibrate gaze to screen coordinates.
Support for custom calibration routines (e.g., maze or race track paths).
Optional mouse tracking integration (via pynput) to combine gaze and cursor behavior.
CSV logging of gaze and focus-related data for later analysis.
## Requirements
 - Python 3.8+
 - OpenCV
 - MediaPipe
 - NumPy
 - pynput (for mouse input, optional)
 - scikit-learn (for regression models)
