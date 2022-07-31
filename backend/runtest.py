import importlib.util
import sys
import pdb

spec = importlib.util.spec_from_file_location("module.name", "./test.py")
foo = importlib.util.module_from_spec(spec)
sys.modules["module.name"] = foo
pdb.set_trace()
spec.loader.exec_module(foo)


