import importlib, sys
_pkg = importlib.import_module('backend.domain.agent')
sys.modules[__name__] = _pkg
