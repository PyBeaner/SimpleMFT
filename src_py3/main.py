__author__ = 'PyBeaner'

import subprocess

command = 'python -c "import mft_grabber;mft_grabber.save_mft_by_drive("G")"'
subprocess.call(["runas", "/user:PyBeaner", command], shell=True)
