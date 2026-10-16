"""Helpers to read the optimizer-pipeline answers saved in raw/pipe_*.json.gz (offline)."""
import re

import ce



def passes(name):
    rec = ce.load(name)
    res = rec["response"]["optPipelineOutput"]["results"]
    key = [k for k in res if "kern_" in k][0]
    return res[key]


def pass_name(p):
    return p["name"].split(" on ")[0]


def ir_text(lines):
    return "\n".join(x["text"] if isinstance(x, dict) else x for x in lines)


def strip_debug(text):
    """Drop debug intrinsics and metadata attachments so two IR dumps can be compared by eye."""
    out = []
    for ln in text.splitlines():
        if "@llvm.dbg." in ln or ln.lstrip().startswith("#dbg_"):
            continue
        ln = re.sub(r", !(dbg|tbaa|llvm\.loop|prof|noundef|nonnull|range|align)[ ]![0-9]+", "", ln)
        ln = re.sub(r" !dbg ![0-9]+", "", ln)
        ln = re.sub(r"(\{)? ?!dbg ![0-9]+ \{", " {", ln)
        out.append(ln.rstrip())
    return "\n".join(out)


def find(name, pass_prefix, nth=0):
    """Index of the nth pass whose name starts with pass_prefix."""
    ps = passes(name)
    idx = [i for i, p in enumerate(ps) if pass_name(p).startswith(pass_prefix)]
    return ps, idx[nth] if len(idx) > nth else None
