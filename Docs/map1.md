# Build Your Own Python: A Minimal Interpreter From Scratch

*A hands-on, incremental guide to writing a tiny Python interpreter — tokenizer, parser, AST, and tree-walking evaluator — in your favorite Language and Programing language, explained for people who have never built one before via Graphic helpers.*

---

## Table of Contents

1. [Introduction: Why and How Build an Interpreter?](#1-introduction-why-build-an-interpreter)
2. [The REPL: Read, Eval, Print, Loop](#2-the-repl-read-eval-print-loop)
3. [The Tokenizer (Lexer): Turning Text Into LEGO Bricks](#3-the-tokenizer-lexer-turning-text-into-lego-bricks)
4. [The PEG Parser: Teaching the Computer Grammar](#4-the-peg-parser-teaching-the-computer-grammar)
5. [The Parse Tree: The Grammar, Drawn as a Shape](#5-the-parse-tree-the-grammar-drawn-as-a-shape)
6. [The AST: Keeping Only What Matters](#6-the-ast-abstract-syntax-tree-keeping-only-what-matters)
7. [The Interpreter: Walking the Tree](#7-the-interpreter-walking-the-tree)
8. [Built-in Functions: Cheating, Legally](#8-built-in-functions-cheating-legally)
9. [Error Handling: Failing Politely](#9-error-handling-failing-politely)
10. [Data Structures Under the Hood](#10-data-structures-under-the-hood)
11. [Where Python's Standard Library Begins](#11-where-pythons-standard-library-begins)
12. [Talking to the Operating System](#12-talking-to-the-operating-system)
13. [Growing the Interpreter: What's Next?](#13-growing-the-interpreter-whats-next)
14. [Wrap-Up](#14-wrap-up)

> **A note on translation and format.** Every chapter in this article is designed to stand on its own: one idea in, one idea mastered, one door opened to the next room. That makes it easy to turn into a video, a workshop, or a translated version in another human language — and even to re-implement in Rust, C++, Java, or Go, while keeping the same mental model. The code shown here is Python, but the *ideas* are language-agnostic.

---

## 1. Introduction: Why Build an Interpreter?

The short answer: 

    because building an interpreter teaches you how Python and Programing languages actually works.

You'll learn how Python tokenizes source code, builds an Abstract Syntax Tree (AST), manages variables and scopes, and executes code. More importantly, you'll become a better programmer by understanding the language beyond its syntax.

There is a common saying among systems programmers:

        You're not a real programmer until you've built a programming language and an operating system.

It's an exaggeration, but it highlights an important idea. Building an interpreter **earns the respect** of other programmers because it demonstrates a deep understanding of computer science fundamentals. It also gives you more freedom: instead of depending entirely on existing libraries and tools, you'll have the knowledge to build your own when needed.

### What is an interpreter, really?

At the most basic level, an **interpreter** is a program that reads another program — written as plain text — and *does what it says*. That's it. You give it:

```python
print(2 + 2)
```

and it prints `4`. Somewhere between the text you typed and the number on your screen, a whole pipeline of small, understandable steps happened. This article is about building that pipeline, piece by piece, so none of it feels like magic anymore.

If you want the more formal definition, the [Wikipedia article on interpreters](https://en.wikipedia.org/wiki/Interpreter_(computing)) is a good reference — but don't worry about vocabulary yet. We'll introduce every term exactly when you need it, never before.

### What is the Diference between compiler and interpreter?

In short:

    Interpreter: Translate while running it.
    Compiler: Translate everything first, then run the finished code.


| Interpreter                                                           | Compiler                                                                         |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Translates and executes code **line by line** while the program runs. | Translates the **entire program** into machine code before it runs.              |
| Starts quickly but performs translation during execution.             | Takes time to compile first, but the resulting program usually runs much faster. |
| Reports errors as they are encountered.                               | Reports compilation errors before the program starts.                            |


(Animation here)

Think about a speech being delivered in a foreign language.

An interpreter listens to the speaker and translates each sentence in real time as the audience hears it. The translation happens while the speech is being given.
A compiler works differently. Before the event, it translates the entire speech into another language and writes it on paper. During the presentation, a second person simply reads the already translated speech to the audience. No translation happens during the event.

### Why Python?

The short answer: 

    Because i love it and you also, who dont love python?
    And Python have a big community

Python is a fantastic language to study for this project because:

- Its syntax is famously readable — that same readability makes it easier to *parse* by hand.
- It uses **indentation** to define blocks of code (instead of curly braces `{ }`), which forces us to confront a genuinely interesting problem: how do you turn *whitespace* into structure? We'll tackle that head-on in Chapter 3.
- It's a language most readers already know how to *use*, which means you can focus all your energy on understanding how it *works*, instead of learning a new syntax on top of a new concept.

### What we're actually building

We are not going to build all of Python. Real Python — technically called **CPython**, the reference implementation — is a project with hundreds of thousands of lines of C and Python code, supporting classes, generators, async/await, a massive standard library, and a sophisticated bytecode compiler. That's not the goal here.

Instead, we're building a **minimal subset**: variables, arithmetic, strings, lists, `if`/`elif`/`else`, `while` and `for` loops, function definitions with `return`, and a small set of built-in functions like `print` and `len`. It's a real, working, runnable interpreter — just a small one. Think of it as a single-room cabin instead of a skyscraper: it has walls, a roof, a door, and it keeps the rain out. It's just not 80 stories tall.

By the end of this article, our tiny interpreter will be able to run this exact program, which we'll use as a running example throughout every chapter:

```python
def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

print(fibonacci_recursive(5))

def fibonacci_iterative(n):
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b

print(fibonacci_iterative(5))
```

Two ways of computing the same [Fibonacci number](https://en.wikipedia.org/wiki/Fibonacci_sequence) — one recursive, one iterative — using functions, conditionals, arithmetic, and a loop. If our interpreter can correctly run this by the end of the article, we've succeeded. (One small honest note: our minimal grammar doesn't support the multi-assignment shorthand `a, b = 0, 1` directly — we'll flag that explicitly in Chapter 6 as a great "grow the interpreter yourself" exercise, because the reason it's excluded is exactly the kind of grammar tradeoff this whole article is about.)

### The pipeline

Every interpreter — CPython included — is built around the same basic pipeline:

```
   source code (text)
          |
          v
   +-------------+
   |    LEXER    |   text  ->  tokens
   +-------------+
          |
          v
   +-------------+
   |   PARSER    |   tokens ->  tree
   +-------------+
          |
          v
   +-------------+
   | INTERPRETER |   tree  ->  behavior
   +-------------+
          |
          v
      output / effects
```

(animation here, with a example in each step)
example ,

    for i in range(3):
        print(i)

and it will replace 
by 

    print(1)
    print(2)
    print(3)
Each box is a chapter (or several) in this article. Each one takes something messy and turns it into something more structured, until eventually the structure is clean enough that "running" the program just means walking through it and doing what it says.

By the time we're done, you'll have written:

- A **lexer** (or "tokenizer") that turns raw text into a stream of meaningful chunks.
- A **parser** that turns that stream into a tree representing the program's structure.
- An **interpreter** that walks the tree and actually executes it.
- A handful of **built-in functions**, some **error handling**, and a simple **REPL** to play with it all interactively.

Let's start at the very end of that pipeline conceptually, but the very *beginning* practically: a program that just talks back to you.

**Exercises before moving on:**
1. Open a Python shell (type `python3` in your terminal) and try typing `2 + 2`, then `print("hi")`, then a syntax error like `if True`. Notice how Python responds differently to each.
2. Without looking anything up, write down — in plain English — what you *think* happens between you pressing Enter and Python printing a result. We'll compare this to reality as we go.

**Coming up next:** we build the smallest possible version of an interactive Python-like shell: one that reads a line, echoes it back, and loops forever. From there, we'll slowly teach it to actually *understand* what it reads.

---

## 2. The REPL: Read, Eval, Print, Loop

### Motivation

Before we write a single line of parsing logic, we need somewhere to type things and see results. That "somewhere" is the same interface Python itself gives you when you type `python3` with no arguments: a prompt that reads what you type, does something with it, prints the result, and waits for the next line. This pattern is called a **REPL** — short for **R**ead, **E**val, **P**rint, **L**oop. You can read more about the general concept on [Wikipedia's REPL page](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop).

### The problem

We want an interactive environment we can grow *alongside* the interpreter. If we build the whole lexer-parser-interpreter pipeline first and only bolt on a REPL at the end, we lose the ability to test each new feature the moment we build it. So instead, we build the REPL shell *first*, even though at the start it won't understand any real Python at all.

### The analogy

Think of a REPL like a very literal parrot with a growing vocabulary. On day one, the parrot only knows how to repeat exactly what you say back to you:

```
you:    hello
parrot: hello
```

That's it. No understanding, just an echo. But every week, you teach the parrot a new word or rule, and slowly its "repeat" turns into "respond." Eventually, when you say "what's 2 plus 2," it doesn't repeat your sentence — it actually answers `4`. Our REPL starts exactly like the day-one parrot.

### Theory: the four steps

| Step | What it does | Analogy |
|---|---|---|
| **Read** | Grab a line of text from the user | The parrot listens |
| **Eval** | Process/evaluate that text into a result | The parrot "thinks" |
| **Print** | Show the result back to the user | The parrot speaks |
| **Loop** | Go back to step 1 forever | The parrot never stops listening |

Here's the same idea as a diagram:

```
        +---------------------------------+
        |                                 |
        v                                 |
   +---------+   +------+   +-------+     |
   |  READ   |-->| EVAL |-->| PRINT |-----+
   +---------+   +------+   +-------+
   (get input)   (do work)  (show output)
```

### Implementation: Version 0 — the echo shell

Here is the smallest possible REPL. It reads a line, prints it back unchanged, and loops until you type `exit`:

```python
def repl_v0():
    print("Echo REPL. Type 'exit' to quit.")
    while True:
        line = input(">>> ")
        if line.strip() == "exit":
            print("Bye!")
            break
        print(line)  # "Eval" is just "return the same text" for now

repl_v0()
```

Running it looks like this:

```
Echo REPL. Type 'exit' to quit.
>>> hello
hello
>>> this is not python yet
this is not python yet
>>> exit
Bye!
```

Notice: there's no understanding happening at all. `line` is just a Python string, and we print it straight back. But the *shape* of the program — an infinite loop with a read step, a processing step, and a print step — is already exactly the shape our real interpreter's REPL will have.

### Implementation: Version 1 — evaluating numbers

Let's make our "Eval" step slightly smarter. Instead of echoing text, let's actually try to interpret it as a number and do something with it:

```python
def repl_v1():
    print("Number REPL. Type 'exit' to quit.")
    while True:
        line = input(">>> ")
        if line.strip() == "exit":
            print("Bye!")
            break
        try:
            value = float(line)
            if value.is_integer():
                value = int(value)
            print(value)
        except ValueError:
            print(f"I don't understand {line!r} yet.")

repl_v1()
```

```
Number REPL. Type 'exit' to quit.
>>> 42
42
>>> 3.14
3.14
>>> hello
I don't understand 'hello' yet.
>>> exit
Bye!
```

This is a real turning point, even though it looks tiny: our "Eval" step now makes a *decision* based on the shape of the input. That decision-making is the seed of everything that follows. Right now we can only recognize "is this a number," but by the end of Chapter 3 we'll be able to recognize numbers, names, operators, strings, and keywords — and by the end of Chapter 4, we'll understand full expressions like `fibonacci_recursive(5) + 1`.

Here's the real interpreter's actual REPL, taken from our finished project, so you can see where we're headed. It's the same Read-Eval-Print-Loop shape, just with a real lexer, parser, and interpreter doing the "Eval" work instead of `float()`:

```python
def repl():
    interp = Interpreter()
    buf = []
    prompt = ">>> "
    while True:
        line = input(prompt if not buf else "... ")
        if not buf and line.strip() == "exit":
            break
        buf.append(line)
        source = "\n".join(buf)
        if line.rstrip().endswith(":"):
            continue  # keep reading -- the block isn't finished yet
        try:
            run_source(source + "\n", interp)
        except (LexerError, ParseError, PyRuntimeError) as e:
            print(e)
        finally:
            buf = []
```

Don't worry about understanding every line yet — notice just one thing: the overall shape (`while True`, read a line, try to run it, print any errors, loop) is identical to our two toy versions above. We've only made "Eval" (here, `run_source`) more powerful. That's the whole philosophy of this article: **grow the middle, keep the shape.**

### Example: tracing it through

If you type `2 + 2` into our *final* REPL, here's what happens at a high level (each of these steps is a full chapter later in this article):

```
"2 + 2"                          <- Read: raw text from input()
   |
   v   Lexer (Chapter 3)
[INTEGER(2), PLUS, INTEGER(2)]   <- a stream of tokens
   |
   v   Parser (Chapter 4-6)
BinOp(left=2, op='+', right=2)   <- a tree describing "2 plus 2"
   |
   v   Interpreter (Chapter 7)
4                                <- Eval: the actual computed result
   |
   v
"4"                              <- Print
```

### Exercises

1. Modify `repl_v1()` so that it also understands basic addition, like `2 + 2` (hint: you can cheat for now with `line.split("+")` — we'll replace this hack with a real lexer in the next chapter, which is exactly why it's worth feeling the hack's limitations first).
2. What happens in your modified REPL if someone types `2 + `? What *should* happen? Keep this question in your back pocket for Chapter 9 (Error Handling).
3. Try to break your REPL with unusual input: empty lines, only spaces, `exit` with a trailing space. Decide what "should" happen in each case.

### Preview of the next chapter

Our REPL currently only understands "is this whole line a number." Real programs are made of many small meaningful pieces — numbers, names, symbols, keywords — mixed together on one line, like `fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)`. Before we can understand *sentences* like that, we need to learn to break them into *words*. That's the job of the **lexer**, and it's next.

---

## 3. The Tokenizer (Lexer): Turning Text Into LEGO Bricks

### Motivation

Right now, our interpreter sees source code the same way you'd see a sentence written with no spaces: `defefibonaccirecursivenreturn...`. Well — not quite that bad, since we do have spaces, but the computer still just sees one giant string of characters. Before we can understand *structure* (which is what parsing is about), we need to break that string into meaningful chunks. That's the job of the **lexer**, short for "lexical analyzer" — sometimes also called a **tokenizer**.

### The problem

Consider this single line from our running example:

```python
return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)
```

To a computer, before any processing, this is just 64 individual characters sitting in a row: `r`, `e`, `t`, `u`, `r`, `n`, ` `, `f`, `i`, `b`, ... and so on. There's no built-in concept of "this is the word `return`" or "this is a minus sign used for subtraction." We have to build that concept ourselves.

### The analogy

Picture a sentence written in a language you don't speak, with every letter squished together and no spaces::

```
thecatsatonthemat
```

Your brain automatically tries to break this into words: "the," "cat," "sat," "on," "the," "mat." That mental step — turning a stream of letters into a stream of *words* — is exactly what a lexer does to source code. Except instead of English words, our "words" are things like numbers, variable names, symbols, and keywords.

Another way to think about it: raw source code is like a sentence made of *sand* — a continuous, undifferentiated substance. Tokenizing turns that sand into **LEGO bricks**: discrete, labeled pieces you can count, inspect, and later snap together into bigger structures. A parser (next chapter) can't work with sand. It needs bricks.

### Theory: what counts as a token?

A **token** is the smallest meaningful unit of source code. Our lexer needs to recognize several categories, mirroring the categories in [CPython's own tokenizer](https://docs.python.org/3/library/tokenize.html):

| Category | Examples | Token type |
|---|---|---|
| Numbers | `5`, `3.14` | `INTEGER`, `FLOAT` |
| Strings | `"hello"` | `STRING` |
| Identifiers (names) | `n`, `fibonacci_recursive` | `NAME` |
| Keywords | `if`, `return`, `def`, `for`, `while` | `IF`, `RETURN`, `DEF`, ... |
| Operators | `+`, `-`, `==`, `<=` | `PLUS`, `MINUS`, `EQEQUAL`, ... |
| Delimiters | `(`, `)`, `:`, `,` | `LPAREN`, `RPAREN`, `COLON`, ... |
| Structure | end of line, indent, dedent | `NEWLINE`, `INDENT`, `DEDENT` |

That last row is the tricky one, and it's the thing that makes Python's lexer more interesting than, say, a lexer for a curly-brace language like JavaScript. We'll get there in a moment.

Each token, in our implementation, is represented as a small data structure carrying its type, its actual value, and its position in the source (useful later for error messages):

```python
@dataclass
class Token:
    type: TT       # what kind of token (NAME, PLUS, INTEGER, ...)
    value: Any     # the actual data (e.g. "fibonacci_recursive", 5, "+")
    line: int      # which line it came from
    col: int       # which column it starts at
```

### Tokenizing our running example, step by step

Let's tokenize just the first line of our Fibonacci program:

```python
def fibonacci_recursive(n):
```

Character by character, our lexer groups things into tokens:

```
def fibonacci_recursive ( n ) :
 │        │              │ │ │ │
 ▼        ▼              ▼ ▼ ▼ ▼
DEF   NAME("fibonacci_recursive")  LPAREN  NAME("n")  RPAREN  COLON
```

As a token stream, that's:

```
[DEF, NAME('fibonacci_recursive'), LPAREN, NAME('n'), RPAREN, COLON, NEWLINE, INDENT]
```

Notice two tokens at the end that don't correspond to any visible character: `NEWLINE` and `INDENT`. `NEWLINE` marks the end of a logical line (so the parser knows a statement is complete). `INDENT` is Python-specific — it marks that the next line is *more indented* than the current one, meaning a new block (like the body of the function) has begun.

### The tricky part: indentation as tokens

In a language like JavaScript or C, blocks are delimited by explicit characters:

```c
if (x > 0) {
    do_something();
}
```

The `{` and `}` tell the parser exactly where a block starts and ends — whitespace is irrelevant, purely cosmetic. Python has no such characters. Instead, it uses the *amount of leading whitespace* on a line to mean the same thing. This is elegant for humans to read, but it means our lexer has to do extra work: it must **measure indentation** and turn *changes* in indentation into synthetic `INDENT` and `DEDENT` tokens.

Here's the core idea, using a stack (we'll properly introduce stacks in Chapter 10, but the intuition is simple: a stack is a pile of plates — you can only add or remove from the top):

```
indent_stack = [0]      # we start at indentation level 0

for each new logical line:
    measure how many spaces begin the line -> `indent`

    if indent > indent_stack[-1]:
        push indent onto the stack
        emit an INDENT token          # we just went "deeper"

    elif indent < indent_stack[-1]:
        while indent_stack[-1] > indent:
            pop the stack
            emit a DEDENT token        # we just came back "out"
```

Here's that logic as it actually appears in our lexer:

```python
def _handle_indentation(self):
    indent = 0
    while self._cur() in (" ", "\t"):
        indent = (indent // 8 + 1) * 8 if self._cur() == "\t" else indent + 1
        self._advance()

    current = self.indent_stack[-1]

    if indent > current:
        self.indent_stack.append(indent)
        self.tokens.append(Token(TT.INDENT, indent, self.line, 1))
    elif indent < current:
        while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent:
            self.indent_stack.pop()
            self.tokens.append(Token(TT.DEDENT, indent, self.line, 1))
        if self.indent_stack[-1] != indent:
            self._err("IndentationError: unindent does not match any outer indentation level")
```

Let's trace this against a small chunk of our Fibonacci program:

```python
def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)
```

| Line | Leading spaces | Stack before | Action | Stack after |
|---|---|---|---|---|
| `def fibonacci_recursive(n):` | 0 | `[0]` | (no change) | `[0]` |
| `    if n <= 1:` | 4 | `[0]` | `4 > 0` → push, emit `INDENT` | `[0, 4]` |
| `        return n` | 8 | `[0, 4]` | `8 > 4` → push, emit `INDENT` | `[0, 4, 8]` |
| `    return fibonacci_recursive(...)` | 4 | `[0, 4, 8]` | `4 < 8` → pop, emit `DEDENT` | `[0, 4]` |

By the time the lexer finishes, every block boundary in the *entire source file* has been converted into explicit `INDENT`/`DEDENT` tokens — meaning the parser (next chapter) never has to think about whitespace at all. It just sees a clean, flat stream of tokens, some of which happen to be named `INDENT` and `DEDENT`. This is a great example of a general engineering principle: **push complexity to the earliest stage that can handle it, so every later stage gets to stay simple.**

### Recognizing operators: the "maximal munch" rule

One more subtlety: when the lexer sees `<`, is that the `LESS` token, or is it the first half of `<=`? The standard approach (used by virtually every real-world lexer) is called **maximal munch**: always consume the *longest* valid token starting at the current position. So when we see `<`, we peek at the *next* character before deciding:

```python
elif ch == "<":
    if self._cur() == "=":
        self._advance()
        self.tokens.append(Token(TT.LESSEQUAL, "<=", ln, cl))
    else:
        self.tokens.append(Token(TT.LESS, "<", ln, cl))
```

The same pattern handles `==` vs `=`, `**` vs `*`, `//` vs `/`, and so on — always look one character ahead before committing to a token.

### Keywords vs. names: one more decision point

How does the lexer know that `if` is a keyword but `interesting_variable` is just a name, even though both start with letters? The trick is refreshingly simple: **read the whole word first, then check if it's in a lookup table of reserved words.**

```python
KEYWORDS = {
    "if": TT.IF, "elif": TT.ELIF, "else": TT.ELSE,
    "while": TT.WHILE, "for": TT.FOR, "in": TT.IN,
    "def": TT.DEF, "return": TT.RETURN,
    "and": TT.AND, "or": TT.OR, "not": TT.NOT,
    "True": TT.TRUE, "False": TT.FALSE, "None": TT.NONE,
}

def _read_name(self):
    buf = []
    while self._cur().isalnum() or self._cur() == "_":
        buf.append(self._advance())
    name = "".join(buf)
    self.tokens.append(Token(KEYWORDS.get(name, TT.NAME), name, ln, cl))
```

If the word we just read (`name`) is a key in `KEYWORDS`, we tag it with its special token type (`IF`, `RETURN`, etc). Otherwise, it falls back to the generic `NAME` token — meaning "this is a variable or function name, I don't yet know which."

### Full token stream for our running example

Here's the complete token stream (types only, values omitted for brevity) for the line `if n <= 1:` followed by `return n`:

```
IF  NAME  LESSEQUAL  INTEGER  COLON  NEWLINE  INDENT  RETURN  NAME  NEWLINE  DEDENT
```

Read it out loud and it almost narrates itself: "if, name, less-or-equal, integer, colon, newline — indent — return, name, newline — dedent." That's the entire shape of a two-line `if` block, with no ambiguity left for the next stage to resolve.

### Exercises

1. By hand, write out the full token stream for `print(fibonacci_recursive(5))`. How many tokens are there? Which ones are `NAME`, and how does the lexer tell they aren't keywords?
2. What should happen if the lexer sees an unrecognized character, like `@` or `$`? Look at `_read_operator`'s final `else` branch in the full source code at the end of this article, and describe in your own words what error it raises.
3. **Challenge:** our lexer treats `\t` (tab) as jumping to the next multiple of 8 columns, matching a common convention. What issue could arise if one function mixes tabs and spaces for indentation? (This is a real, notorious Python gotcha — CPython actually raises a `TabError` for exactly this reason.)

### Preview of the next chapter

We now have a flat list of tokens — LEGO bricks, sorted and labeled. But a *pile* of labeled bricks isn't a castle. The next step is figuring out the *rules* for how tokens are allowed to combine into valid statements and expressions — and that means learning about **grammars** and **parsing**.

---

## 4. The PEG Parser: Teaching the Computer Grammar

### Motivation

We now have tokens — but tokens alone don't tell us *how* they fit together. `NAME EQUAL INTEGER` could be an assignment (`x = 5`). `NAME LPAREN NAME RPAREN` could be a function call (`f(x)`). The lexer doesn't know the difference; it just labels bricks. Someone has to define the *rules* for how bricks combine into valid structures — and that someone is the **parser**.

### The problem

Given the token stream for `n - 1`:

```
[NAME('n'), MINUS, INTEGER(1)]
```

we want to recognize: "this is a subtraction expression, with `n` on the left and `1` on the right." Given `fibonacci_recursive(n - 1)`, we want to recognize: "this is a function call, whose single argument is that subtraction expression." The rules that let us recognize these shapes are called a **grammar**, and the process of applying a grammar to a token stream is called **parsing**.

### The analogy

Think about how you were taught grammar in school: a sentence is built from a subject, a verb, and an object; a noun phrase can contain an adjective plus a noun; and so on. You didn't memorize every possible sentence in English — you learned a small set of *rules* that let you both understand and produce an infinite number of new sentences you'd never heard before.

A programming language grammar works the same way. We define a small number of rules like "an expression is a term, optionally followed by `+` or `-` and another term," and from those few rules, an infinite variety of valid programs can be recognized (or, if you're writing a compiler, generated).

### Theory: PEG vs. other approaches

There are many styles of formal grammar (if you want the deep end, see [context-free grammars](https://en.wikipedia.org/wiki/Context-free_grammar) on Wikipedia). Since Python 3.9, CPython itself uses a style called a **PEG parser** — "Parsing Expression Grammar." You can read the original announcement and rationale in [PEP 617](https://peps.python.org/pep-0617/).

The key idea behind a PEG, and the reason it's approachable for a first-time parser author, is this:

> **At every decision point, try each alternative rule in order, and commit to the first one that matches.**

This is sometimes summarized as "ordered choice." Unlike some more academic grammar formalisms, a PEG never has to consider multiple interpretations of the same input at once — it always greedily picks the first rule that works and moves on. That determinism makes it dramatically easier to implement by hand, using a technique called **recursive descent**: one function per grammar rule, where each function calls the next one down the chain, and functions may call themselves (hence "recursive"). If "recursion" itself feels shaky, [this friendly explainer](https://en.wikipedia.org/wiki/Recursion_(computer_science)) is worth a detour — but the short version is: a function that solves a big problem by calling itself on a slightly smaller version of the same problem.

### Building the grammar, layer by layer

Here's the core insight that makes arithmetic parsing work correctly: **grammar rules are layered by precedence.** `*` binds tighter than `+`, so `2 + 3 * 4` must parse as `2 + (3 * 4)`, not `(2 + 3) * 4`. We achieve this not with special-casing, but by literally writing one grammar rule *per precedence level*, each one calling into the next tighter level:

```
expr        := or_expr
or_expr     := and_expr  ('or'  and_expr)*
and_expr    := not_expr  ('and' not_expr)*
not_expr    := 'not' not_expr | comparison
comparison  := sum (comp_op sum)*
sum         := term  (('+' | '-') term)*
term        := factor (('*' | '/' | '//' | '%') factor)*
factor      := ('+' | '-') factor | power
power       := primary ['**' factor]
primary     := atom (call | subscript | method_call)*
atom        := INTEGER | FLOAT | STRING | NAME | ... | '(' expr ')'
```

Read from top to bottom, each rule is "looser-binding" than the one below it. `or` binds the loosest (evaluated last), and things like numbers and parentheses (`atom`) bind the tightest (evaluated first). This ladder, sometimes called a **precedence climbing** or "precedence cascade" structure, is one of the most reused patterns in all of parser-writing — nearly every hand-written recursive-descent parser for an arithmetic-containing language uses exactly this shape.

Here's the same ladder as a picture, showing how deeply nested each level is by the time we reach a single number:

```
expr
 └─ or_expr
     └─ and_expr
         └─ not_expr
             └─ comparison
                 └─ sum
                     └─ term
                         └─ factor
                             └─ power
                                 └─ primary
                                     └─ atom  →  INTEGER(5)
```

To parse *any* single number like `5`, control has to pass down through every rung of this ladder — and back up again. That might sound wasteful, but it's exactly what guarantees the precedence comes out correct, automatically, with no special-casing anywhere.

### Implementation: recursive descent in practice

Each grammar rule above becomes one Python method. Here's `sum`, which handles `+` and `-`:

```python
def _sum(self) -> ASTNode:
    node = self._term()                       # parse the left side first
    while self._check(TT.PLUS, TT.MINUS):     # then look for + or -
        op = self._advance().value
        right = self._term()                  # parse the right side
        node = BinOp(left=node, op=op, right=right, line=node.line)
    return node
```

Notice the shape: **parse one thing, then loop, looking for an operator followed by another thing of the same kind.** This `while` loop is what makes `1 + 2 + 3 + 4` parse correctly without needing four separate grammar rules — it just keeps folding the running result (`node`) into a bigger and bigger tree as it finds more `+`/`-` tokens.

`term` (handling `*`, `/`, `//`, `%`) is *structurally identical*, just one level down and with different operators:

```python
def _term(self) -> ASTNode:
    node = self._factor()
    while self._check(TT.STAR, TT.SLASH, TT.DOUBLESLASH, TT.PERCENT):
        op = self._advance().value
        right = self._factor()
        node = BinOp(left=node, op=op, right=right, line=node.line)
    return node
```

This is the whole trick. Once you've written one precedence level, the rest is mostly copy-paste with different token types and a different "next level down" call.

### Tracing our running example: `n - 1`

Let's trace `_sum()` on the tokens `[NAME('n'), MINUS, INTEGER(1)]`:

1. `_sum()` calls `_term()`, which calls `_factor()`, which calls `_power()`, which calls `_primary()`, which calls `_atom()`.
2. `_atom()` sees `NAME('n')`, consumes it, and returns a `Name(id='n')` node. This bubbles all the way back up to `_sum()`, unchanged, since no `*`, `**`, or call/subscript tokens follow it.
3. Back in `_sum()`, `node` is now `Name(id='n')`. We check: is the next token `PLUS` or `MINUS`? Yes — it's `MINUS`.
4. We consume `MINUS`, then call `_term()` again to parse the right-hand side, which recurses all the way down and comes back with `IntLiteral(value=1)`.
5. We wrap both sides: `node = BinOp(left=Name('n'), op='-', right=IntLiteral(1))`.
6. No more `+`/`-` tokens remain, so `_sum()` returns this `BinOp` node.

### Where does a function call fit in?

Function calls, subscripting (`list[0]`), and method calls (`"hi".upper()`) all live in `_primary()`, the level just above `atom`:

```python
def _primary(self) -> ASTNode:
    node = self._atom()
    while True:
        if self._check(TT.LPAREN):
            self._advance()
            args = self._call_args()
            self._expect(TT.RPAREN, "expected ')' after arguments")
            node = Call(func=node, args=args, line=...)
        elif self._check(TT.LBRACKET):
            ...  # subscript, e.g. lst[0]
        elif self._check(TT.DOT):
            ...  # method call, e.g. "hi".upper()
        else:
            break
    return node
```

This `while True` loop is what lets you chain calls and subscripts arbitrarily: `f(x)(y)[0].upper()` all falls out of the same loop, re-checking after each piece whether *another* `(`, `[`, or `.` follows. Applied to `fibonacci_recursive(n - 1)`, `_atom()` first returns `Name(id='fibonacci_recursive')`, and then the `while` loop in `_primary()` notices the following `(`, parses the argument list (which internally calls all the way back up to `_expr()` to parse `n - 1`), and wraps everything into a `Call` node.

### Exercises

1. Why does `power` (handling `**`) sit *between* `factor` and `primary`, rather than at the very bottom next to `atom`? Hint: think about what `-2 ** 2` should evaluate to in real Python (it's `-4`, not `4` — try it!), and trace how our grammar produces that.
2. Draw the same "ladder" diagram as above, but trace `2 + 3 * 4` down and back up. At which rule does the multiplication get grouped *before* the addition sees it?
3. `not_expr` is defined as `'not' not_expr | comparison` — notice it calls *itself* for the first alternative. Why is that necessary? (Hint: what should `not not True` mean?)

### Preview of the next chapter

We've just spent this whole chapter describing *rules*. Applying those rules to actual tokens produces a *result* — a tree-shaped structure representing exactly how the tokens nested inside one another. That raw, rule-shaped tree is called a **parse tree**, and it's the direct, literal output of the grammar we just wrote. It turns out we don't actually want to keep all of it around — but understanding what it looks like first will make it much clearer why we throw parts of it away.

---

## 5. The Parse Tree: The Grammar, Drawn as a Shape

### Motivation

In the last chapter, we wrote grammar rules and traced how they process tokens. Every time a grammar rule matches something, it conceptually creates a "node" representing that match, and nodes that were built out of other nodes naturally nest inside each other. If you drew *every single rule invocation* as a box, and drew a line from each box to the boxes it called, you'd get a tree. That tree is called a **parse tree** (sometimes a "concrete syntax tree" or CST).

### The problem

A parse tree, taken completely literally, includes *everything* — every rule that was invoked, even the ones that didn't really "do" anything except pass a value through unchanged. That's useful for understanding the grammar, but it's needlessly bulky for actually running the program. This chapter's job is just to *see* that bulkiness clearly, so the next chapter's cleanup makes obvious sense.

### The analogy

Think of a parse tree like a rough transcript of a phone call, including every "um," every false start, every "so anyway." It's completely faithful to what was said, but nobody wants to *read* it that way — you'd want the cleaned-up meeting notes instead. The parse tree is the rough transcript. The AST (next chapter) is the meeting notes.

### Drawing it out

Let's parse the tiny expression `n - 1` using the *full, literal* rule ladder from Chapter 4, and draw every single rule invocation as a tree node — even the ones that just pass their child through unchanged:

```
sum
 └─ term
     └─ factor
         └─ power
             └─ primary
                 └─ atom
                     └─ NAME('n')
     '-'
 └─ term
     └─ factor
         └─ power
             └─ primary
                 └─ atom
                     └─ INTEGER(1)
```

Notice: almost the entire left half of this tree (`term → factor → power → primary → atom`) exists purely because our grammar has five precedence levels, and *none of them did anything* except confirm "yep, nothing interesting happening at this level, pass it down." Only two things in this entire tree actually matter: **"subtract"** and its two operands, **`n`** and **`1`**.

### Why we don't execute the parse tree directly

If our interpreter had to walk a tree shaped exactly like the one above, it would need to know, and correctly skip over, five layers of "pass-through" nodes for every single number or name in the program. Every rule name (`sum`, `term`, `factor`, `power`, `primary`) would need its own handling code in the interpreter, even though 90% of them do nothing but forward a value. That's a lot of ceremony for zero payoff.

Formally, a parse tree captures the *derivation* — literally, the sequence of grammar rules applied — rather than the *meaning*. For a course-style deep dive on this distinction, see [Crafting Interpreters' chapter on representing code](https://craftinginterpreters.com/representing-code.html), which covers the same parse-tree-vs-AST tradeoff in more formal detail than we will here.

### The fix, previewed

The good news is our recursive-descent parser from Chapter 4 *already avoids building this bloated tree in the first place* — if you look back at `_sum()` and `_term()`, notice they don't return a "sum-node" and a "term-node" stacked on top of each other. When there's no `+`/`-` at a given level, the function just returns whatever its child returned, with no wrapping at all:

```python
def _sum(self) -> ASTNode:
    node = self._term()
    while self._check(TT.PLUS, TT.MINUS):
        ...
        node = BinOp(left=node, op=op, right=right, line=node.line)
    return node   # <-- if the while loop never ran, we return term's result AS-IS
```

In other words: our parser produces the *lean* tree directly, skipping the bulky intermediate representation entirely. This is a common and practical shortcut taken by many hand-written parsers — we build the **AST** straight away, and only ever *talk about* the fuller parse tree as a mental model for understanding precedence. It's a bit like knowing the "rough transcript" exists in theory, while the parser is smart enough to hand you cleaned-up notes from the very first draft.

### Example, side by side

Here's the "full literal" parse tree next to the actual leaner tree our parser really builds for `n - 1`:

```
   PARSE TREE (all rules shown)          WHAT OUR PARSER ACTUALLY BUILDS

   sum                                          BinOp('-')
    ├─ term                                       ├─ Name('n')
    │   └─ ... → NAME('n')                        └─ IntLiteral(1)
    ├─ '-'
    └─ term
        └─ ... → INTEGER(1)
```

Same information, radically less clutter. That right-hand tree — the one with only the meaningful nodes — is called the **Abstract Syntax Tree**, and it's the actual subject of the next chapter.

### Exercises

1. Draw the full, literal parse tree (with every precedence rule shown, like the `n - 1` example above) for the expression `2 * 3`. How many "pass-through" layers appear before you reach the multiplication?
2. Why do you think it's called a "concrete" syntax tree, in contrast to an "abstract" one? What do you think "concrete" is referring to?
3. Look at `_power()` from Chapter 4. Under what condition does it *not* simply pass its child through unchanged?

### Preview of the next chapter

Now that we can see exactly what "extra" a full parse tree carries, let's define precisely what we keep, what we drop, and what a clean, minimal tree — the AST — looks like for every kind of statement and expression in our language.

---

## 6. The AST (Abstract Syntax Tree): Keeping Only What Matters

### Motivation

We ended the last chapter with a promise: a tree that keeps only the meaningful structure of a program, and throws away every "pass-through" layer that existed solely because of grammar precedence. That tree is called an **Abstract Syntax Tree**, or **AST** — "abstract" precisely because it discards the concrete grammar mechanics and keeps only the *meaning*. If you want a reference definition, [Wikipedia's AST article](https://en.wikipedia.org/wiki/Abstract_syntax_tree) is a solid one, and if you're curious how CPython itself defines its AST node types, they're listed (using a small description language called ASDL) in [Grammar/Python.asdl](https://docs.python.org/3/library/ast.html).

### The problem

We need concrete, working data structures — one per *kind* of meaningful thing in our language — that our interpreter can later walk through and execute. Not "sum-rule-result" or "term-rule-result," but things like "this is a subtraction," "this is a function call," "this is an if-statement."

### The analogy

If a parse tree is a rough phone transcript, the AST is the meeting notes a good assistant hands you afterward: "Alice proposed X. Bob disagreed, suggesting Y instead. Decision: proceed with X." All the hesitations, restarts, and filler are gone — only the *decisions and facts* remain, organized by what actually happened, not by the order sentences were spoken.

### Theory: one node type per concept

Every AST node in our interpreter is a small Python `dataclass` (a compact way to define a class that mostly just holds data — see the [dataclasses docs](https://docs.python.org/3/library/dataclasses.html) if that's new to you). Here are the core ones, each with a plain-English description and a tiny example:

| Node | Meaning | Example source | Fields |
|---|---|---|---|
| `IntLiteral` / `FloatLiteral` | A literal number | `5`, `3.14` | `value` |
| `StringLiteral` | A literal string | `"hi"` | `value` |
| `Name` | A reference to a variable | `n` | `id` |
| `BinOp` | A binary arithmetic operation | `n - 1` | `left`, `op`, `right` |
| `UnaryOp` | A unary operation | `-n`, `not x` | `op`, `operand` |
| `Compare` | A comparison | `n <= 1` | `left`, `op`, `right` |
| `BoolOp` | Boolean `and`/`or` | `x and y` | `op`, `values` |
| `Call` | A function call | `fibonacci_recursive(n)` | `func`, `args` |
| `MethodCall` | A method call | `"hi".upper()` | `obj`, `method`, `args` |
| `ListLiteral` | A list literal | `[1, 2, 3]` | `elts` |
| `Subscript` | Indexing | `lst[0]` | `value`, `index` |
| `Assign` | Variable assignment | `x = 5` | `target`, `value` |
| `AugAssign` | Augmented assignment | `x += 1` | `target`, `op`, `value` |
| `Return` | A return statement | `return n` | `value` |
| `If` | Conditional branching | `if n <= 1: ...` | `test`, `body`, `orelse` |
| `While` | A while loop | `while x > 0: ...` | `test`, `body` |
| `For` | A for loop | `for i in range(5): ...` | `target`, `iter`, `body` |
| `FuncDef` | A function definition | `def f(n): ...` | `name`, `params`, `body` |
| `Program` | The whole file | *(the entire source)* | `body` |

Here's what a couple of these actually look like as Python dataclasses:

```python
@dataclass
class BinOp(ASTNode):
    left: ASTNode = None
    op: str = ""
    right: ASTNode = None

@dataclass
class If(ASTNode):
    test: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)
    orelse: List[ASTNode] = field(default_factory=list)

@dataclass
class FuncDef(ASTNode):
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
```

Notice the pattern: **each node stores exactly the information needed to understand or execute that construct, and nothing more.** A `BinOp` doesn't care which grammar rule produced it — it just knows it has a left side, an operator, and a right side. An `If` doesn't remember the word "if" or the colon that followed its condition — it just remembers the test expression and the two possible bodies to run.

### The full AST for our running example

Let's build the complete AST for the `fibonacci_recursive` function:

```python
def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)
```

Drawn as an ASCII tree:

```
FuncDef(name='fibonacci_recursive', params=['n'])
 └─ body:
     ├─ If
     │   ├─ test:  Compare(op='<=')
     │   │           ├─ left:  Name('n')
     │   │           └─ right: IntLiteral(1)
     │   └─ body:
     │       └─ Return
     │           └─ value: Name('n')
     │
     └─ Return
         └─ value: BinOp(op='+')
                     ├─ left:  Call
                     │           ├─ func: Name('fibonacci_recursive')
                     │           └─ args: [ BinOp(op='-')
                     │                        ├─ left:  Name('n')
                     │                        └─ right: IntLiteral(1) ]
                     └─ right: Call
                                 ├─ func: Name('fibonacci_recursive')
                                 └─ args: [ BinOp(op='-')
                                              ├─ left:  Name('n')
                                              └─ right: IntLiteral(2) ]
```

Take a second to really look at this. Every single piece of the original source code is represented *exactly once*, in exactly the shape needed to execute it — no colons, no keywords, no parentheses, no precedence-ladder scaffolding. This is the tree our interpreter (next chapter) will actually walk.

### Where this comes from in the parser

Each parser method from Chapter 4 directly constructs one of these node types the moment it finishes recognizing a pattern. For example, here's the actual `_if_stmt` method:

```python
def _if_stmt(self) -> If:
    ln = self._prev().line
    test = self._expr()
    self._expect(TT.COLON, "expected ':' after if-condition")
    body = self._block()
    orelse = self._elif_or_else()
    return If(test=test, body=body, orelse=orelse, line=ln)
```

Notice it doesn't build any intermediate "if-statement-rule" node — it goes straight to constructing the final `If` dataclass with exactly the three fields the interpreter will need later: `test`, `body`, `orelse`. The parser and the AST are designed together, hand in glove.

### A grammar tradeoff, made honest

Earlier, in the introduction, we noted that our grammar doesn't support Python's multiple-assignment shorthand:

```python
a, b = 0, 1          # not supported by our minimal grammar
a, b = b, a + b       # not supported either
```

Here's *why*, in AST terms: our `Assign` node has a single string field, `target: str`, and a single `value: ASTNode` field. Real Python's assignment AST node supports a *list* of targets and allows the right-hand side to itself be a tuple. Supporting `a, b = b, a + b` properly would mean introducing a new expression kind (a "tuple expression") and teaching `Assign` to unpack a tuple of values into a tuple of targets, one-to-one. It's absolutely doable — and it's one of the best hands-on exercises this whole article can hand you, because it touches the lexer (comma-separated expressions), the parser (a new grammar rule), the AST (a new node shape), and the interpreter (unpacking logic) all at once. We'll return to this idea explicitly in Chapter 13.

For now, our interpreter handles the *iterative* Fibonacci function's loop and return correctly, but would need this exercise completed to handle its `a, b = 0, 1` line. Consider that your first real invitation to extend the project yourself.

### Exercises

1. Draw the full AST (in the same ASCII-tree style as above) for the `fibonacci_iterative` function's `if n <= 1: return n` portion. It should look almost identical to the recursive version's — why?
2. Why does `FuncDef` store `params` as a plain list of strings (`['n']`), rather than as a list of `Name` nodes? What does that tell you about the difference between a variable *reference* (like `n` inside an expression) and a variable *binding* (like `n` inside a parameter list)?
3. Design an AST node (with fields) for a language feature we haven't discussed yet: a ternary/conditional expression, like `x if condition else y`. What fields would it need?

### Preview of the next chapter

We finally have the data structure we've been building toward: a small, clean tree that captures exactly what a program means, with nothing extra. The next chapter is where the payoff arrives — we write the code that walks this tree and actually *executes* it, one node at a time.

---

## 7. The Interpreter: Walking the Tree

### Motivation

This is the chapter where everything pays off. We have a tree that faithfully represents a program's meaning. Now we teach the computer to *walk* that tree — visiting each node, one at a time — and actually perform the action each node describes. This process is often called **tree-walking interpretation**, and it's the simplest (though not the fastest) way to execute a program. It's also exactly the technique used by [Crafting Interpreters' first interpreter, "jlox"](https://craftinginterpreters.com/a-tree-walk-interpreter.html), and it's a great starting point before anyone tackles a faster, compiled bytecode approach (which real CPython uses under the hood).

### The problem

Given an AST node, how do we decide what Python code should run to "execute" it? A `BinOp` node needs different handling than an `If` node, which needs different handling than a `Call` node. We need a systematic way to route each node to the code that knows how to handle *that specific kind* of node.

### The analogy

Imagine a translator working at a multilingual conference, wearing a headset. Every time a new speaker starts talking, the translator has to instantly recognize *which language* is being spoken and switch to the matching translation strategy. They don't have one giant tangled function that tries to handle every language in a single breath — they have a small mental "if this language, use this strategy" dispatch table, and they apply it fresh for every single sentence, over and over, drilling down into sub-clauses as needed. That's exactly the shape of a tree-walking interpreter: for every node, look at *what kind* it is, and dispatch to the matching handler — and if that handler needs to process smaller pieces (like a `BinOp`'s left and right sides), it recursively repeats the exact same process on those pieces.

### Theory: dispatch by node type

The classic, formal name for this pattern is the [visitor pattern](https://en.wikipedia.org/wiki/Visitor_pattern) — but we don't need its full object-oriented ceremony to get the benefit. In Python, we can implement it with a simple naming convention and `getattr`:

```python
def _eval(self, node: ASTNode, env: Environment) -> Any:
    name = type(node).__name__                      # e.g. "BinOp"
    method = getattr(self, f"_eval_{name}", None)    # look up "_eval_BinOp"
    if method is None:
        raise PyRuntimeError(f"InternalError: no eval handler for {name}", node.line)
    return method(node, env)
```

Every node type gets its own small, focused method: `_eval_BinOp`, `_eval_Name`, `_eval_Call`, and so on. `_eval` itself never needs to know the details of any specific node kind — it just reads the node's Python class name and looks up the matching handler by string. This is the "dispatch table" from our translator analogy, built almost for free using Python's own introspection.

Statements get the same treatment, through a parallel `_exec` method (statements, like `if` or `while`, don't produce a value the way expressions do — they just *do* something):

```python
def _exec(self, node: ASTNode, env: Environment):
    name = type(node).__name__
    method = getattr(self, f"_exec_{name}", None)
    if method is None:
        raise PyRuntimeError(f"InternalError: no exec handler for {name}", node.line)
    method(node, env)
```

### Recursive evaluation: the heart of the machine

Here's the key realization that makes tree-walking so elegant: **most handlers just evaluate their children, then combine the results.** Look at `_eval_BinOp`:

```python
def _eval_BinOp(self, node: BinOp, env: Environment) -> Any:
    left = self._eval(node.left, env)     # recursively evaluate the left side
    right = self._eval(node.right, env)   # recursively evaluate the right side
    return self._apply_binop(node.op, left, right, node.line)
```

To evaluate `n - 1`, we don't need any special-case logic for "subtraction of variables." We just recursively call `_eval` on whatever `node.left` and `node.right` happen to be — which might themselves be more `BinOp` nodes, `Call` nodes, or simple literals — and once we have two plain values, we combine them. The tree shape *is* the recursion. There's no separate "evaluation order" to configure; it falls directly out of which children get evaluated before the parent's own logic runs.

### Variable scopes: the `Environment`

Every time we look up a variable (`n`) or call a function, we need to know *where to find its value*. That's the job of the `Environment` class — essentially a dictionary that remembers variable names and their current values, with one twist: environments can be **chained**, so that a function call gets its own private scope, while still being able to "see" variables from the scope it was defined in.

```python
class Environment:
    def __init__(self, parent: "Environment" = None):
        self.vars: dict = {}
        self.parent: Environment = parent

    def get(self, name: str, line: int = None) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)     # look one level further out
        raise PyRuntimeError(f"NameError: name '{name}' is not defined", line)
```

This chain-of-scopes idea is a simplified version of what's known as Python's [LEGB rule](https://docs.python.org/3/reference/executionmodel.html#resolution-of-names) — Local, Enclosing, Global, Built-in — the order Python searches when resolving a name. Our version only has two levels (a function's local scope, and the single global scope), which is enough to run real programs with functions and recursion, but skips nested closures over intermediate enclosing scopes.

### Tracing our running example: calling `fibonacci_recursive(5)`

This is where it gets exciting. Let's trace what actually happens, step by step, when we call `fibonacci_recursive(5)`. Every function call creates a **new** `Environment`, whose `parent` points back at the environment where the function was *defined* (this is what makes recursion — and closures — work correctly):

```python
if isinstance(callee, PyFunction):
    fn = callee.node
    call_env = Environment(parent=callee.closure)      # <-- brand new scope
    for param, val in zip(fn.params, args):
        call_env.set(param, val)                        # bind n = 5
    try:
        self._exec_stmts(fn.body, call_env)             # run the function body
    except ReturnSignal as ret:
        result = ret.value
    return result
```

Notice `except ReturnSignal`. Since `return` needs to immediately stop execution and hand a value back — potentially from deep inside a nested `if` — we use Python's own exception mechanism as a shortcut. A `return n` statement doesn't quietly set a variable; it *throws* a special internal signal that unwinds however many nested statements are currently executing, until it's caught right at the call boundary:

```python
def _exec_Return(self, node: Return, env: Environment):
    value = self._eval(node.value, env) if node.value is not None else None
    raise ReturnSignal(value)
```

Here's the call stack building up as `fibonacci_recursive(5)` recurses down to its base case. Each box is a separate `Environment`, each remembering its own value of `n`:

```
call fibonacci_recursive(5)
 env: {n: 5}
   │  n <= 1? No. → return fib(5-1) + fib(5-2) = fib(4) + fib(3)
   │
   ├─ call fibonacci_recursive(4)
   │   env: {n: 4}
   │     │  n <= 1? No. → return fib(3) + fib(2)
   │     │
   │     ├─ call fibonacci_recursive(3)
   │     │   env: {n: 3}
   │     │     │  n <= 1? No. → return fib(2) + fib(1)
   │     │     │
   │     │     ├─ call fibonacci_recursive(2)
   │     │     │   env: {n: 2}
   │     │     │     n <= 1? No. → return fib(1) + fib(0)
   │     │     │     ├─ call fibonacci_recursive(1) → env: {n: 1} → n <= 1? Yes → return 1
   │     │     │     └─ call fibonacci_recursive(0) → env: {n: 0} → n <= 1? Yes → return 0
   │     │     │     ⇒ returns 1 + 0 = 1
   │     │     │
   │     │     └─ call fibonacci_recursive(1) → env: {n: 1} → returns 1
   │     │     ⇒ returns 1 + 1 = 2
   │     │
   │     └─ call fibonacci_recursive(2)  ⇒ returns 1  (same as above, recomputed)
   │     ⇒ returns 2 + 1 = 3
   │
   └─ call fibonacci_recursive(3)  ⇒ returns 2  (recomputed)
   ⇒ returns 3 + 2 = 5
```

`fibonacci_recursive(5)` returns `5` — matching real Python. Notice, as a bonus insight: the recursive version recomputes `fibonacci_recursive(2)` and `fibonacci_recursive(3)` multiple times. That's not a bug in our interpreter — it's an honest property of this particular algorithm, and it's a big part of *why* the iterative version exists at all. Our tiny interpreter faithfully reproduces both the correct answer *and* the correct (in)efficiency of the algorithm it's running.

### Loops: `while` and `for`

`If`, `While`, and `For` all follow the same recipe: evaluate a test or iterable, then repeatedly execute a list of statements. Here's `While`:

```python
def _exec_While(self, node: While, env: Environment):
    while _ep_bool(self._eval(node.test, env)):
        self._exec_stmts(node.body, env)
```

And `For`, which additionally has to bind a loop variable on every iteration:

```python
def _exec_For(self, node: For, env: Environment):
    iterable = self._eval(node.iter, env)
    for item in iterable:
        env.set(node.target, item)
        self._exec_stmts(node.body, env)
```

Tracing `for _ in range(2, n + 1):` from `fibonacci_iterative`, with `n = 5`: `range(2, 6)` produces the list `[2, 3, 4, 5]`. Each iteration binds `_` to the next value and re-runs the loop body — which reassigns `a` and `b` — four times total.

### Exercises

1. Draw the same "call stack" diagram (in the style above) for `fibonacci_recursive(3)` on its own. How many total function calls happen?
2. Why does `_exec_If` only need to check *one* branch (`body` or `orelse`), while `_exec_While` needs to *re-check* its condition every single loop iteration? What does that tell you about the difference between "conditional" and "repeated" control flow at the interpreter level?
3. `Environment.assign()` (used by `AugAssign`, i.e. `+=`) walks *up* the parent chain to find which scope already owns a variable, before deciding where to write a new value. Why is that different from `Environment.set()`, which always writes to the *current* scope? Try to construct an example program where the difference matters.

### Preview of the next chapter

Our interpreter can already run `if`, `while`, `for`, function definitions, and arithmetic — but it can't yet *talk to the outside world*. `print()` doesn't do anything yet, because we haven't defined it. Time to add a small set of built-in functions.

---

## 8. Built-in Functions: Cheating, Legally

### Motivation

Right now, if you called `print(fibonacci_recursive(5))` in our interpreter, `_eval_Call` would look up the name `print` in the environment... and find nothing, because we never defined it. Every language needs a small set of functions that are simply "there" from the start, without the programmer writing them — things like `print`, `len`, and `range`. These are called **built-in functions**, or just **builtins**.

### The problem

Our language, as defined so far, has no way to *produce output* at all. `print(...)` needs to exist, but it can't be written *in* our language — it has to reach outside the interpreter and use Python's real, native `print()` to actually put text on the screen. Similarly, `range()`, `len()`, and friends need to be implemented using the *host* language (Python) rather than the language we're building.

### The analogy

Think of built-in functions like the pre-installed apps that come on a new phone: a calculator, a clock, a camera app. You didn't write them, and you don't need to — they're just part of the environment from the moment you turn the phone on. Everything else (the apps you install yourself) is built *using* the phone's capabilities, but those first few apps had to be baked in directly by the manufacturer, using tools the end user never sees. Our builtins are exactly that: functions "baked in" using raw Python, available to any program the moment the interpreter starts.

### Theory: builtins are just... functions

Here's the pleasantly simple realization: from the interpreter's point of view, a builtin isn't a special AST node or a special kind of syntax. It's just a **value bound to a name in the global environment**, exactly like a user-defined function — except its "body" is a real, native Python function instead of a list of AST statements.

```python
def _builtin_print(args):
    print(*(_ep_str(a) for a in args))
    return None

def _builtin_len(args):
    if len(args) != 1:
        raise PyRuntimeError("TypeError: len() takes exactly 1 argument")
    v = args[0]
    if isinstance(v, (str, list)):
        return len(v)
    raise PyRuntimeError(f"TypeError: object of type '{_type_name(v)}' has no len()")

def _builtin_range(args):
    if not (1 <= len(args) <= 3):
        raise PyRuntimeError("TypeError: range() takes 1-3 arguments")
    iargs = [int(a) for a in args]
    return list(range(*iargs))
```

And then, registering them is just... putting them in a dictionary and loading that dictionary into the interpreter's starting environment:

```python
BUILTINS = {
    "print": _builtin_print,
    "len": _builtin_len,
    "range": _builtin_range,
    # ...and int, float, str, bool, abs, max, min, type, append, pop
}

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        for name, fn in BUILTINS.items():
            self.globals.set(name, fn)   # bind "print" -> the native Python function
```

### How a call site decides "builtin or user-defined?"

Back in `_eval_Call`, we look up whatever `callee` the name resolved to, and check what *kind* of thing it is:

```python
def _eval_Call(self, node: Call, env: Environment) -> Any:
    callee = self._eval(node.func, env)
    args = [self._eval(a, env) for a in node.args]

    if callable(callee) and not isinstance(callee, PyFunction):
        return callee(args)          # it's a native Python function -> call it directly

    if isinstance(callee, PyFunction):
        # ... set up a new Environment, run the AST body, catch ReturnSignal ...
```

This is a genuinely elegant consequence of the design: **the call site doesn't care whether `fibonacci_recursive` or `print` is being called.** Both are just names that resolved to *something callable*. The only difference is what happens next — a raw Python function call for builtins, versus setting up a fresh `Environment` and walking an AST body for user-defined functions. From the language user's perspective, `print(x)` and `fibonacci_recursive(x)` look and behave identically, which matches how Python really works too (`print` genuinely is just a name pointing to a function object, and you can even do `p = print; p("hi")`).

### Tracing our running example

`print(fibonacci_recursive(5))` evaluates in this order (innermost first, since arguments must be evaluated before the outer call can happen):

```
1. Evaluate fibonacci_recursive(5)   -> recurses per Chapter 7's trace -> 5
2. Evaluate print(5)
     - callee = the _builtin_print function
     - args = [5]
     - callable(callee) is True, and it's not a PyFunction
     - call _builtin_print([5])
         -> print(*(_ep_str(a) for a in [5]))
         -> print("5")
         -> prints: 5
```

That final `_ep_str` helper deserves a mention — it's what makes `print([1, 2, 3])` show `[1, 2, 3]` instead of Python's raw internal representation, and what turns Python's native `True`/`False`/`None` into the exact capitalized strings our language uses:

```python
def _ep_str(v) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, list):
        return "[" + ", ".join(_ep_str(x) for x in v) + "]"
    return str(v)
```

### Exercises

1. Add a new builtin, `sum_list(lst)`, that adds up all the numbers in a list. What error should it raise if `lst` contains a string? Write that check explicitly, following the pattern used by `_builtin_len`.
2. `_builtin_max` and `_builtin_min` both accept *either* a single list argument (`max([1, 2, 3])`) or multiple separate arguments (`max(1, 2, 3)`). Look at how `_builtin_max` decides which case it's in, and explain the logic in one sentence.
3. **Challenge:** what would it take to let user-written code *shadow* a builtin — for example, defining your own `def print(x): ...` and having calls to `print` afterward use your version instead? Trace through `Environment.set()` and `_eval_Call` to convince yourself whether this already works, or would need a change.

### Preview of the next chapter

We've been assuming, this whole time, that programs are well-formed — that `n` is always defined, that we never divide by zero, that parentheses are always balanced. Real programs (and real programmers) make mistakes constantly. Next, we teach our interpreter to fail *helpfully* instead of crashing in confusing ways.

---

## 9. Error Handling: Failing Politely

### Motivation

Try typing `x +` into a real Python shell. You get a clear, specific message: `SyntaxError: invalid syntax`. Try `print(undefined_variable)`. You get `NameError: name 'undefined_variable' is not defined`. These aren't crashes — they're the language *communicating* what went wrong, in terms a human can act on. A good interpreter treats error messages as a first-class feature, not an afterthought.

### The problem

At every stage of our pipeline — lexing, parsing, and executing — something can go wrong. An unrecognized character. A missing colon. A variable that was never assigned. Dividing by zero. If we don't handle these deliberately, our interpreter will either crash with a confusing raw Python traceback, or (worse) silently do the wrong thing. We need a systematic way to detect problems, describe them clearly, and report exactly *where* in the source they happened.

### The analogy

Think about the difference between a strict but fair teacher handing back a paper covered in specific, actionable comments ("this argument needs a citation, right here, on line 4") versus a teacher who just writes a large red "WRONG" with no explanation. Both "caught" the same mistakes. Only one actually helps you fix them. Good error handling is the difference between those two teachers.

### Theory: one error type per pipeline stage

Our interpreter defines a small hierarchy of custom exceptions, one for each stage where something can go wrong:

```python
class PyError(Exception):
    """Base class for all our errors."""
    def __init__(self, message: str, line: int = None):
        self.message = message
        self.line = line
        super().__init__(str(self))

class LexerError(PyError):
    """Illegal character or unterminated literal."""

class ParseError(PyError):
    """Token stream violates the grammar."""

class PyRuntimeError(PyError):
    """Type error, undefined name, wrong arity, etc."""
```

Every one of these carries a `line` number, captured at the moment the problem was detected — which is exactly why every `Token` and every AST node carries a `line` field all the way from Chapter 3 onward. That small, easy-to-overlook design decision (tracking line numbers *everywhere*, from the very first token) is what makes it possible to report `SyntaxError: ... [line 12]` instead of a shrug.

### Where each error type is raised

| Error | Raised when | Example trigger |
|---|---|---|
| `LexerError` | An illegal character, or a string/comment that never closes | Typing `$` or `@` in source |
| `ParseError` | A token appears where the grammar doesn't allow it | `if x` with no trailing `:` |
| `PyRuntimeError` | A valid-looking program does something meaningless at execution time | `undefined_var + 1`, `5 / 0`, calling a number |

Let's look at one real example from each stage.

**Lexer stage** — an unrecognized character:

```python
else:
    self._err(f"SyntaxError: unexpected character {ch!r}")
```

```
>>> x = 5 $ 3
LexerError: SyntaxError: unexpected character '$' [line 1]
```

**Parser stage** — a missing colon:

```python
def _if_stmt(self) -> If:
    test = self._expr()
    self._expect(TT.COLON, "expected ':' after if-condition")
    ...
```

```
>>> if n <= 1
...     return n
ParseError: SyntaxError: expected ':' after if-condition [line 1]
```

**Runtime stage** — dividing by zero:

```python
if op == "/":
    if right == 0:
        raise PyRuntimeError("ZeroDivisionError: division by zero", line)
    return left / right
```

```
>>> 5 / 0
PyRuntimeError: ZeroDivisionError: division by zero [line 1]
```

**Runtime stage** — an undefined variable, straight from our `Environment.get`:

```python
def get(self, name: str, line: int = None) -> Any:
    if name in self.vars:
        return self.vars[name]
    if self.parent:
        return self.parent.get(name, line)
    raise PyRuntimeError(f"NameError: name '{name}' is not defined", line)
```

```
>>> print(mystery_variable)
PyRuntimeError: NameError: name 'mystery_variable' is not defined [line 1]
```

### Tying it back to the REPL

Recall the real REPL's execution loop from Chapter 2:

```python
try:
    run_source(source + "\n", interp)
except (LexerError, ParseError, PyRuntimeError) as e:
    print(e)
```

Every one of our three custom error types is caught in exactly the same place, and simply printed. Because `PyError.__str__` already formats a friendly message including the line number:

```python
def __str__(self) -> str:
    loc = f" [line {self.line}]" if self.line else ""
    label = f"\033[91m{type(self).__name__}\033[0m"   # colored red in a terminal
    return f"{label}: {self.message}{loc}"
```

...the REPL's error handling is refreshingly small: catch, print, move on to the next line. This is only possible *because* we were disciplined about raising specific, well-described errors at every earlier stage — the payoff of Chapters 3 through 7's carefulness shows up as simplicity here in Chapter 9.

### Why crash cleanly instead of catching *everything*?

You might notice the REPL specifically catches `(LexerError, ParseError, PyRuntimeError)` — not a bare `except Exception`. This is deliberate. If some *other*, unexpected Python exception occurs (say, a genuine bug in the interpreter itself), we want that to be visible as an "InternalError," clearly distinguished from an error in the *user's* program:

```python
except Exception as e:
    print(f"\033[91mInternalError\033[0m: {e}")
```

This distinction matters enormously in real-world tools: **"your code has a mistake" and "our tool has a bug" are different categories of problem**, and conflating them (by showing a raw traceback for both) makes debugging harder for everyone. CPython itself is careful about the same distinction — a `SyntaxError` in your code looks very different from a genuine CPython internal error (which is rare enough to be considered a reportable bug).

### Exercises

1. Try to trigger all three of `LexerError`, `ParseError`, and `PyRuntimeError` yourself, using variations of our running Fibonacci example (e.g., remove a colon, misspell `fibonacci_recursive`, or call it with the wrong number of arguments).
2. Look at `_builtin_len`'s error message: `"TypeError: object of type '{_type_name(v)}' has no len()"`. Real Python's message for `len(5)` is almost word-for-word identical. Why do you think matching real Python's phrasing, even in a toy interpreter, is worth the effort?
3. **Challenge:** currently, if a `for` loop's target is used outside the loop afterward, it keeps its last value (matching real Python's behavior, actually!). Is that a bug or a feature? Try it in a real Python shell to check your intuition, and explain why our `Environment.set()` makes this fall out naturally.

### Preview of the next chapter

We've talked about environments, stacks of function calls, and dictionaries mapping names to values — all without stepping back to look at these as a *general toolkit*. The next chapter takes a step back and tours the small set of core data structures that make interpreters (and most of computer science) tick.

---

## 10. Data Structures Under the Hood

### Motivation

Throughout this article, we've quietly been using a handful of general-purpose data structures — without stopping to name them as a category. This chapter is a short, deliberate pause to name them explicitly, because recognizing them will help you read *any* interpreter's source code, not just ours.

### The problem

If someone shows you the source code of a real language runtime (CPython, Ruby's MRI, a JavaScript engine), it will look intimidating at first glance. But almost all of that complexity is built from a small number of well-known, well-understood building blocks. Once you can point at a piece of unfamiliar code and say "oh, that's just a stack" or "that's just a dictionary with a twist," the intimidation mostly evaporates.

### Theory: the toolkit

| Structure | What it is | Where we used it | Analogy |
|---|---|---|---|
| **Stack** | A pile where you can only add/remove from the top | `indent_stack` in the lexer (Chapter 3); the call stack itself (Chapter 7) | A stack of plates — you take from the top, put back on the top |
| **Call stack** | A stack of "what function is currently running, and what should happen when it returns" | Every recursive call to `fibonacci_recursive` (Chapter 7) | Nested Russian dolls — the innermost one has to finish before the next one out can continue |
| **Dictionary / hash map** | Fast lookup from a key to a value | `KEYWORDS` (Chapter 3); `Environment.vars` (Chapter 7); `BUILTINS` (Chapter 8) | A phone book — look up a name, get a number back, without reading every entry |
| **Symbol table** | A dictionary specifically mapping *names* to *what they refer to* | `Environment` itself is a chain of symbol tables | A classroom seating chart — "this name" sits "at this desk" |
| **Environment (scope chain)** | A linked chain of symbol tables, innermost first | `Environment.parent` (Chapter 7) | A set of nested folders — look in the current folder first, then its parent folder, and so on |
| **Tree** | Nodes connected by parent-child links, no cycles | The AST itself (Chapters 5-6) | A family tree, or the folders-within-folders on your computer |
| **Heap** *(briefly)* | The region of memory where long-lived, dynamically-sized data lives | Not implemented explicitly in our interpreter — Python's own memory manager handles it for us | A big shared warehouse, versus the call stack's small, personal desk that gets cleared the moment you leave the room |

### The stack, concretely

We already saw two different stacks in this article without naming them as such. The lexer's indentation tracking:

```python
self.indent_stack = [0]
...
self.indent_stack.append(indent)   # push
...
self.indent_stack.pop()            # pop
```

And the *call stack*, implicit in every recursive Python function call our interpreter makes while walking the AST. When `_eval_Call` calls `_exec_stmts`, which calls `_exec`, which calls `_eval_BinOp`, which calls `_eval` again on a nested `Call`... each of those is a **frame** pushed onto Python's own native call stack, on our behalf, for free. This is a subtle but important point: **our tree-walking interpreter's call stack literally *is* Python's own call stack.** We didn't implement a call stack ourselves — we got one for free by using recursive Python function calls to walk a recursive tree structure. That's a common (and very convenient) shortcut for tree-walking interpreters; a bytecode-based interpreter, by contrast, usually manages its *own* explicit stack data structure, because it isn't relying on its host language's call stack the same way.

### The symbol table / environment, concretely

We can now describe `Environment` more precisely: it's a **symbol table** (a dictionary from names to values) that additionally supports **chaining** to a parent symbol table. Here's a picture of what the environment chain looks like *during* the call to `fibonacci_recursive(3)`, deep inside its own recursive call to `fibonacci_recursive(2)`:

```
 globals
 ┌─────────────────────────────────────┐
 │ print, len, range, ... (builtins)   │
 │ fibonacci_recursive: <function>     │
 │ fibonacci_iterative: <function>     │
 └───────────────▲─────────────────────┘
                 │ parent
 ┌───────────────┴─────────────────────┐
 │  call_env for fibonacci_recursive(3)│
 │  { n: 3 }                           │
 └───────────────▲─────────────────────┘
                 │ parent
 ┌───────────────┴─────────────────────┐
 │  call_env for fibonacci_recursive(2)│
 │  { n: 2 }                           │
 └──────────────────────────────────────┘
```

Looking up `n` from inside the innermost call finds it immediately (it's in the current scope). Looking up `fibonacci_recursive` from that same innermost call fails locally, then succeeds by walking `parent` all the way up to `globals` — exactly the code in `Environment.get()` from Chapter 7.

### The heap, briefly

Real language runtimes distinguish between the **stack** (small, fast, automatically cleaned up the moment a function returns) and the **heap** (a larger, more flexible pool of memory for data that needs to outlive a single function call — like a list you return from a function and keep using afterward). We don't implement a heap ourselves; our interpreter is written in Python, so every list, string, and number we create is already being managed by *Python's own* memory allocator and [garbage collector](https://docs.python.org/3/library/gc.html) behind the scenes. This is one of the genuine advantages of building a toy interpreter *in* a high-level language: we get memory management for free, and can focus entirely on language semantics. (If you ever build an interpreter in C, this free lunch disappears, and manual memory management becomes one of the hardest parts of the whole project.)

### Exercises

1. In the environment-chain diagram above, what would go wrong if `call_env`'s `parent` pointed at the *caller's* environment (i.e., whoever called `fibonacci_recursive`) instead of the function's own defining scope (`globals`)? Try to construct a small example where the difference is observable. (This distinction — closing over the *defining* scope rather than the *calling* scope — is the whole idea behind [lexical scoping](https://en.wikipedia.org/wiki/Scope_(computer_science)#Lexical_scoping).)
2. We said our call stack is "free," borrowed from Python's own recursive function calls. What do you think would happen if you called `fibonacci_recursive(10000)` in our interpreter? (Hint: look up "maximum recursion depth" in Python.)
3. Sketch, in your own words, why a dictionary (hash map) is a better fit for `Environment.vars` than, say, a plain list of `(name, value)` pairs searched one at a time.

### Preview of the next chapter

Our interpreter can run real logic, but it still can't do much with the *outside world* — no math functions beyond basic arithmetic, no randomness, no access to time or files. Real Python solves this with its enormous standard library. Let's look at where that begins, and how our interpreter could eventually plug into it.

---

## 11. Where Python's Standard Library Begins

### Motivation

Real Python ships with what's affectionately called a ["batteries included"](https://docs.python.org/3/tutorial/stdlib.html) standard library: hundreds of modules covering math, file I/O, networking, dates, randomness, and much more. Our interpreter currently has none of this — just a dozen or so builtins. This chapter is about understanding *where* those modules conceptually sit, relative to everything we've built so far, so that extending our interpreter toward them feels like a natural next step rather than a mystery.

### The problem

Builtins like `print` and `len` are available *automatically*, with no import required. Most of Python's functionality, though, lives behind an explicit `import` statement:

```python
import math
import random
import time
from pathlib import Path
```

Our interpreter doesn't support `import` at all yet — which is intentional, since it's listed as a growth exercise in Chapter 13. But it's worth understanding conceptually where modules like `math`, `random`, `time`, `os`, and `pathlib` fit into the picture, because the mechanism for adding them is a direct extension of Chapter 8's builtin-function trick.

### The analogy

If builtins are the pre-installed apps that came with your phone, the standard library is the *official app store* run by the same company that made the phone. You still have to explicitly "install" (import) each app before using it, but you trust it implicitly, because it ships with, and is maintained alongside, the language itself — as opposed to a truly third-party package you'd install from elsewhere (Python's equivalent there is [PyPI](https://pypi.org/), the Python Package Index).

### A quick tour of the modules mentioned in this chapter

| Module | What it's for | A representative function |
|---|---|---|
| [`math`](https://docs.python.org/3/library/math.html) | Mathematical functions beyond basic arithmetic | `math.sqrt(16)` → `4.0` |
| [`random`](https://docs.python.org/3/library/random.html) | Pseudo-random number generation | `random.randint(1, 6)` → a dice roll |
| [`time`](https://docs.python.org/3/library/time.html) | Reading the clock, measuring durations | `time.time()` → seconds since a fixed reference point |
| [`os`](https://docs.python.org/3/library/os.html) | Talking to the operating system (files, processes, environment variables) | `os.listdir(".")` → files in the current folder |
| [`pathlib`](https://docs.python.org/3/library/pathlib.html) | A more modern, object-oriented way of handling filesystem paths | `Path("data.txt").exists()` → `True`/`False` |

### How our interpreter *could* expose these

Here's the key idea: from our interpreter's point of view, exposing `math.sqrt` isn't conceptually different from exposing `len` or `print`. It's still just "a name in the global environment, pointing to a native Python callable." We could extend `BUILTINS` today, with zero new AST nodes or grammar rules, simply by wrapping real Python functions:

```python
import math as _math

def _builtin_sqrt(args):
    if len(args) != 1:
        raise PyRuntimeError("TypeError: sqrt() takes 1 argument")
    v = args[0]
    if not isinstance(v, (int, float)) or v < 0:
        raise PyRuntimeError("ValueError: math domain error")
    return _math.sqrt(v)

BUILTINS["sqrt"] = _builtin_sqrt
```

That's genuinely the whole mechanism. The only reason we don't already expose all of `math` this way is that Python's real `math` module doesn't require an explicit `import math` prefix in *our* language yet — every function we add this way behaves like a global builtin, similar to `len` or `range`, rather than living inside a proper namespace.

### Where `import` would fit in

To support real Python-style `import math` followed by `math.sqrt(16)`, we'd need a few new pieces working together:

1. **Lexer**: no changes needed — `import`, `math`, and `.` are already tokenizable (in fact `import` would just need adding to `KEYWORDS`).
2. **Parser**: a new grammar rule, `import_stmt := 'import' NAME`, producing a new AST node, say `Import(name='math')`.
3. **AST / Interpreter**: `Import` would look up a Python "module object" (perhaps just a dictionary of builtin functions, namespaced) and bind it to a name in the environment — e.g., `env.set('math', {'sqrt': _builtin_sqrt, ...})`.
4. A tweak to attribute access (recall from Chapter 4 that our parser currently *requires* every `.name` to be followed by a call — `.method()` — and explicitly rejects bare attribute access like `.name` without parentheses). We'd need to relax that restriction so `math.sqrt` can be looked up as "the `sqrt` attribute of the `math` object," separately from calling it.

None of this is conceptually hard — it's a natural extension of ideas we've already built. It's simply more grammar, one more AST node, and one more interpreter case, following the exact same recipe as every other feature in this article.

### Exercises

1. Using the `_builtin_sqrt` pattern above, sketch (in pseudocode or real Python) a `_builtin_random_int(args)` builtin wrapping `random.randint`. What argument-count and type checks should it perform, following the style of `_builtin_len` and `_builtin_range`?
2. Why do you think real Python separates "builtins" (like `print`, `len`) from "standard library modules" (like `math`, `os`) instead of making everything a global builtin? What tradeoff is this separation managing? (Hint: think about namespace collisions, and how many function names *could* exist across hundreds of modules.)
3. Look back at the parser's `_primary()` method (Chapter 4). Find the exact line that currently raises an error for attribute access without a call, and describe in your own words what minimal change would be needed to support `math.sqrt` as a two-step "get attribute, then optionally call it" operation.

### Preview of the next chapter

Some of the modules above (`os`, `pathlib`) don't just compute values — they reach *outside* the running program entirely, into the filesystem, the clock, or other processes. That's a good excuse to talk explicitly about how *any* interpreter — ours or CPython's — actually communicates with the operating system it's running on.

---

## 12. Talking to the Operating System

### Motivation

Every real program eventually needs to do something the CPU alone can't do by itself: read a file, write to the screen, wait for a network response, or ask "what time is it?" These capabilities don't live inside the interpreter — they live in the **operating system**, and the interpreter has to explicitly ask for them.

### The problem

Our `_builtin_print` function calls Python's real `print()`, which — many layers down — eventually asks the operating system to write bytes to a stream (your terminal). We've been relying on this the whole article without examining it. This chapter briefly opens that box.

### The analogy

Think of the operating system as a hotel's front desk, and your program as a guest. You, the guest, aren't allowed to walk into the kitchen and cook your own food, or go into the electrical room and flip breakers yourself. Instead, you call the front desk and make a *request*: "please bring food to room 204," "please turn the lights back on." The front desk (the OS) has exclusive control over the shared, sensitive resources — CPU time, memory, disks, network cards — and every program has to go through it, using an agreed-upon set of request formats, to get anything done. Those agreed-upon request formats are called **system calls**. If you want a rigorous reference, [Wikipedia's system call article](https://en.wikipedia.org/wiki/System_call) is a solid one.

### Theory: a few concrete OS-level operations

| Operation | What it does | Common Python spelling |
|---|---|---|
| `open()` | Ask the OS to grant access to a file | `open("data.txt")` |
| `read()` | Ask the OS for the next chunk of bytes from an open file | `f.read()` |
| `write()` | Ask the OS to store bytes into an open file (or terminal) | `f.write("hi")`, `print(...)` |
| `mkdir()` | Ask the OS to create a new folder | `os.mkdir("new_folder")` |
| process creation | Ask the OS to start a whole new running program | `subprocess.run([...])` |

Each of these is, at its core, a request handed off to the operating system's kernel, which is the only part of the whole system trusted to directly touch hardware. Python's `open()`, in fact, is itself just a friendly wrapper around your OS's native `open` system call — Python asks, the OS checks permissions and disk state, and either hands back a working file handle or reports an error (which is exactly why `open("missing.txt")` can raise `FileNotFoundError`: the OS said no, and Python translated that "no" into a Python exception).

### Where our interpreter's `print` fits into this

Trace the whole chain, from our AST all the way down to your screen:

```
Call(func=Name('print'), args=[...])          <- our AST node (Chapter 6)
        │
        ▼  _eval_Call  ->  _builtin_print(args)         (Chapter 8)
        │
        ▼  Python's real print(*values)
        │
        ▼  Python's io module writes to sys.stdout
        │
        ▼  a "write" system call, handed to the OS kernel
        │
        ▼  the OS forwards those bytes to your terminal
        │
        ▼  the terminal renders characters on your screen
```

Six layers, and we only implemented the very top one! This is a genuinely important thing to internalize: **almost every layer of a modern computing stack is built by delegating "the hard, dangerous, shared-resource part" downward to something else that's already solved it.** Our interpreter delegates output to Python. Python delegates it to the operating system. The operating system delegates it to a device driver. The device driver delegates it to hardware. Nobody at any layer needs to understand every layer below them completely — they just need to trust the interface.

### If we wanted our language to read files itself

Following the exact same recipe as Chapter 8 and Chapter 11, adding filesystem access to our toy language would mean wrapping Python's own `open()`/`read()`/`write()` behind new builtins:

```python
def _builtin_read_file(args):
    if len(args) != 1 or not isinstance(args[0], str):
        raise PyRuntimeError("TypeError: read_file() takes 1 string argument")
    try:
        with open(args[0], "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        raise PyRuntimeError(f"FileNotFoundError: no such file: {args[0]!r}")

BUILTINS["read_file"] = _builtin_read_file
```

Same shape, same pattern, every time: **wrap a trusted, already-working native function, check the arguments defensively, translate any native exception into our own error type.** By this point in the article, that pattern should feel completely familiar — it's the same one we used for `len`, `range`, and `sqrt`.

### Exercises

1. Why do you think operating systems don't let ordinary programs directly manipulate the disk's hardware, and instead force everything through system calls? What could go wrong if two programs both tried to write raw bytes to the same physical disk location at the same time, with no OS mediating?
2. Trace, in your own words, what happens differently if `_builtin_read_file`'s target file exists but the *user running the program* doesn't have permission to read it. Which layer (Python, the OS, or our interpreter) do you think detects that, and what Python exception would likely be raised instead of `FileNotFoundError`?
3. **Challenge:** sketch a `_builtin_write_file(args)` builtin, following the same defensive pattern as `_builtin_read_file` above. What arguments should it take, and what should happen if the containing folder doesn't exist?

### Preview of the next chapter

We've now walked the entire pipeline: text in, tokens, a parse tree, a clean AST, tree-walking execution, builtins, error handling, core data structures, and a glimpse of how a real standard library and operating system fit around all of it. The last chapter is a tour of everything we deliberately left out — and a map for where to go next if you want to keep growing this project.

---

## 13. Growing the Interpreter: What's Next?

### Motivation

A finished toy interpreter is not the end of the story — it's a foundation sturdy enough to experiment on. This chapter is a map of the biggest features we deliberately left out, with just enough of an explanation of *why each one is hard* that you can decide which one sounds like the most fun to tackle yourself.

### The tuple-assignment exercise, revisited

Before the bigger list, let's close the loop on the concrete gap we flagged back in Chapter 6: our grammar doesn't support `a, b = 0, 1` or `a, b = b, a + b`. If you want a genuinely satisfying first project on top of this article, that's it. It touches every layer we built:

1. **Parser**: after parsing an expression, check for a following comma, and if present, keep collecting a comma-separated list of expressions (this is usually called a "tuple expression" in real Python).
2. **AST**: give `Assign` a list of targets instead of a single string, and let its `value` field be either a single expression or a tuple of expressions.
3. **Interpreter**: when executing an `Assign` whose value evaluated to a tuple-like structure, zip the targets against the values and bind each one — being careful, for `a, b = b, a + b`, that *all* right-hand values are computed **before** any left-hand assignment happens (this is the exact detail that makes swap-style assignment work correctly in real Python).

### The bigger list

| Feature | What it adds | Why it's a meaningfully bigger step |
|---|---|---|
| **Classes** | User-defined types with methods and attributes | Needs a new kind of environment (an "instance," with its own attribute dictionary) and a rule for how method calls find `self`. See [Python's data model docs](https://docs.python.org/3/reference/datamodel.html). |
| **Modules & imports** | Splitting code across files, `import` | Needs a way to load, parse, and cache another file's AST, plus a namespacing rule so names don't collide — this is the piece we sketched conceptually in Chapter 11. |
| **Decorators** | `@some_decorator` wrapping a function definition | Requires functions to be full first-class values that can themselves be passed into, and returned from, other functions — a small step past what we've built, since our `PyFunction` objects are already values. |
| **Exceptions (`try`/`except`)** | User-level error recovery, not just interpreter-level errors | We already have an internal exception mechanism (`ReturnSignal`) — user-facing exceptions are a generalization: a `raise` statement that unwinds until a matching `except` catches it. |
| **Generators (`yield`)** | Functions that pause and resume, producing a sequence lazily | Genuinely hard: a tree-walking interpreter has to somehow *suspend* in the middle of executing a function body and resume later, which usually requires either real coroutines or restructuring execution around an explicit, resumable stack machine. See [PEP 255](https://peps.python.org/pep-0255/) for the original design rationale. |
| **Async / await** | Cooperative concurrency | Builds on the same "pause and resume" machinery as generators, plus an event loop to decide *when* to resume each paused task. |
| **Bytecode compilation** | Compiling the AST to a flatter, faster instruction format before running it | This is what real CPython actually does — the AST is compiled to bytecode instructions (viewable via Python's own [`dis` module](https://docs.python.org/3/library/dis.html)) that run on a small virtual stack machine, which is significantly faster than re-walking a tree on every single execution. |
| **JIT compilation** | Compiling hot code paths directly to native machine code at runtime | The next major performance step past bytecode — used by projects like PyPy, and increasingly by CPython itself; a genuinely deep systems topic on its own. |
| **Garbage collection** | Automatically reclaiming memory no longer in use | We get this for free today, because our interpreter is written in Python. Building your own (say, in C or Rust) means implementing something like reference counting or a mark-and-sweep collector — see [Wikipedia's garbage collection article](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)) for an overview of the main strategies. |

### A closing analogy

If this article was baking your first loaf of bread, the list above is the rest of the bakery: sourdough starters, laminated pastry, wedding cakes. None of it is required to appreciate what you just built — but all of it is now *reachable*, because you understand the fundamental steps (mixing, rising, baking) that every fancier recipe still relies on underneath. Every one of the features in this table is, underneath its own complexity, still built from lexing, parsing, an AST, and something that walks or compiles that AST — the exact pipeline you now know by heart.

### Exercises

1. Pick exactly one row from the table above. Without writing any code yet, write two or three sentences describing which of our *existing* AST nodes and interpreter methods you'd reuse unchanged, and which ones you'd need to modify or add.
2. Revisit your answer to Chapter 1's Exercise 2 (your original guess about what happens between typing code and seeing output). How has it changed?
3. If you could add exactly one feature from the table above to our interpreter this week, which would you pick, and why?

### Preview of the next chapter

One short wrap-up, tying every chapter's piece back into the single pipeline diagram we started with — plus a map of where to go if you want to keep exploring.

---

## 14. Wrap-Up

Let's return to the diagram from Chapter 1, and this time fill in exactly what we built at every stage:

```
   source code (text)
   "print(fibonacci_recursive(5))"
          │
          ▼
   ┌─────────────────────┐
   │   LEXER (Ch. 3)     │   text -> tokens
   │   Lexer class       │   [NAME, LPAREN, NAME, LPAREN, INTEGER, RPAREN, RPAREN, NEWLINE, EOF]
   └─────────────────────┘
          │
          ▼
   ┌─────────────────────┐
   │  PEG PARSER (Ch. 4)  │   tokens -> parse tree (Ch. 5) -> lean AST (Ch. 6)
   │  Parser class        │   Call(func=Name('print'), args=[Call(func=Name('fibonacci_recursive'), args=[5])])
   └─────────────────────┘
          │
          ▼
   ┌─────────────────────┐
   │ INTERPRETER (Ch. 7) │   AST -> behavior, via recursive tree-walking + Environment scopes
   │ Interpreter class   │
   └─────────────────────┘
          │           ▲
          ▼           │
   ┌─────────────────────┐
   │  BUILTINS (Ch. 8)   │   print, len, range, ... — native Python functions, called just like user functions
   └─────────────────────┘
          │
          ▼
        "5"     ← printed to your terminal, via the OS (Ch. 12)

   Woven throughout: ERROR HANDLING (Ch. 9), DATA STRUCTURES (Ch. 10),
   and a map toward the STANDARD LIBRARY (Ch. 11) and beyond (Ch. 13).
```

Every box in that diagram started this article as a mystery and ends it as a few hundred lines of Python you could write yourself, from memory, given enough time. That's the entire goal of this article — not to make you a compiler-theory expert, but to make the gap between "I use Python" and "I understand how Python works" feel small and crossable.

### Where to go from here

- Re-implement this same pipeline in a language you don't know well yet — Rust, Go, or C++ are all excellent choices, and because the *ideas* in this article are language-agnostic, you'll spend your energy learning the new language's syntax rather than relearning the interpreter concepts from scratch.
- Pick one item from Chapter 13's table and actually build it.
- Read [Crafting Interpreters](https://craftinginterpreters.com/) end to end — it covers this exact territory (and a full bytecode virtual machine) in much greater depth, for a different toy language called Lox.
- Skim CPython's own [`Grammar/python.gram`](https://docs.python.org/3/reference/grammar.html) and [`Python-ast.asdl`](https://docs.python.org/3/library/ast.html) — after this article, they should look far more familiar than intimidating.

### One last look at the running example

Both functions we've been tracing all article long, side by side, exactly as our interpreter now understands them:

```python
def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

print(fibonacci_recursive(5))   # -> 5

def fibonacci_iterative(n):
    if n <= 1:
        return n
    a, b = 0, 1                  # exercise: see Chapter 13
    for _ in range(2, n + 1):
        a, b = b, a + b          # exercise: see Chapter 13
    return b

print(fibonacci_iterative(5))   # -> 5
```

Thanks for building this with us. Now go build the rest.

---

## Appendix: Full Reference Implementation

Everything in this article was drawn from a single, self-contained Python file implementing the lexer, parser, AST, environment, interpreter, builtins, error types, an AST pretty-printer, and a REPL — a little over 1,000 lines in total. If you want to run it yourself, save it as `py.py` and run `python3 py.py your_script.py`, or run it with no arguments to drop into the REPL. Passing `--ast` alongside a script prints the parsed AST before executing it, which is a great way to check your understanding against Chapters 5 and 6.

The full file is organized into the same sections this article walked through, in the same order:

```
§1  ERRORS               (Chapter 9)
§2  TOKENS                (Chapter 3)
§3  LEXER                 (Chapter 3)
§4  AST NODES             (Chapter 6)
§5  PARSER                (Chapter 4, 5, 6)
§6  ENVIRONMENT           (Chapter 7, 10)
§7  BUILTIN FUNCTIONS     (Chapter 8)
§8  INTERPRETER           (Chapter 7)
§9  AST PRETTY PRINTER    (Chapter 6)
§10 PIPELINE              (Chapter 1, 14)
§11 REPL                  (Chapter 2)
§12 CLI ENTRY POINT       (running it from the command line)
```

Rather than repeat the entire file here, we've quoted the load-bearing pieces of it directly, in context, in every chapter above — that's deliberate, so that each chapter's code sits right next to the explanation that motivates it, rather than asking you to flip back and forth to a giant listing. If you'd like the complete, runnable file exactly as referenced throughout this article, it's the natural companion piece to keep alongside this write-up.