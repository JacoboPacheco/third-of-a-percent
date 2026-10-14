import os

import _path  # noqa: F401
import classify

KERNEL_LINES = {
    "k01": ("for (size_t i = 0; i < a.size(); ++i) s += a[i];", None),
    "k04": ("for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;", "reverse"),
    "k05": ("for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i] + a[2 * i + 1];", "strided"),
    "k06": ("for (size_t i = 0; i < idx.size(); ++i) c[i] = a[idx[i]];", "indirect"),
    "k07": ("for (size_t i = 0; i < a.size(); ++i) h[a[i] & 255]++;", "indirect"),
    "k08": ("      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];", "strided"),
}


def test_kernel_loops():
    for kid, (line, want) in KERNEL_LINES.items():
        cls, _ = classify.classify([line], 1)
        if want:
            assert cls == want, (kid, cls)
        else:
            assert cls == "other", (kid, cls)


def test_real_kernel_files_match_the_table():
    kdir = os.path.join(_path.REPO, "kernels")
    if not os.path.isdir(kdir):
        return
    for kid, (line, _) in KERNEL_LINES.items():
        name = [f for f in os.listdir(kdir) if f.startswith(kid)][0]
        with open(os.path.join(kdir, name)) as f:
            src = [x for x in f.read().splitlines() if "// LOOP" in x][0]
        assert src.split("  // LOOP")[0].strip() == line.strip(), kid


def test_other_patterns():
    assert classify.classify(["for (auto it = v.rbegin(); it != v.rend(); ++it) s += *it;"])[0] == "reverse"
    assert classify.classify(["for (int i = 0; i < n; i += step) s += a[i];"])[0] == "strided"
    assert classify.classify(["for (int i = 0; i < n; ++i) out[i] = in[i << 1];"])[0] == "strided"
    assert classify.classify(["for (int i = 0; i < n; ++i) out[i] = in[i + off];"])[0] == "strided"
    assert classify.classify(["for (int i = 0; i < n; ++i) out[i] = in[n - 1 - i];"])[0] == "reverse"
    assert classify.classify(["while (p != end) {", "  if (*p == 0) break;", "  ++p;", "}"]) == \
        ("other", "early exit (break/return or a compound condition)")
    assert classify.classify(["for (auto& x : v) s += x;"]) == ("other", "no subscript (iterator, pointer or range loop)")
    assert classify.classify(["for (; first != last; ++first) *out = *first;"], 1, "libc++")[1] == \
        "loop inside libc++'s own code"
    assert classify.classify([]) == ("other", "source not available")
    # leveldb db/c.cc:117, the one lost loop in the first full census
    assert classify.classify(["    for (int i = 0; i < n; i++) {", "      key_pointers[i] = keys[i].data();",
                              "      key_sizes[i] = keys[i].size();", "    }"], 5) ==         ("other", "forward loop bounded by a variable, not the container's size()")


def test_strings_and_comments_ignored():
    assert classify.classify(['for (int i = 0; i < n; ++i) s += a[i]; // i-- here "[x[y]]"'])[0] == "other"


def test_loop_context():
    lines = ["int f() {", "  for (int i = 0; i < n; ++i) {", "    a[i] = b[i];", "  }", "  return 0;", "}"]
    assert classify.loop_context(lines, 1) == lines[1:4]
    assert classify.loop_context(["for (;;) x[i] = 0;", "next"], 0) == ["for (;;) x[i] = 0;"]
    assert classify.loop_context(["for (int i = 0; i < n; ++i)", "  a[i] = 0;", "next"], 0) == \
        ["for (int i = 0; i < n; ++i)", "  a[i] = 0;"]
