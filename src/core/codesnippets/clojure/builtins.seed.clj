(defn new-interpreter []
  (let [globals (new-env)]
    (doseq [[nm f] builtins] (env-set! globals nm f))
    {:globals globals}))
