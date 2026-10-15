# Thread caps and numba's threading layer, before anything imports numpy or
# numba (planet/parallel.py says why; set the variables yourself to override).
from . import parallel as _parallel

_parallel.set_default_threads()
THREADING_LAYER = _parallel.pin_threading_layer()
