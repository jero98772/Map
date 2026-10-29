fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();

    if args.is_empty() {
        repl();
        return;
    }

    let show_ast = args.iter().any(|a| a == "--ast");
    let files: Vec<&String> = args.iter().filter(|a| !a.starts_with("--")).collect();

    if files.is_empty() {
        println!("Usage: py <script.py> [--ast]");
        std::process::exit(1);
    }

    let filepath = files[0];

    let source = match std::fs::read_to_string(filepath) {
        Ok(s) => s,
        Err(_) => {
            println!("\x1b[91mFileNotFoundError\x1b[0m: No such file: {:?}", filepath);
            std::process::exit(1);
        }
    };

    let result = if show_ast {
        run_source_with_ast(&source)
    } else {
        let interp = Interpreter::new();
        run_source(&source, &interp)
    };

    if let Err(e) = result {
        println!("{}", e);
        std::process::exit(1);
    }
}
