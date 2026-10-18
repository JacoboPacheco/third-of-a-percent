0000000000000e40 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x12, x8, [x1]
     e44:	subs	x8, x8, x12
     e48:	b.eq	ea0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>  // b.none
     e4c:	ldp	x11, x9, [x0]
     e50:	asr	x10, x8, #2
     e54:	sub	x12, x12, #0x4
     e58:	sub	x8, x9, x11
     e5c:	sub	x9, x10, #0x1
     e60:	sub	x11, x11, #0x4
     e64:	asr	x8, x8, #2
     e68:	nop
     e6c:	nop
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	cmp	x9, x8
     e84:	b.cs	ea4 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>  // b.hs, b.nlast
     e88:	lsl	x13, x10, #2
     e8c:	subs	x10, x10, #0x1
     e90:	ldr	w14, [x12, x13]
     e94:	lsl	w14, w14, #1
     e98:	str	w14, [x11, x13]
     e9c:	b.ne	e80 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.any
     ea0:	ret
     ea4:	brk	#0x1
