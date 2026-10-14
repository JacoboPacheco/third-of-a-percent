"""Instruction counts (Cachegrind `Ir`) for one kernel function: instructions, not time.

The run executes `valgrind --tool=cachegrind --cache-sim=no --cachegrind-out-file=<f> <binary> <n> <iters>`
and this module reads <f>. The file format (valgrind 3.x) is plain text:

    events: Ir
    fl=/path/k04_rev.cpp
    fn=kern_k04_rev(std::__1::vector<int, std::__1::allocator<int> >&, ...)
    5 123456
    6 789
    fn=main
    ...
    summary: 1234567

Every `<line> <count>` row after an `fn=` line belongs to that function. The counts of all rows
under every fn= whose name contains the kernel's name are summed. Function names may be
demangled or mangled depending on the valgrind build; matching on the substring kern_<id>
works for both.
"""


def function_ir(text, name):
    """Total Ir attributed to functions whose name contains `name`. Returns an int (0 if absent)."""
    events = None
    total = 0
    in_fn = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("events:"):
            events = line.split(":", 1)[1].split()
            continue
        if line.startswith("fn="):
            in_fn = name in line[3:]
            continue
        if "=" in line.split(" ", 1)[0] or line.startswith(("desc:", "cmd:", "summary:", "totals:", "positions:", "version:", "creator:")):
            continue
        if in_fn:
            parts = line.split()
            if len(parts) < 2:
                continue
            idx = events.index("Ir") if events and "Ir" in events else 0
            # parts[0] is the line number; the event counts follow in the order of `events:`
            try:
                total += int(parts[1 + idx])
            except (IndexError, ValueError):
                continue
    return total


def per_call(text, name, calls):
    """Ir of the kernel function divided by the number of calls, rounded to an integer."""
    if calls < 1:
        raise ValueError("calls must be at least 1")
    return int(round(function_ir(text, name) / calls))
