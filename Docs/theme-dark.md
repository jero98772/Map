# Dark theme — "Night-shift terminal"

The default theme of the MAP tutorial site. It is set on `:root` in
[`core/static/css/base.css`](../core/static/css/base.css).

## Personality

Late at night, the editor is the only light in the room and the interpreter is starting to
work. The dark theme is a **deep navy sky** with **clear blue** light for anything you can
click or follow. Keywords are lit in **logo yellow**, the spark of the language. It should
feel quiet and calm and keep you focused on the code.

**Calm · focused · nocturnal · precise**

## Core palette

| Token          | Hex       | Role                                              |
|----------------|-----------|---------------------------------------------------|
| `--bg-dark`    | `#0b1220` | Page background                                   |
| `--text-dark`  | `#e6edf5` | Body text                                         |
| `--card`       | `#0e1a33` | Cards, panels, raised surfaces                    |
| `--code-bg`    | `#071633` | Code blocks (`--navy-900`)                        |
| `--border`     | `#1b2c52` | Dividers, card and code borders (`--border-dark`) |
| `--accent`     | `#7fd1ff` | Links, highlights, focus (`--blue-clear`)         |
| `--muted`      | `#9fb0c8` | Secondary text, captions, file paths              |
| `--ok`         | `#8be0a4` | Passing tests, correct output                     |
| `--err`        | `#ff7b7b` | Errors, failing tests, error messages             |

## Syntax highlighting

| Token          | Hex       | Used for                     |
|----------------|-----------|------------------------------|
| `--hl-keyword` | `#f5c02f` | `def`, `if`, `while`… (logo yellow) |
| `--hl-name`    | `#7fd1ff` | Identifiers, function names  |
| `--hl-type`    | `#6fa8ff` | Types, classes               |
| `--hl-string`  | `#8be0a4` | String literals              |
| `--hl-comment` | `#6c7fa3` | Comments                     |

## Shared brand colors (the same in both themes)

| Token           | Hex       | Role                          |
|-----------------|-----------|-------------------------------|
| `--navy-900`    | `#071633` | Navbar, darkest navy          |
| `--navy-800`    | `#0d2456` | Navbar hover / mid navy       |
| `--navy-700`    | `#16357a` | Navbar active / light navy    |
| `--blue-clear`  | `#7fd1ff` | Brand blue on navy            |
| `--blue-bright` | `#d3f1ff` | Brand title text              |
| `--logo-blue`   | `#2f6fd6` | Logo                          |
| `--logo-yellow` | `#f5c02f` | Logo                          |

The navbar is always navy, whichever theme the page uses.

## Typography

- Text: `'Segoe UI', system-ui, -apple-system, sans-serif`
- Code: `ui-monospace, Menlo, Consolas, monospace`

## Usage rules

- Use the CSS variables and never hard-code hex values, so the light theme can override them.
- Use `--accent` only for things you can click or follow (links, focus, the current step). Don't use it for decoration.
- Use `--ok` / `--err` only for interpreter results (tests, outputs, `.errmsg`). Don't use them for general emphasis.
- Use `--muted` for metadata such as file paths (`.cpy`, `.where`) and captions.
- Mark dark-only content with `.only-dark` and use the `*_dark.png` image variants (for example `pipeline-programing_languages_dark.png`).

## CSS

```css
:root {
    --accent: var(--blue-clear);   /* #7fd1ff */
    --muted: #9fb0c8;
    --card: #0e1a33;
    --code-bg: var(--navy-900);    /* #071633 */
    --border: var(--border-dark);  /* #1b2c52 */
    --ok: #8be0a4;
    --err: #ff7b7b;
    --hl-keyword: var(--logo-yellow); /* #f5c02f */
    --hl-name: var(--blue-clear);
    --hl-type: #6fa8ff;
    --hl-string: #8be0a4;
    --hl-comment: #6c7fa3;
}
body { background: var(--bg-dark); color: var(--text-dark); }
```
