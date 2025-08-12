import importlib, sys
_pkg = importlib.import_module('backend.domain.text_adventure_games')
sys.modules[__name__] = _pkg
