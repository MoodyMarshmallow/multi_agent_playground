import importlib, sys
_pkg = importlib.import_module('backend.domain.config')
sys.modules[__name__] = _pkg
