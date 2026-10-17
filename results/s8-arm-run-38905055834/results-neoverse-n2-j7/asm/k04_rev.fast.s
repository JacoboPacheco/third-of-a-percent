0000000000000e28 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x12, x8, [x1]
     e2c:	subs	x8, x8, x12
     e30:	b.eq	e70 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.none
     e34:	ldp	x11, x9, [x0]
     e38:	asr	x10, x8, #2
     e3c:	sub	x12, x12, #0x4
     e40:	sub	x8, x9, x11
     e44:	sub	x9, x10, #0x1
     e48:	sub	x11, x11, #0x4
     e4c:	asr	x8, x8, #2
     e50:	cmp	x9, x8
     e54:	b.cs	e74 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4c>  // b.hs, b.nlast
     e58:	lsl	x13, x10, #2
     e5c:	subs	x10, x10, #0x1
     e60:	ldr	w14, [x12, x13]
     e64:	lsl	w14, w14, #1
     e68:	str	w14, [x11, x13]
     e6c:	b.ne	e50 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x28>  // b.any
     e70:	ret
     e74:	brk	#0x1
