// Layout sweep wrapper: PAD_BYTES bytes of 0x90 filler at the start of this object's .text, then the
// unchanged kernel source (KERNEL_SRC, e.g. "kernels/k02_add_fwd.cpp"). Module-level asm is emitted before
// any function, so the filler sits in front of the kernel function; with -falign-functions=1 the function
// starts right after it, and the hot loop moves by exactly PAD_BYTES. Verified from the disassembly by
// layout-sweep/sweep.py (never assumed). Nothing here is executed: the filler is never reached.
#ifndef PAD_BYTES
#define PAD_BYTES 0
#endif
#define LS_STR2(x) #x
#define LS_STR(x) LS_STR2(x)
#if PAD_BYTES > 0
asm(".text\n\t.skip " LS_STR(PAD_BYTES) ", 0x90\n");
#endif
#include KERNEL_SRC
