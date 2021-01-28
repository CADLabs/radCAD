try:
    from cadCAD.configuration.utils import config_sim
except ImportError:
    _has_cadCAD = False
else:
    _has_cadCAD = True


if not _has_cadCAD:
    raise Exception("Optional compatibility dependency cadCAD not installed")


def config_sim(d):
    # radCAD handles configuration
    return d
