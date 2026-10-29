pub const NAMES: &[&str] = &[
    "print", "len", "range", "int", "float", "str", "bool", "input", "abs", "max", "min", "type",
    "append", "pop",
];

pub fn call(name: &str, args: &[Value]) -> Result<Value, PyError> {
    match name {
        "print" => builtin_print(args),
        "len" => builtin_len(args),
        "range" => builtin_range(args),
        "int" => builtin_int(args),
        "float" => builtin_float(args),
        "str" => builtin_str(args),
        "bool" => builtin_bool(args),
        "input" => builtin_input(args),
        "abs" => builtin_abs(args),
        "max" => builtin_max(args),
        "min" => builtin_min(args),
        "type" => builtin_type(args),
        "append" => builtin_append(args),
        "pop" => builtin_pop(args),
        _ => rt(format!("NameError: name '{}' is not defined", name)),
    }
}
