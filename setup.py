import sys
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need
# fine-tuning.
build_options = {'packages': [],
                 'excludes': [],
                 'include_files': ["ffmpeg.exe", "icon.ico", "Logo.png", "학생 명부.txt"]
                 }

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('BAVoice_GUI.py', base=base, icon="icon.ico")
]

setup(name='BAVoice_GUI',
      version='1.2',
      description="Blue Archive Voice Downloader GUI",
      options={'build_exe': build_options},
      executables=executables)
