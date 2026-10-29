(defrecord Env [vars parent])

(defn new-env
  ([] (->Env (atom {}) nil))
  ([parent] (->Env (atom {}) parent)))

(defn env-owns? [env nm]
  (or (contains? @(:vars env) nm)
      (and (:parent env) (env-owns? (:parent env) nm))))

(defn env-get
  "Look a name up the scope chain; raises NameError if not found."
  [env nm line]
  (cond
    (contains? @(:vars env) nm) (get @(:vars env) nm)
    (:parent env) (env-get (:parent env) nm line)
    :else (throw (runtime-error (str "NameError: name '" nm "' is not defined") line))))

(defn env-set!
  "Always sets in the *current* scope (like Python assignment)."
  [env nm value]
  (swap! (:vars env) assoc nm value))

(defn env-assign!
  "Assign to the nearest scope that already owns *name*, else the current scope."
  [env nm value line]
  (cond
    (contains? @(:vars env) nm) (swap! (:vars env) assoc nm value)
    (and (:parent env) (env-owns? (:parent env) nm)) (env-assign! (:parent env) nm value line)
    :else (swap! (:vars env) assoc nm value)))
