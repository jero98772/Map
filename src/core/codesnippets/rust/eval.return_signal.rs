pub enum Flow {
    Error(PyError),
    Return(Value),
}

impl From<PyError> for Flow {
    fn from(e: PyError) -> Self {
        Flow::Error(e)
    }
}
