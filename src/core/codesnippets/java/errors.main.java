    static int realMain(String[] args) {
        try {
            if (args.length == 0) {
                repl();
                return 0;
            }

            boolean showAst = Arrays.asList(args).contains("--ast");
            List<String> files = new ArrayList<>();
            for (String a : args) if (!a.startsWith("--")) files.add(a);

            if (files.isEmpty()) {
                System.out.println("Usage: java Py.java [script] [--ast]");
                return 1;
            }

            String filepath = files.get(0);
            Path path = Path.of(filepath);
            if (!Files.exists(path)) {
                System.out.println("\033[91mFileNotFoundError\033[0m: No such file: " + pyRepr(filepath));
                return 1;
            }

            String source = Files.readString(path, StandardCharsets.UTF_8);
            if (showAst) runSourceWithAst(source);
            else runSource(source, null);
            return 0;
        } catch (PyError e) {
            System.out.println(e);
            return 1;
        } catch (Exception e) {
            System.out.println("\033[91mInternalError\033[0m: " + e);
            return 1;
        }
    }
