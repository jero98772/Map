        reg("print", a -> {
            StringJoiner sj = new StringJoiner(" ");
            for (Object x : a) sj.add(epStr(x));
            System.out.println(sj);
            return null;
        });
