fn builtin_range(args: &[Value]) -> Result<Value, PyError> {
    if args.is_empty() || args.len() > 3 {
        return rt("TypeError: range() takes 1\u{2013}3 arguments");
    }
    let mut ints = Vec::with_capacity(args.len());
    for a in args {
        match a.as_i64() {
            Some(_) if a.is_number() => ints.push(a.as_i64().unwrap()),
            _ => return rt("TypeError: range() arguments must be integers"),
        }
    }
    let (start, stop, step) = match ints.len() {
        1 => (0, ints[0], 1),
        2 => (ints[0], ints[1], 1),
        3 => (ints[0], ints[1], ints[2]),
        _ => unreachable!(),
    };
    if step == 0 {
        return rt("ValueError: range() arg 3 must not be zero");
    }
    let mut out = Vec::new();
    if step > 0 {
        let mut i = start;
        while i < stop {
            out.push(Value::Int(i));
            i += step;
        }
    } else {
        let mut i = start;
        while i > stop {
            out.push(Value::Int(i));
            i += step;
        }
    }
    Ok(Value::new_list(out))
}
