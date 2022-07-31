from pdb import Pdb
import io 
import os
from multiprocessing.process import AuthenticationString

class PdbExt(Pdb):
    def __init__(self, stdin, stdout):
        PdbExt.instance = self
        super().__init__(stdin=stdin, stdout=stdout)

    def my_get_curframe_locals(self):
        res = self.curframe_locals
        return res


    def runscript(self, filename):
        import __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
                                  "__file__"    : filename,
                                  "__builtins__": __builtins__,
                                 })

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = False
        with io.open_code(filename) as fp:
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)