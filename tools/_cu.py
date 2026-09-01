"""Grounded computer-use for the Moyan WeChat DevTools window.

Usage (.ocr-venv python):
  python tools/_cu.py shot                  capture window + OCR -> out/wxide_shot.png + out/wxide_ocr.json
  python tools/_cu.py click <text> [wait]   OCR-locate text, click its center, wait, re-shot
  python tools/_cu.py drag <text> <dy>      drag from text center up/down dy px (picker wheel)
  python tools/_cu.py paste                 Ctrl+V current clipboard into focused control
"""
import ctypes
import ctypes.wintypes as wt
import json
import sys
import time

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
user32.SetProcessDPIAware()

OUT_SHOT = r"D:\Desktop\墨衍-项目\out\wxide_shot.png"
OUT_OCR = r"D:\Desktop\墨衍-项目\out\wxide_ocr.json"


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
        ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
        ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
        ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
    ]


def find_window():
    target = None

    def _cb(hwnd, lparam):
        nonlocal target
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, buf, 256)
            if buf.value == "墨衍":
                target = hwnd
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    if not target:
        print("window not found")
        raise SystemExit(1)
    return target


def capture(hwnd):
    rect = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    hdc_window = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
    gdi32.SelectObject(hdc_mem, hbmp)
    user32.PrintWindow(hwnd, hdc_mem, 2)
    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth, bmi.biHeight, bmi.biPlanes, bmi.biBitCount = w, -h, 1, 32
    bmi.biSizeImage = w * h * 4
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bmi), 0)
    from PIL import Image

    img = Image.frombuffer("RGB", (w, h), buf.raw, "raw", "BGRX", 0, 1)
    return img, (rect.left, rect.top)


def ocr(img):
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR

    arr = np.asarray(img.convert("RGB"))[:, :, ::-1]  # BGR
    engine = RapidOCR()
    result, _ = engine(arr)
    items = []
    if result:
        for box, text, score in result:
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            items.append({
                "text": text,
                "score": round(float(score), 3),
                "cx": int(sum(xs) / 4),
                "cy": int(sum(ys) / 4),
                "x0": int(min(xs)), "y0": int(min(ys)),
                "x1": int(max(xs)), "y1": int(max(ys)),
            })
    return items


def do_shot():
    hwnd = find_window()
    img, (wl, wt_) = capture(hwnd)
    img.save(OUT_SHOT)
    items = ocr(img)
    with open(OUT_OCR, "w", encoding="utf-8") as f:
        json.dump({"window": [wl, wt_], "items": items}, f, ensure_ascii=False, indent=1)
    print(f"shot + ocr: {len(items)} items")


def find_item(needle):
    with open(OUT_OCR, encoding="utf-8") as f:
        items = json.load(f)["items"]
    for it in items:
        if needle in it["text"]:
            return it
    return None


def click_at(sx, sy):
    user32.SetCursorPos(sx, sy)
    time.sleep(0.15)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.08)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def do_click(needle, wait=2.0):
    it = find_item(needle)
    if not it:
        print(f"NOT FOUND: {needle}")
        raise SystemExit(2)
    hwnd = find_window()
    rect = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    sx, sy = rect.left + it["cx"], rect.top + it["cy"]
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.6)
    click_at(sx, sy)
    print(f"clicked [{it['text']}] at screen ({sx},{sy})")
    time.sleep(float(wait))
    do_shot()


def do_drag(needle, dy):
    it = find_item(needle)
    if not it:
        print(f"NOT FOUND: {needle}")
        raise SystemExit(2)
    hwnd = find_window()
    rect = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    sx, sy = rect.left + it["cx"], rect.top + it["cy"]
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.6)
    user32.SetCursorPos(sx, sy)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.15)
    steps = 12
    for i in range(1, steps + 1):
        user32.SetCursorPos(sx, sy + dy * i // steps)
        time.sleep(0.03)
    time.sleep(0.15)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    print(f"dragged [{it['text']}] dy={dy}")
    time.sleep(2.0)
    do_shot()


def do_paste():
    VK_CONTROL, VK_V = 0x11, 0x56
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_V, 0, 2, 0)
    user32.keybd_event(VK_CONTROL, 0, 2, 0)
    print("pasted")


cmd = sys.argv[1]
if cmd == "shot":
    do_shot()
elif cmd == "click":
    do_click(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 2.0)
elif cmd == "drag":
    do_drag(sys.argv[2], int(sys.argv[3]))
elif cmd == "paste":
    do_paste()
else:
    print("unknown cmd")
