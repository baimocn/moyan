import ctypes
import sys
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32.SetClipboardData.restype = ctypes.c_void_p
user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

text = sys.argv[1]
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

ok = False
for i in range(10):
    if user32.OpenClipboard(None):
        ok = True
        break
    time.sleep(0.2)
if not ok:
    print("OpenClipboard failed")
    raise SystemExit(1)

user32.EmptyClipboard()
h = kernel32.GlobalAlloc(GMEM_MOVEABLE, (len(text) + 1) * 2)
p = kernel32.GlobalLock(h)
if not p:
    print("GlobalLock failed")
    raise SystemExit(1)
ctypes.memmove(p, text, (len(text) + 1) * 2)
kernel32.GlobalUnlock(h)
r = user32.SetClipboardData(CF_UNICODETEXT, h)
user32.CloseClipboard()
print("clipboard set, handle:", bool(r))

VK_CONTROL = 0x11
VK_V = 0x56
user32.keybd_event(VK_CONTROL, 0, 0, 0)
time.sleep(0.05)
user32.keybd_event(VK_V, 0, 0, 0)
time.sleep(0.05)
user32.keybd_event(VK_V, 0, 2, 0)
user32.keybd_event(VK_CONTROL, 0, 2, 0)
print("pasted")
