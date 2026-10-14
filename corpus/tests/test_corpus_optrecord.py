import _path  # noqa: F401
import optrecord

SAMPLE = """--- !Passed
Pass:            loop-vectorize
Name:            Vectorized
DebugLoc:        { File: 'src/a.cpp', Line: 5, Column: 3 }
Function:        _Z3fooRNSt3__16vectorIiNS_9allocatorIiEEEE
Args:
  - String:          'vectorized loop (vectorization width: '
  - VectorizationFactor: '4'
  - String:          ', interleaved count: '
  - InterleaveCount: '2'
  - String:          ')'
...
--- !Analysis
Pass:            loop-vectorize
Name:            CantComputeNumberOfIterations
DebugLoc:        { File: '/usr/lib/llvm-18/bin/../include/c++/v1/__algorithm/copy.h', Line: 41, Column: 5 }
Function:        '_Z3barv'
Args:
  - String:          'loop not vectorized: '
  - String:          could not determine number of loop iterations
...
--- !Missed
Pass:            loop-vectorize
Name:            MissedDetails
DebugLoc:        { File: 'it''s.cpp', Line: 9, Column: 1 }
Function:        _Z3bazv
Args:
  - String:          loop not vectorized
  - Callee:          foo
    DebugLoc:        { File: 'x.h', Line: 1, Column: 1 }
...
--- !Passed
Pass:            inline
Name:            Inlined
Function:        _Z3bazv
Args:
  - String:          inlined
...
"""


def test_parse_fields_and_message():
    recs = optrecord.parse(SAMPLE)
    assert len(recs) == 4
    r = recs[0]
    assert r["kind"] == "Passed" and r["name"] == "Vectorized"
    assert r["loc"] == {"file": "src/a.cpp", "line": 5, "column": 3}
    assert r["function"].startswith("_Z3foo")
    assert r["message"] == "vectorized loop (vectorization width: 4, interleaved count: 2)"
    assert optrecord.is_vectorized(r)


def test_quoted_function_plain_args_and_escapes():
    recs = optrecord.parse(SAMPLE)
    assert recs[1]["function"] == "_Z3barv"
    assert recs[1]["message"] == "loop not vectorized: could not determine number of loop iterations"
    assert recs[2]["loc"]["file"] == "it's.cpp"
    assert recs[2]["message"] == "loop not vectorized" + "foo"
    assert not optrecord.is_vectorized(recs[1])


def test_filter_and_missing_loc():
    recs = optrecord.loop_vectorize(optrecord.parse(SAMPLE))
    assert len(recs) == 3
    assert optrecord.parse(SAMPLE)[3]["loc"] is None


def test_continuation_line_joined():
    text = "--- !Missed\nPass: loop-vectorize\nName: X\nArgs:\n  - String: 'a long'\n    continued here\n...\n"
    r = optrecord.parse(text)[0]
    assert r["message"] == "a long continued here"


def test_wrapped_debugloc_is_joined():
    # LLVM wraps a long flow mapping over two lines (seen in the first full census run)
    text = ("--- !Passed\nPass:            loop-vectorize\nName:            Vectorized\n"
            "DebugLoc:        { File: '/usr/lib/llvm-18/bin/../include/c++/v1/__memory/uninitialized_algorithms.h', \n"
            "                   Line: 96, Column: 5 }\n"
            "Function:        _Z1fv\nArgs:\n  - String:          'vectorized '\n  - String:          ''\n"
            "  - String:          'loop (vectorization width: '\n  - VectorizationFactor: '2'\n"
            "  - String:          ', interleaved count: '\n  - InterleaveCount: '2'\n  - String: ')'\n...\n")
    r = optrecord.parse(text)[0]
    assert r["loc"] == {"file": "/usr/lib/llvm-18/bin/../include/c++/v1/__memory/uninitialized_algorithms.h",
                        "line": 96, "column": 5}
    assert r["function"] == "_Z1fv"
    assert r["message"] == "vectorized loop (vectorization width: 2, interleaved count: 2)"
