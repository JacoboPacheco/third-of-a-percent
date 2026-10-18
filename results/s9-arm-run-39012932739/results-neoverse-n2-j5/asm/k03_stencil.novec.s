0000000000000e28 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x9, x8, [x1]
     e2c:	sub	x8, x8, x9
     e30:	asr	x8, x8, #2
     e34:	cmp	x8, #0x3
     e38:	b.cc	e68 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.lo, b.ul, b.last
     e3c:	ldr	x10, [x0]
     e40:	sub	x8, x8, #0x2
     e44:	add	x9, x9, #0x4
     e48:	add	x10, x10, #0x4
     e4c:	ldp	w11, w12, [x9, #-4]
     e50:	ldr	w13, [x9, #4]!
     e54:	subs	x8, x8, #0x1
     e58:	add	w11, w12, w11
     e5c:	add	w11, w11, w13
     e60:	str	w11, [x10], #4
     e64:	b.ne	e4c <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x24>  // b.any
     e68:	ret
