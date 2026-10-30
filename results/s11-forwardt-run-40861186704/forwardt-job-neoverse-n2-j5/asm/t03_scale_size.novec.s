0000000000000e28 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e58 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>  // b.none
     e34:	asr	x10, x9, #2
     e38:	ldr	x9, [x0]
     e3c:	cmp	x10, #0x1
     e40:	csinc	x10, x10, xzr, hi	// hi = pmore
     e44:	ldr	w11, [x8], #4
     e48:	subs	x10, x10, #0x1
     e4c:	lsl	w11, w11, #1
     e50:	str	w11, [x9], #4
     e54:	b.ne	e44 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1c>  // b.any
     e58:	ret
