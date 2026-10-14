"""Independent read of the saved objdump of kern_<id> per build: counts packed-SIMD instructions
on xmm/ymm registers (movdqu/movdqa/movups/padd*/psll*/pshufd/shufps/pmull*/punpck*) and ud2 traps.
A build 'has a vector loop' when at least one packed integer arithmetic op is present."""
import re, sys, os, glob
PACKED = re.compile(r'\t(movdq[au]|movup[sd]|movap[sd]|padd[bwdq]|psub[bwdq]|psll[dqw]|psrl[dqw]|pshufd|shufps|pmul\w*|punpck\w*|pmadd\w*|pand|por|pxor)\s.*%[xy]mm')
ARITH = re.compile(r'\t(padd[bwdq]|psll[dqw]|pmul\w*|pmadd\w*|shufps|pshufd)\s')
def read(path):
    lines = open(path).read().splitlines()
    packed = sum(1 for l in lines if PACKED.search(l))
    arith = sum(1 for l in lines if ARITH.search(l) and '%xmm' in l)
    ud2 = sum(1 for l in lines if '\tud2' in l)
    return len(lines), packed, arith, ud2
for d in sys.argv[2:]:
    for k in sys.argv[1].split(','):
        row = [os.path.basename(os.path.dirname(d))[8:28], k]
        for b in ('none', 'fast', 'none_a64', 'fast_a64', 'novec'):
            p = os.path.join(d, f'{k}.{b}.s')
            if os.path.exists(p):
                n, pk, ar, u = read(p); row.append(f'{b}: {n}L pk{pk} ar{ar} ud2:{u}')
        print(' | '.join(row))
