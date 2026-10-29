(defn- report-exception [e]
  (if (py-error? e)
    (println (.getMessage ^Throwable e))
    (println (str "\033[91mInternalError\033[0m: " (.getMessage ^Throwable e)))))

(defn -main [& args]
  (if (empty? args)
    (repl)
    (let [show-ast (boolean (some #(= % "--ast") args))
          files (remove #(str/starts-with? % "--") args)]
      (if (empty? files)
        (do (println "Usage: bb core.clj [script.ep] [--ast]")
            (System/exit 1))
        (let [filepath (first files)
              f (java.io.File. ^String filepath)]
          (if-not (.exists f)
            (do (println (str "\033[91mFileNotFoundError\033[0m: No such file: " (pr-str filepath)))
                (System/exit 1))
            (let [source (slurp filepath)]
              (try
                (if show-ast
                  (run-source-with-ast source)
                  (run-source source))
                (catch clojure.lang.ExceptionInfo e (report-exception e) (System/exit 1))
                (catch Exception e (report-exception e) (System/exit 1))))))))))
