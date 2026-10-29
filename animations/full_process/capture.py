"""
capture.py — run the EXISTING reference interpreter and record what it does.

Nothing here re-implements the interpreter. We import
python_interpreter_in_python/main.py as a module and call its real Lexer,
Parser and Interpreter.  The only thing we add is *observation*:

  tokens(src)          -> the real token stream
  ast_tree(src)        -> the real AST as a plain nested dict
  parse_calls(src)     -> which Parser._method was entered/exited, in order
  parse_failure(src)   -> the real error message + the token it stopped on
  run(src)             -> what the program prints (or the error it reports)
  trace(src)           -> Python-Tutor style steps (frames, objects, stdout)
  scope_table(src)     -> local/global classification (teaching aid, ch. 5)
  dis_text(src)        -> CPython 3.14 bytecode for each function (ch. 9)

slides.py and build_html.py both import this file, so the videos and the
HTML always show the same, real data.
"""

import contextlib
import importlib.util
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAIN_PY = os.path.join(ROOT, "python_interpreter_in_python", "main.py")

_spec = importlib.util.spec_from_file_location("map_main", MAIN_PY)
M = importlib.util.module_from_spec(_spec)
sys.modules["map_main"] = M  # dataclasses need the module registered
_spec.loader.exec_module(M)


def example(name):
    with open(os.path.join(HERE, "examples", name), encoding="utf-8") as fh:
        return fh.read()


PROGRAM_A = example("program_a.py")
PROGRAM_B = example("program_b.py")


# ── Tokens ────────────────────────────────────────────────────────────────────


def tokens(src):
    """[(type_name, value, line, col), ...] straight from M.Lexer."""
    return [(t.type.name, t.value, t.line, t.col) for t in M.Lexer(src).tokenize()]


def token_text(tok):
    """How a token looks in the source (used to size the cursor box)."""
    kind, value, _, _ = tok
    if kind in ("NEWLINE", "INDENT", "DEDENT", "EOF"):
        return ""
    return str(value)


# ── AST ───────────────────────────────────────────────────────────────────────


def _label(node):
    n = type(node).__name__
    if isinstance(node, M.Program):
        return "Program"
    if isinstance(node, M.FuncDef):
        return f"FuncDef {node.name}({', '.join(node.params)})"
    if isinstance(node, M.If):
        return "If"
    if isinstance(node, M.For):
        return f"For {node.target}"
    if isinstance(node, M.Return):
        return "Return"
    if isinstance(node, M.Assign):
        return f"Assign {node.target}"
    if isinstance(node, M.ExprStmt):
        return "ExprStmt"
    if isinstance(node, M.Call):
        return "Call"
    if isinstance(node, M.BinOp):
        return f"BinOp {node.op}"
    if isinstance(node, M.Compare):
        return f"Compare {node.op}"
    if isinstance(node, M.Name):
        return f"Name {node.id}"
    if isinstance(node, M.IntLiteral):
        return f"Int {node.value}"
    if isinstance(node, M.BoolLiteral):
        return f"Bool {node.value}"
    if isinstance(node, M.NoneLiteral):
        return "None"
    return n


def _children(node):
    if isinstance(node, M.Program):
        return list(node.body)
    if isinstance(node, M.FuncDef):
        return list(node.body)
    if isinstance(node, M.If):
        return [node.test] + list(node.body) + list(node.orelse)
    if isinstance(node, M.For):
        return [node.iter] + list(node.body)
    if isinstance(node, M.Return):
        return [node.value] if node.value is not None else []
    if isinstance(node, M.Assign):
        return [node.value]
    if isinstance(node, M.ExprStmt):
        return [node.expr]
    if isinstance(node, M.Call):
        return [node.func] + list(node.args)
    if isinstance(node, (M.BinOp, M.Compare)):
        return [node.left, node.right]
    return []


def _to_dict(node):
    return {
        "label": _label(node),
        "kind": type(node).__name__,
        "line": node.line,
        "children": [_to_dict(c) for c in _children(node)],
    }


def parse(src):
    return M.Parser(M.Lexer(src).tokenize()).parse()


def ast_tree(src):
    return _to_dict(parse(src))


def ast_text(src):
    """Exactly what `main.py --ast` prints."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        M._print_ast(parse(src))
    return buf.getvalue()


# ── Parser call trace (real methods, observed) ────────────────────────────────


def parse_calls(src, entry="_expr"):
    """
    Wrap every Parser._method so we can see the recursive descent.
    Returns [("enter"|"exit", method, token_pos, result_label), ...].
    """
    toks = M.Lexer(src).tokenize()
    events = []

    class Traced(M.Parser):
        pass

    for name, fn in list(vars(M.Parser).items()):
        if not name.startswith("_") or name.startswith("__"):
            continue
        if name in ("_cur", "_peek", "_prev", "_advance", "_check", "_match",
                    "_expect", "_err", "_skip_newlines"):
            continue

        def wrap(fn=fn, name=name):
            def inner(self, *a, **k):
                events.append(("enter", name, self.pos, None))
                res = fn(self, *a, **k)
                lab = _label(res) if isinstance(res, M.ASTNode) else None
                events.append(("exit", name, self.pos, lab))
                return res
            return inner

        setattr(Traced, name, wrap())

    p = Traced(toks)
    getattr(p, entry)() if entry != "parse" else p.parse()
    return events, [(t.type.name, t.value) for t in toks]


def parse_failure(src):
    """Run the real lexer+parser; return (message, line, col) of the failure."""
    toks = None
    try:
        toks = M.Lexer(src).tokenize()
    except M.PyError as e:
        return e.plain(), e.line, None
    p = M.Parser(toks)
    try:
        p.parse()
    except M.PyError as e:
        t = p._cur()
        return e.plain(), t.line, t.col
    return None


# ── Running ───────────────────────────────────────────────────────────────────


def run(src):
    """Same as `python3 main.py file`: stdout, or the plain error line."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            M.run_source(src)
    except M.PyError as e:
        return buf.getvalue() + e.plain() + "\n"
    except Exception as e:  # main.py prints these as InternalError
        return buf.getvalue() + f"InternalError: {e}\n"
    return buf.getvalue()


# ── Python-Tutor style trace ──────────────────────────────────────────────────


def _show(v):
    if isinstance(v, M.PyFunction):
        return {"ref": f"function {v.node.name}({', '.join(v.node.params)})"}
    if isinstance(v, list):
        return {"ref": "list [" + ", ".join(M._ep_str(x) for x in v) + "]"}
    return M._ep_str(v)


def trace(src, max_steps=400):
    """
    One step per executed statement, like pythontutor.com.
    Each step: {line, event, frames:[{name, vars:{k: value|{"ref":..}}}],
                stdout, ret}
    The Interpreter subclass only *watches*; evaluation is main.py's own code.
    """
    steps = []
    out = io.StringIO()
    frames = []  # [(name, Environment)]

    def snapshot(line, event, ret=None, error=None):
        fr = []
        for name, env in frames:
            vs = {}
            for k, v in env.vars.items():
                if callable(v) and not isinstance(v, M.PyFunction):
                    continue  # builtins hidden, as Python Tutor does
                vs[k] = _show(v)
            fr.append({"name": name, "vars": vs})
        steps.append({"line": line, "event": event, "frames": fr,
                      "stdout": out.getvalue(), "ret": ret, "error": error})
        if len(steps) > max_steps:
            raise RuntimeError("trace too long")

    class Tracer(M.Interpreter):
        def _exec(self, node, env):
            snapshot(node.line, "line")
            return super()._exec(node, env)

        def _eval_Call(self, node, env):
            callee = self._eval(node.func, env)
            if not isinstance(callee, M.PyFunction):
                return super()._eval_Call(node, env)
            # Same steps as main.py's _eval_Call, plus frame bookkeeping.
            args = [self._eval(a, env) for a in node.args]
            fn = callee.node
            if len(args) != len(fn.params):
                return super()._eval_Call(node, env)
            call_env = M.Environment(parent=callee.closure)
            for p, v in zip(fn.params, args):
                call_env.set(p, v)
            label = f"{fn.name}({', '.join(M._ep_str(a) for a in args)})"
            frames.append((label, call_env))
            snapshot(fn.line, "call")
            result = None
            try:
                self._exec_stmts(fn.body, call_env)
            except M.ReturnSignal as r:
                result = r.value
            snapshot(steps[-1]["line"], "return", ret=M._ep_str(result))
            frames.pop()
            return result

    interp = Tracer()
    frames.append(("Global frame", interp.globals))
    program = parse(src)
    try:
        with contextlib.redirect_stdout(out):
            interp.run(program)
    except M.PyError as e:
        snapshot(e.line, "exception", error=e.plain())
        return steps
    snapshot(None, "end")
    return steps


# ── Scope table (concept for chapter 5; MAP itself has no semantic pass) ─────


def scope_table(src):
    """
    Python's rule: a name assigned anywhere in a function body is local to
    the whole function. Walks the REAL AST; returns {scope: {name: kind}}.
    """
    prog = parse(src)
    table = {"global": {}}
    for name in M.BUILTINS:
        if name in ("print", "range"):
            table["global"][name] = "builtin"

    def assigned(stmts, acc):
        for s in stmts:
            if isinstance(s, M.Assign):
                acc.add(s.target)
            elif isinstance(s, M.For):
                acc.add(s.target)
                assigned(s.body, acc)
            elif isinstance(s, M.If):
                assigned(s.body, acc)
                assigned(s.orelse, acc)
        return acc

    for s in prog.body:
        if isinstance(s, M.FuncDef):
            table["global"][s.name] = "global (function)"
            scope = {p: "local (parameter)" for p in s.params}
            for n in sorted(assigned(s.body, set()) - set(s.params)):
                scope[n] = "local"
            table[s.name] = scope
        elif isinstance(s, M.Assign):
            table["global"][s.target] = "global"
    return table


# ── CPython bytecode (chapter 9) ──────────────────────────────────────────────


def dis_text(src, func):
    code = (
        "import dis,sys\n"
        "ns={}\nexec(sys.stdin.read(), ns)\n"
        f"dis.dis(ns[{func!r}])\n"
    )
    body = src.split("\nprint(")[0] + "\n"
    r = subprocess.run(["python3.14", "-c", code], input=body,
                       capture_output=True, text=True, check=True)
    return r.stdout


def python314_error(src):
    r = subprocess.run(["python3.14", "-c", src], capture_output=True, text=True)
    return (r.stdout + r.stderr).strip().splitlines()[-1] if r.returncode else r.stdout.strip()


if __name__ == "__main__":
    for t in tokens(PROGRAM_A)[:12]:
        print(t)
    print(ast_text(PROGRAM_A))
    print(run(PROGRAM_A), run(PROGRAM_B))
    print(len(trace(PROGRAM_A)), len(trace(PROGRAM_B)))
    print(scope_table(PROGRAM_B))
    ev, _ = parse_calls("n <= 1\n")
    print(len(ev), ev[:6])
    print(dis_text(PROGRAM_B, "fib_iter"))
