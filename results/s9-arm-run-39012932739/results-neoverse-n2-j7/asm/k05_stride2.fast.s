0000000000000e28 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x0]
     e2c:	subs	x11, x9, x8
     e30:	b.eq	e80 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x58>  // b.none
     e34:	ldp	x10, x12, [x1]
     e38:	asr	x13, x11, #2
     e3c:	mov	x9, xzr
     e40:	cmp	x13, #0x1
     e44:	sub	x11, x12, x10
     e48:	csinc	x12, x13, xzr, hi	// hi = pmore
     e4c:	asr	x11, x11, #2
     e50:	cmp	x11, x9
     e54:	b.ls	e84 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5c>  // b.plast
     e58:	add	x13, x9, #0x1
     e5c:	cmp	x11, x13
     e60:	b.ls	e84 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5c>  // b.plast
     e64:	add	x13, x10, x9, lsl #2
     e68:	subs	x12, x12, #0x1
     e6c:	add	x9, x9, #0x2
     e70:	ldp	w14, w13, [x13]
     e74:	add	w13, w13, w14
     e78:	str	w13, [x8], #4
     e7c:	b.ne	e50 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x28>  // b.any
     e80:	ret
     e84:	brk	#0x1
