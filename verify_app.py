#!/usr/bin/env python3
"""
YaRead — Test & Verification Suite
Validates application files, audio assets, icons, syntax, and Linux environment.
"""

import os
import sys
import py_compile

def check(title, condition, details=""):
    status = "✓ PASS" if condition else "✗ FAIL"
    msg = f"  [{status}] {title}"
    if details:
        msg += f": {details}"
    print(msg)
    return condition

def main():
    print("================================================================")
    print(" 📚 YaRead Verification Suite")
    print("================================================================")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_ok = True

    # 1. Python version
    py_ver = sys.version_info
    all_ok &= check(
        "Python Version",
        py_ver >= (3, 10),
        f"{py_ver.major}.{py_ver.minor}.{py_ver.micro} (Requires >= 3.10)"
    )

    # 2. Syntax / Bytecode compilation
    main_py = os.path.join(script_dir, "yaread.py")
    try:
        py_compile.compile(main_py, doraise=True)
        compiled_ok = True
        err = ""
    except Exception as e:
        compiled_ok = False
        err = str(e)
    all_ok &= check("yaread.py Bytecode Compilation", compiled_ok, err)

    # 3. Essential Assets
    assets_to_check = [
        "assets/icon.png",
        "icon.ico",
        "qr.png",
        "assets/demo.gif",
        "LICENSE",
        "README.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "requirements.txt",
        "build_release.sh",
        "run.sh",
        "install.sh",
        "uninstall.sh"
    ]
    for rel in assets_to_check:
        full_path = os.path.join(script_dir, rel)
        exists = os.path.isfile(full_path)
        all_ok &= check(f"File exists: {rel}", exists)

    # 4. Music Soundtracks (1.mp3 to 12.mp3)
    music_dir = os.path.join(script_dir, "music")
    music_ok = os.path.isdir(music_dir)
    missing_tracks = []
    if music_ok:
        for i in range(1, 13):
            track_path = os.path.join(music_dir, f"{i}.mp3")
            if not os.path.isfile(track_path) or os.path.getsize(track_path) == 0:
                missing_tracks.append(f"{i}.mp3")
    music_all_present = music_ok and len(missing_tracks) == 0
    all_ok &= check(
        "Soundtracks (12 Emotional Loops)",
        music_all_present,
        f"Missing: {missing_tracks}" if missing_tracks else "12/12 present"
    )

    # 5. Check dependencies report (informative)
    print("\n--- Python Modules Status ---")
    mods = {
        "PyQt6": "GUI framework (python3-pyqt6)",
        "pygame": "Sound engine (python3-pygame)",
        "fitz": "PDF engine / PyMuPDF (python3-fitz)",
        "bs4": "BeautifulSoup4 HTML/EPUB parser (python3-bs4)",
        "lxml": "FB2 XML parser (python3-lxml)",
        "ebooklib": "EPUB reader (python3-ebooklib)",
        "llama_cpp": "Local offline LLM (optional)"
    }
    for mod, desc in mods.items():
        try:
            __import__(mod)
            print(f"  [FOUND]     {mod:12} : {desc}")
        except ImportError:
            print(f"  [NOT FOUND] {mod:12} : {desc}")

    print("================================================================")
    if all_ok:
        print(" 🎉 All checks passed successfully!")
        return 0
    else:
        print(" ⚠️  Some checks failed. Please see above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
