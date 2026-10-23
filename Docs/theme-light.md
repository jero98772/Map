# Light theme — "Blueprint textbook"

Turned on with `html[data-theme="light"]` in
[`core/static/css/base.css`](../core/static/css/base.css).

## Personality

A well-printed textbook on cool blueprint paper. **Navy ink** on an off-white page with a
slight blue tint, white cards that look like printed figures, and **muted amber** keywords
that work like a highlighter in the margin. It should feel like a careful lesson you can
study in daylight, clean and serious without being cold.

**Clean · academic · approachable · trustworthy**

## Core palette

| Token          | Hex       | Role                                               |
|----------------|-----------|----------------------------------------------------|
| `--bg-light`   | `#f5f8fc` | Page background                                    |
| `--text-light` | `#10213f` | Body text                                          |
| `--card`       | `#ffffff` | Cards, panels, raised surfaces                     |
| `--code-bg`    | `#eaf1fb` | Code blocks                                        |
| `--border`     | `#d7e3f2` | Dividers, card and code borders (`--border-light`) |
| `--accent`     | `#16357a` | Links, highlights, focus (`--navy-700`)            |
| `--muted`      | `#4a5a78` | Secondary text, captions, file paths               |
| `--ok`         | `#2f7d3e` | Passing tests, correct output                      |
| `--err`        | `#c62828` | Errors, failing tests, error messages              |

## Syntax highlighting

| Token          | Hex       | Used for                     |
|----------------|-----------|------------------------------|
| `--hl-keyword` | `#9a6700` | `def`, `if`, `while`… (amber) |
| `--hl-name`    | `#1d5fbf` | Identifiers, function names  |
| `--hl-type`    | `#16357a` | Types, classes (navy ink)    |
| `--hl-string`  | `#2f7d3e` | String literals              |
| `--hl-comment` | `#6a7a94` | Comments                     |

## Shared brand colors (the same in both themes)

| Token           | Hex       | Role                          |
|-----------------|-----------|-------------------------------|
| `--navy-900`    | `#071633` | Navbar, darkest navy          |
| `--navy-800`    | `#0d2456` | Navbar hover / mid navy       |
| `--navy-700`    | `#16357a` | Navbar active; light-theme accent |
| `--blue-clear`  | `#7fd1ff` | Brand blue on navy            |
| `--blue-bright` | `#d3f1ff` | Brand title text              |
| `--logo-blue`   | `#2f6fd6` | Logo                          |
| `--logo-yellow` | `#f5c02f` | Logo                          |

The navbar stays navy in the light theme as well, so the brand looks the same in both.

## Typography

- Text: `'Segoe UI', system-ui, -apple-system, sans-serif`
- Code: `ui-monospace, Menlo, Consolas, monospace`

## Usage rules

- Use the CSS variables and never hard-code hex values. Every token here overrides a dark default.
- Don't use the dark theme's yellow `#f5c02f` for text on the light page, because it is too faint. Keywords use `#9a6700` instead.
- Use `--accent` (navy ink) only for things you can click or follow.
- Use `--ok` / `--err` only for interpreter results (tests, outputs, `.errmsg`).
- Mark light-only content with `.only-light` and use the `*_light.png` image variants (for example `pipeline-programing_languages_light.png`).

## CSS

```css
html[data-theme="light"] {
    --accent: var(--navy-700);     /* #16357a */
    --muted: #4a5a78;
    --card: #ffffff;
    --code-bg: #eaf1fb;
    --border: var(--border-light); /* #d7e3f2 */
    --ok: #2f7d3e;
    --err: #c62828;
    --hl-keyword: #9a6700;
    --hl-name: #1d5fbf;
    --hl-type: var(--navy-700);
    --hl-string: #2f7d3e;
    --hl-comment: #6a7a94;
}
html[data-theme="light"] body { background: var(--bg-light); color: var(--text-light); }
```
