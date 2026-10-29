"""
Copy the code shown in the tutorial out of the six interpreters.

    cd src && python3 scripts/extract_snippets.py

Writes
  core/codesnippets/<prog_lang>/<id>.<ext>   interpreter code, one file per concept
  core/codesnippets/index.json               {id: {prog_lang: "file:first–last"}}
  core/shared/<id>.txt + core/shared/index.json
                                             language-neutral blocks (programs, ASTs,
                                             dis output, error examples, tests) taken
                                             from ../index.html

Every snippet is located by a pattern (function / class / record name), so the
code always matches the interpreters as they are. A concept with no equivalent
in a language is simply left out; the app then shows the Python version.
"""

import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
TUTORIAL = os.path.dirname(SRC)
ROOT = os.path.dirname(TUTORIAL)
CORE = os.path.join(SRC, "core")

FILES = {
    "python": "python_interpreter_in_python/main.py",
    "rust": "python_interpreter_rust/src/main.rs",
    "c++": "python_interpreter_cpp/main.cpp",
    "java": "python_interpreter_java/Main.java",
    "clojure": "python_interpreter_clojure/main.clj",
    "llvm": "python_interpreter_llvm/main.py",
}
EXT = {"python": "py", "rust": "rs", "c++": "cpp", "java": "java", "clojure": "clj", "llvm": "py"}

_cache = {}


def lines_of(lang):
    if lang not in _cache:
        with open(os.path.join(ROOT, FILES[lang]), encoding="utf-8") as fh:
            _cache[lang] = fh.read().split("\n")
    return _cache[lang]


def _is_edge_noise(line):
    t = line.strip()
    return not t or t.startswith(("# ──", "# ══", "# §", ";; ──", ";; ══", ";; §", "// ──", "// ══", "// §"))


def _is_comment(line):
    return line.strip().startswith(("#", ";", "//", "/*", "* ", "*/"))


def _find(lang, pattern, after=0):
    rx = re.compile(pattern)
    for i, l in enumerate(lines_of(lang)[after:], start=after):
        if rx.search(l):
            return i
    raise LookupError(f"{FILES[lang]}: no line matches {pattern!r}")


def _strip_literals(line, lang):
    """Remove strings, char literals and comments so brackets can be counted."""
    if lang == "clojure":
        line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
        line = re.sub(r"\\(newline|space|tab|u[0-9a-fA-F]{4}|.)", "", line)
        return line.split(";", 1)[0]
    line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
    line = re.sub(r"'(\\.|[^'\\])'", "''", line)
    return line.split("//", 1)[0]


def _block_end(lang, start):
    ls = lines_of(lang)
    if lang in ("python", "llvm"):
        ind = len(ls[start]) - len(ls[start].lstrip())
        end = start
        for i in range(start + 1, len(ls)):
            if ls[i].strip() and len(ls[i]) - len(ls[i].lstrip()) <= ind:
                break
            end = i
        return end
    opener, closer = ("(", ")") if lang == "clojure" else ("{", "}")
    depth, opened = 0, False
    for i in range(start, len(ls)):
        s = _strip_literals(ls[i], lang)
        depth += s.count(opener) - s.count(closer)
        opened = opened or opener in s
        if opened and depth <= 0:
            return i
        if not opened and lang != "clojure" and s.rstrip().endswith(";"):
            return i
    raise LookupError(f"{FILES[lang]}:{start + 1}: unbalanced block")


def _with_decorators(lang, start):
    ls = lines_of(lang)
    while start > 0 and ls[start - 1].strip().startswith(("@", "#[")):
        start -= 1
    return start


def block(pattern, after=None):
    """The whole function / class / record whose first line matches pattern."""
    def get(lang):
        a = _find(lang, after) if after else 0
        s = _find(lang, pattern, a)
        return _with_decorators(lang, s), _block_end(lang, s)
    return get


def span(start_pat, end_pat, after=None):
    """From the line matching start_pat up to (not including) the line matching end_pat."""
    def get(lang):
        a = _find(lang, after) if after else 0
        s = _find(lang, start_pat, a)
        e = _find(lang, end_pat, s + 1) - 1
        ls = lines_of(lang)
        while e > s and (_is_edge_noise(ls[e]) or _is_comment(ls[e]) or ls[e].strip().startswith(("@", "#["))):
            e -= 1
        return _with_decorators(lang, s), e
    return get


def lines(a, b):
    return lambda lang: (a - 1, b - 1)


# id -> {lang: [part, ...]}; parts are joined with a blank line.
# Python ranges are the ones the tutorial has always quoted.
SNIPPETS = {
    "lexer.loop": {
        "python": [lines(190, 197)],
        "rust": [block(r"pub fn tokenize\(")],
        "c++": [block(r"std::vector<Token> tokenize\(\)")],
        "java": [block(r"List<Token> tokenize\(\)")],
        "clojure": [block(r"^\(defn tokenize!")],
        "llvm": [block(r"def tokenize\(self\)")],
    },
    "lexer.dispatch": {
        "python": [lines(234, 269)],
        "rust": [block(r"fn next_token\(")],
        "c++": [block(r"void nextToken\(\)")],
        "java": [block(r"private void nextToken\(\)")],
        "clojure": [block(r"^\(defn- next-token!")],
        "llvm": [block(r"def _next_token\(self\)")],
    },
    "lexer.token": {
        "python": [lines(137, 147)],
        "rust": [block(r"^pub struct Token \{")],
        "c++": [block(r"^struct TokenValue \{"), block(r"^struct Token \{")],
        "java": [block(r"record Token\(TT type")],
        "clojure": [block(r"^\(defrecord Token ")],
        "llvm": [block(r"^class Token:")],
    },
    "lexer.indent": {
        "python": [lines(271, 302)],
        "rust": [block(r"fn handle_indentation\(")],
        "c++": [block(r"void handleIndentation\(\)")],
        "java": [block(r"private void handleIndentation\(\)")],
        "clojure": [block(r"^\(defn- handle-indentation!")],
        "llvm": [block(r"def _handle_indentation\(self\)")],
    },
    "parser.stmt": {
        "python": [lines(752, 788)],
        "rust": [block(r"fn stmt\(&mut self\)"), block(r"fn simple_stmt\(&mut self\)")],
        "c++": [block(r"ASTPtr stmt\(\) \{"), block(r"ASTPtr simpleStmt\(\) \{")],
        "java": [block(r"private Node stmt\(\) \{"), block(r"private Node simpleStmt\(\) \{")],
        "clojure": [block(r"^\(defn- p-stmt \["), block(r"^\(defn- p-simple-stmt ")],
        "llvm": [block(r"def _stmt\(self\)"), block(r"def _simple_stmt\(self\)")],
    },
    "parser.comparison": {
        "python": [lines(898, 914)],
        "rust": [block(r"fn comparison\(&mut self\)"), block(r"fn sum\(&mut self\)")],
        "c++": [block(r"ASTPtr comparison\(\) \{"), block(r"ASTPtr sum\(\) \{")],
        "java": [block(r"private Node comparison\(\) \{"), block(r"private Node sum\(\) \{")],
        "clojure": [block(r"^\(def \^:private compare-ops"), block(r"^\(defn- p-comparison "),
                    block(r"^\(defn- p-sum ")],
        "llvm": [block(r"def _comparison\(self\)"), block(r"def _sum\(self\)")],
    },
    "parser.error": {
        "python": [lines(718, 728)],
        "rust": [block(r"fn expect\(&mut self, tag"), block(r"fn err<T>\(&self", after=r"^pub struct Parser")],
        "c++": [block(r"const Token& expect\(TT tt"), block(r"void err\(const std::string& msg\)", after=r"^class Parser")],
        "java": [block(r"private Token expect\(TT tt, String msg\)"), block(r"private ParseError err\(")],
        "clojure": [block(r"^\(defn- p-err! "), block(r"^\(defn- p-expect!")],
        "llvm": [block(r"def _expect\(self, tt"), block(r"def _err\(self, msg", after=r"^class Parser")],
    },
    "ast.base": {
        "python": [lines(506, 520)],
        "rust": [block(r"^pub struct Program \{")],
        "c++": [block(r"^enum class NodeType \{"), block(r"^struct ASTNode \{")],
        "java": [span(r"sealed interface Node \{", r"// Literals")],
        "clojure": [block(r"^\(defrecord Program ")],
        "llvm": [span(r"^class ASTNode", r"^class IntLiteral")],
    },
    "ast.expr": {
        "python": [lines(565, 595)],
        "rust": [block(r"^pub enum Expr \{")],
        "java": [span(r"// Expressions", r"// Statements", after=r"sealed interface Node")],
        "clojure": [span(r"^\(defrecord IntLiteral ", r"^\(defrecord Assign ")],
        "llvm": [span(r"^class BinOp", r"^class MethodCall")],
    },
    "ast.stmt": {
        "python": [lines(605, 651)],
        "rust": [block(r"^pub enum Stmt \{")],
        "java": [span(r"// Statements", r"// ═", after=r"sealed interface Node")],
        "clojure": [span(r"^\(defrecord Assign ", r"^\(defrecord FuncDef "), block(r"^\(defrecord FuncDef ")],
        "llvm": [span(r"^class Assign", r"^# ═")],
    },
    "eval.dispatch": {
        "python": [lines(1307, 1318)],
        "rust": [span(r"fn exec_stmts\(", r"Stmt::Assign \{")],
        "c++": [span(r"void execStmts\(", r"case NodeType::Assign:")],
        "java": [span(r"private void execStmts\(", r"case AugAssign n")],
        "clojure": [span(r"^\(defmulti exec-node", r"^\(defn apply-binop")],
        "llvm": [block(r"def stmts\(self, ss\)"), block(r"def ex\(self, n\)")],
    },
    "env.get": {
        "python": [lines(1018, 1057)],
        "rust": [block(r"^pub struct Env \{"), block(r"^impl Env \{")],
        "c++": [block(r"^class Environment : ")],
        "java": [block(r"static final class Environment \{")],
        "clojure": [span(r"^\(defrecord Env ", r"^\(defrecord PyFunction ")],
        "llvm": [block(r"^def _scan\("), block(r"def var_ptr\("), block(r"def load_checked\(")],
    },
    "eval.call": {
        "python": [lines(1588, 1615)],
        "rust": [block(r"fn eval_call\(&self")],
        "c++": [block(r"case NodeType::Call: \{")],
        "java": [block(r"private Object evalCall\(Call n")],
        "clojure": [block(r"^\(defmethod eval-node Call ")],
        "llvm": [block(r"def ex_Call\(self, n\)")],
    },
    "eval.return_signal": {
        "python": [lines(43, 48)],
        "rust": [block(r"^pub enum Flow \{"), block(r"^impl From<PyError> for Flow")],
        "c++": [block(r"^struct ReturnException \{")],
        "java": [block(r"static final class ReturnSignal ")],
        "clojure": [block(r"^\(defn return-signal$"), block(r"^\(defn return-signal\? ")],
        "llvm": [block(r"def emit_return\(self, val\)"), block(r"def st_Return\(self, n\)")],
    },
    "eval.control": {
        "python": [lines(1336, 1360)],
        "rust": [span(r"Stmt::Return \{ value", r"^        \}$", after=r"fn exec\(&self, node: &Stmt")],
        "c++": [span(r"case NodeType::Return: \{", r"default:", after=r"void exec\(const ASTPtr")],
        "java": [span(r"case Return n ->", r"default ->", after=r"private void exec\(Node node")],
        "clojure": [span(r"^\(defmethod exec-node Return ", r";; ── Expression evaluation")],
        "llvm": [block(r"def st_If\(self, n\)"), block(r"def _for_range\(self, n\)")],
    },
    "errors.classes": {
        "python": [lines(13, 41)],
        "rust": [block(r"^pub enum PyError \{"), block(r"^impl PyError \{")],
        "c++": [span(r"^class EduPyError ", r"^struct ReturnSignal")],
        "java": [span(r"static class PyError extends", r"static final class ReturnSignal")],
        "clojure": [span(r"^\(defn- format-error ", r"^\(defn return-signal$")],
        "llvm": [span(r"^class PyError", r"^# ═")],
    },
    "errors.main": {
        "python": [lines(1879, 1889)],
        "rust": [block(r"^fn main\(\)")],
        "c++": [block(r"^int main\(")],
        "java": [block(r"static int realMain\(")],
        "clojure": [block(r"^\(defn- report-exception "), block(r"^\(defn -main ")],
        "llvm": [block(r"^def main\(\)")],
    },
    "builtins.print": {
        "python": [lines(1076, 1079)],
        "rust": [block(r"^fn builtin_print\(")],
        "c++": [block(r"^static Value builtin_print\(")],
        "java": [block(r'reg\("print", a -> \{')],
        "clojure": [block(r"^\(defn builtin-print ")],
        "llvm": [block(r"^def _builtin_print\(")],
    },
    "builtins.range": {
        "python": [lines(1090, 1098)],
        "rust": [block(r"^fn builtin_range\(")],
        "c++": [block(r"^static Value builtin_range\(")],
        "java": [block(r'reg\("range", a -> \{')],
        "clojure": [block(r"^\(defn builtin-range ")],
        "llvm": [block(r"^def _builtin_range\(")],
    },
    "builtins.registry": {
        "python": [lines(1209, 1224)],
        "rust": [block(r"^pub const NAMES: "), block(r"^pub fn call\(name: &str")],
        "c++": [block(r"^static const std::vector<std::pair<std::string, Value::BuiltinFn>> BUILTINS")],
        "java": [span(r"static final Map<String, Builtin> BUILTINS", r"static void need\(")],
        "clojure": [block(r"^\(def builtins$")],
        "llvm": [span(r"^BUILTINS = \{", r"^OPS = ")],
    },
    "builtins.seed": {
        "python": [lines(1284, 1287)],
        "rust": [block(r"pub fn new\(\) -> Self", after=r"^impl Interpreter")],
        "c++": [block(r"^    Interpreter\(\) \{")],
        "java": [block(r"^        Interpreter\(\) \{")],
        "clojure": [block(r"^\(defn new-interpreter ")],
        "llvm": [block(r"def _rt_call_builtin\(self")],
    },
}


def build_snippets():
    out = os.path.join(CORE, "codesnippets")
    for d in os.listdir(out):
        p = os.path.join(out, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    index = {}
    for sid, per_lang in SNIPPETS.items():
        index[sid] = {}
        for lang, parts in per_lang.items():
            ls = lines_of(lang)
            chunks, refs = [], []
            for part in parts:
                a, b = part(lang)
                while b > a and _is_edge_noise(ls[b]):
                    b -= 1
                chunks.append("\n".join(ls[a:b + 1]))
                refs.append(f"{a + 1}–{b + 1}")
            os.makedirs(os.path.join(out, lang), exist_ok=True)
            with open(os.path.join(out, lang, f"{sid}.{EXT[lang]}"), "w", encoding="utf-8") as fh:
                fh.write("\n\n".join(chunks) + "\n")
            index[sid][lang] = f"{FILES[lang]}:{', '.join(refs)}"
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, ensure_ascii=False)
    return index


# ---------- language-neutral blocks, copied from the static tutorial ----------

TITLES = {
    "Program A — fib_rec(4)": "program_a",
    "Program B — fib_iter(6)": "program_b",
    "ordered choice by hand (the technique from peg.txt)": "ordered_choice",
    "packrat in a few lines": "packrat",
    "Program A": "ast_a",
    "Program B": "ast_b",
    "MAP output": "rt_name_error_deep_out",
    "CPython 3.14, last line of the traceback": "cpython_traceback",
    "fib_rec — python3.14 -m dis": "dis_fib_rec",
    "fib_iter — python3.14 -m dis": "dis_fib_iter",
}


def build_shared():
    with open(os.path.join(TUTORIAL, "index.html"), encoding="utf-8") as fh:
        page = fh.read()
    out = os.path.join(CORE, "shared")
    os.makedirs(out, exist_ok=True)
    index = {}
    fig = re.compile(r"<figure class='code'><figcaption>(.*?)</figcaption><pre class='([^']+)'>(.*?)</pre></figure>", re.S)
    for cap, cls, body in fig.findall(page):
        title = re.search(r"<span class='ctitle'>(.*?)</span>", cap)
        ref = re.search(r"<span class='ref'>(.*?)</span>", cap)
        title = html.unescape(title.group(1)) if title else ""
        ref = html.unescape(ref.group(1)) if ref else ""
        if title.startswith("examples/errors/"):
            sid = "err_" + title.rsplit("/", 1)[1][:-3]
        elif title.startswith("MAP grammar"):
            sid = "grammar"
        elif title in TITLES:
            sid = TITLES[title]
        else:
            continue
        hl = {"lang-python": "python", "out": "plaintext", "lang-text": "plaintext"}[cls]
        with open(os.path.join(out, sid + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(html.unescape(body))
        index[sid] = {"hl": hl, "out": cls == "out", "ref": ref}
        if sid.startswith(("program_", "err_")):
            index[sid]["runnable"] = True  # the Run button executes it
    tokens = re.search(r"<summary>Show all \d+ tokens</summary>(<div class='tablewrap'>.*?</div>)</details>", page, re.S)
    with open(os.path.join(out, "tokens_a.html"), "w", encoding="utf-8") as fh:
        fh.write(tokens.group(1))
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, ensure_ascii=False)
    return index


if __name__ == "__main__":
    idx = build_snippets()
    langs = list(FILES)
    print(f"{'snippet':<20}" + "".join(f"{l:>9}" for l in langs))
    for sid, per in idx.items():
        print(f"{sid:<20}" + "".join(f"{'✓' if l in per else '·':>9}" for l in langs))
    print(f"shared blocks: {len(build_shared())}")
