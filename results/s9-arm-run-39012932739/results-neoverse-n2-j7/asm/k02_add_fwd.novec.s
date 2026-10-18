0000000000000e28 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e60 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x38>  // b.none
     e34:	asr	x11, x9, #2
     e38:	ldr	x9, [x2]
     e3c:	ldr	x10, [x0]
     e40:	cmp	x11, #0x1
     e44:	csinc	x11, x11, xzr, hi	// hi = pmore
     e48:	ldr	w12, [x8], #4
     e4c:	subs	x11, x11, #0x1
     e50:	ldr	w13, [x9], #4
     e54:	add	w12, w13, w12
     e58:	str	w12, [x10], #4
     e5c:	b.ne	e48 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x20>  // b.any
     e60:	ret
