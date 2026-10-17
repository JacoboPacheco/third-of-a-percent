0000000000000e28 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x9, x8, [x1]
     e2c:	subs	x8, x8, x9
     e30:	b.eq	e5c <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x34>  // b.none
     e34:	ldr	x11, [x0]
     e38:	asr	x10, x8, #2
     e3c:	sub	x9, x9, #0x4
     e40:	sub	x8, x11, #0x4
     e44:	lsl	x11, x10, #2
     e48:	subs	x10, x10, #0x1
     e4c:	ldr	w12, [x9, x11]
     e50:	lsl	w12, w12, #1
     e54:	str	w12, [x8, x11]
     e58:	b.ne	e44 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1c>  // b.any
     e5c:	ret
