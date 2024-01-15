# HEVA_Portal
VMC protocol implementation for Blender for VTubers. Supports animation and sound recording. Works with both [HEVA](https://github.com/scaledteam/HEVA) and [VSeeFace](https://www.vseeface.icu/). Also supports animation creating and sound recording + synchronization of both.

[RUS] Дополнительную информацию на русском языке можно найти на стриме: https://www.youtube.com/watch?v=4X-1wE6MlDc

# Usage
1. Start program like VSeeFace or HEVA
2. Enable VMC sender and set ip to 127.0.0.1 and port 9000
3. Start blender and open HEVA_Portal.blend
4. Launch HEVA_Portal.py script inside Blender (already included in HEVA_Portal.blend)
5. Enjoy

Use F1 key to toggle recording, ESC for exiting program.

# Some setup info
- Default port for this program is 9000.
- Dependencies can be installed as .zip Blender addon.

Dependencies:
- [pythonosc](https://pypi.org/project/python-osc/)
- [PyAudio](https://pypi.org/project/PyAudio/)
