fn builtin_print(args: &[Value]) -> Result<Value, PyError> {
    let parts: Vec<String> = args.iter().map(ep_str).collect();
    println!("{}", parts.join(" "));
    Ok(Value::None)
}
