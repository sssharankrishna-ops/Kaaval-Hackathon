"""Test if laptop camera can be accessed."""
import cv2
import platform

print("Testing camera access...")
print(f"Platform: {platform.system()}")

# Try to open camera on Windows
if platform.system() == "Windows":
    print("Using CAP_DSHOW on Windows...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)

print(f"Camera opened: {cap.isOpened()}")

if cap.isOpened():
    print("Camera is accessible!")
    ret, frame = cap.read()
    print(f"Frame read: {ret}")
    if ret:
        print(f"Frame shape: {frame.shape}")
        print(f"Frame dtype: {frame.dtype}")
    cap.release()
    print("Camera test PASSED")
else:
    print("Camera FAILED to open - checking alternative backends...")
    # Try without CAP_DSHOW
    cap = cv2.VideoCapture(0)
    print(f"CAP_V4L2 result: {cap.isOpened()}")
    if cap.isOpened():
        ret, frame = cap.read()
        print(f"Frame read: {ret}")
        cap.release()
