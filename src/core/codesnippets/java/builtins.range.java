        reg("range", a -> {
            if (a.isEmpty() || a.size() > 3) throw rt("TypeError: range() takes 1-3 arguments");
            long[] n = new long[a.size()];
            for (int i = 0; i < n.length; i++) {
                if (!isNum(a.get(i))) throw rt("TypeError: range() arguments must be integers");
                n[i] = toLong(a.get(i));
            }
            long start = 0, stop, step = 1;
            if (n.length == 1) stop = n[0];
            else { start = n[0]; stop = n[1]; if (n.length == 3) step = n[2]; }
            if (step == 0) throw rt("ValueError: range() arg 3 must not be zero");
            List<Object> out = new ArrayList<>();
            if (step > 0) for (long i = start; i < stop; i += step) out.add(i);
            else for (long i = start; i > stop; i += step) out.add(i);
            return out;
        });
