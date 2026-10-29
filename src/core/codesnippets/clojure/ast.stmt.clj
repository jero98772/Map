(defrecord Assign [target value line])               ; ast.Assign(targets, value)
(defrecord AugAssign [target op value line])         ; ast.AugAssign(target, op, value)
(defrecord ExprStmt [expr line])                     ; ast.Expr(value)
(defrecord Return [value line])                      ; ast.Return(value)
(defrecord If [test body orelse line])               ; ast.If(test, body, orelse)
(defrecord While [test body line])                   ; ast.While(test, body, orelse)
(defrecord For [target iter body line])              ; ast.For(target, iter, body)

(defrecord FuncDef [name params body line])          ; ast.FunctionDef(name, args, body)
