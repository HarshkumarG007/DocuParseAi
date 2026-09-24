import sys
import platform
import subprocess
import os

def check_python():
    print("=== Python Check ===")
    print(f"Version: {sys.version.split()[0]} ({platform.architecture()[0]})")
    if sys.version_info < (3, 9):
        print("[WARN] Warning: Python 3.9+ is recommended.")
    else:
        print("[OK] Python version is supported.")
    print()

def check_gpu():
    print("=== GPU & CUDA Check ===")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"[OK] CUDA is available. GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("[WARN] CUDA not available. Application will run on CPU fallback.")
    except ImportError:
        print("[ERROR] PyTorch not installed yet (Wait for 'pip install' to complete).")
    print()

def check_tesseract():
    print("=== Tesseract OCR Check ===")
    tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")
    try:
        result = subprocess.run([tesseract_cmd, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[OK] Tesseract found: {version_line}")
        else:
            print("[ERROR] Tesseract found but failed to run properly.")
    except FileNotFoundError:
        print(f"[ERROR] Tesseract OCR not found in PATH.\n   Please install it (e.g. via Windows installer) and add it to your PATH, or set TESSERACT_CMD in .env.")
    print()

if __name__ == "__main__":
    print("Running DocuParse AI Diagnostics...\n")
    check_python()
    check_gpu()
    check_tesseract()
    print("Diagnostics complete.")
