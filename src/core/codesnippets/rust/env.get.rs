pub struct Env {
    pub vars: RefCell<HashMap<String, Value>>,
    pub parent: Option<Rc<Env>>,
}

impl Env {
    pub fn new(parent: Option<Rc<Env>>) -> Rc<Env> {
        Rc::new(Env {
            vars: RefCell::new(HashMap::new()),
            parent,
        })
    }

    pub fn get(&self, name: &str, line: Option<usize>) -> Result<Value, PyError> {
        if let Some(v) = self.vars.borrow().get(name) {
            return Ok(v.clone());
        }
        if let Some(p) = &self.parent {
            return p.get(name, line);
        }
        Err(PyError::Runtime(
            format!("NameError: name '{}' is not defined", name),
            line,
        ))
    }

    /// Always sets in the *current* scope (like Python assignment).
    pub fn set(&self, name: &str, value: Value) {
        self.vars.borrow_mut().insert(name.to_string(), value);
    }

    pub fn owns(&self, name: &str) -> bool {
        if self.vars.borrow().contains_key(name) {
            return true;
        }
        match &self.parent {
            Some(p) => p.owns(name),
            Option::None => false,
        }
    }

    /// Assign to the nearest scope that already owns `name`.
    /// Falls back to the current scope (new variable).
    pub fn assign(&self, name: &str, value: Value) {
        if self.vars.borrow().contains_key(name) {
            self.vars.borrow_mut().insert(name.to_string(), value);
            return;
        }
        if let Some(p) = &self.parent {
            if p.owns(name) {
                p.assign(name, value);
                return;
            }
        }
        self.vars.borrow_mut().insert(name.to_string(), value);
    }
}
