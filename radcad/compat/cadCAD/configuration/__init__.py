try:
    from cadCAD.configuration import Experiment
except ImportError:
    _has_cadCAD = False
else:
    _has_cadCAD = True


if not _has_cadCAD:
    raise Exception("Optional compatibility dependency cadCAD not installed")
