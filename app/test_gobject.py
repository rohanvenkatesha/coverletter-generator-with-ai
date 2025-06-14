import ctypes
import os

gtk_bin_path = r'C:\Program Files\GTK3-Runtime Win64\bin'  # Change this to your actual path

dll_path = os.path.join(gtk_bin_path, 'gobject-2.0-0.dll')

try:
    gobject = ctypes.CDLL(dll_path)
    print("Loaded libgobject-2.0-0.dll successfully!")
except Exception as e:
    print(f"Failed to load DLL: {e}")
