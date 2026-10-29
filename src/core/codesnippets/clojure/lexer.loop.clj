(defn tokenize! [st]
  (while (< (:pos @st) (src-len st))
    (next-token! st))
  (close-all-indents! st)
  (let [toks (:tokens @st)]
    (when (or (empty? toks) (not (contains? #{:newline :dedent} (:type (last toks)))))
      (emit! st :newline "\n" (:line @st) (:col @st))))
  (emit! st :eof nil (:line @st) (:col @st))
  (:tokens @st))
