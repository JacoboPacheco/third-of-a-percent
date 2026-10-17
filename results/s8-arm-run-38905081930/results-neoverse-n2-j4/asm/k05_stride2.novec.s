0000000000000e28 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x0]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e60 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x38>  // b.none
     e34:	asr	x9, x9, #2
     e38:	ldr	x10, [x1]
     e3c:	cmp	x9, #0x1
     e40:	add	x10, x10, #0x4
     e44:	csinc	x9, x9, xzr, hi	// hi = pmore
     e48:	ldp	w11, w12, [x10, #-4]
     e4c:	subs	x9, x9, #0x1
     e50:	add	x10, x10, #0x8
     e54:	add	w11, w12, w11
     e58:	str	w11, [x8], #4
     e5c:	b.ne	e48 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x20>  // b.any
     e60:	ret
