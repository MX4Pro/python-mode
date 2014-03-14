""" Code runnning support. """

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sys

from .environment import env
from re import compile as re


encoding = re(r'#[^\w]+coding:\s+utf.*$')


def run_code():
    """ Run python code in current buffer.

    :returns: None

    """

    errors, err = [], ''
    line1, line2 = env.var('a:line1'), env.var('a:line2')
    lines = __prepare_lines(line1, line2)
    for ix in (0, 1):
        if encoding.match(lines[ix]):
            lines.pop(ix)

    context = dict(
        __name__='__main__', input=env.user_input, raw_input=env.user_input)

    sys.stdout, stdout_ = StringIO(), sys.stdout
    sys.stderr, stderr_ = StringIO(), sys.stderr

    try:
        code = compile('\n'.join(lines) + '\n', env.curbuf.name, 'exec')
        exec(code, context) # noqa

    except SystemExit as e:
        if e.code:
            # A non-false code indicates abnormal termination.
            # A false code will be treated as a
            # successful run, and the error will be hidden from Vim
            env.error("Script exited with code %s" % e.code)
            return env.stop()

    except Exception:
        import traceback
        err = traceback.format_exc()

    else:
        err = sys.stderr.getvalue()

    output = sys.stdout.getvalue()
    output = env.prepare_value(output, dumps=False)
    sys.stdout, sys.stderr = stdout_, stderr_

    errors += [er for er in err.splitlines() if er and "<string>" not in er]

    env.let('l:traceback', errors[2:])
    env.let('l:output', [s for s in output.split('\n')])


def __prepare_lines(line1, line2):

    lines = [l.rstrip() for l in env.lines[int(line1) - 1:int(line2)]]

    indent = 0
    for line in lines:
        if line:
            indent = len(line) - len(line.lstrip())
            break

    if len(lines) == 1:
        lines.append('')
    return [l[indent:] for l in lines]
