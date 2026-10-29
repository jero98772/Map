(defn- next-token! [st]
  (if (and (:at-line-start @st) (zero? (:paren-depth @st)))
    (handle-indentation! st)
    (let [ch (cur st)]
      (cond
        (or (= ch \space) (= ch \tab)) (adv! st)

        (= ch \newline)
        (let [[ln cl] (here st)]
          (adv! st)
          (when (zero? (:paren-depth @st))
            (emit! st :newline "\n" ln cl)
            (swap! st assoc :at-line-start true)))

        (= ch \return) (adv! st)

        (= ch \#) (do (while (not (contains? #{\newline \u0000} (cur st))) (adv! st)))

        (contains? #{\" \'} ch) (read-string-lit! st)
        (digit? ch) (read-number! st)
        (name-start? ch) (read-name! st)
        :else (read-operator! st)))))
