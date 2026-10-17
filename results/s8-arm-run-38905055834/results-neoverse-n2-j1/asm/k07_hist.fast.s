0000000000000e28 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x10, x9, x8
     e30:	b.eq	e70 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.none
     e34:	ldp	x9, x11, [x0]
     e38:	asr	x12, x10, #2
     e3c:	cmp	x12, #0x1
     e40:	sub	x10, x11, x9
     e44:	csinc	x11, x12, xzr, hi	// hi = pmore
     e48:	asr	x10, x10, #2
     e4c:	ldrb	w12, [x8], #4
     e50:	cmp	x10, x12
     e54:	b.ls	e74 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4c>  // b.plast
     e58:	lsl	x12, x12, #2
     e5c:	subs	x11, x11, #0x1
     e60:	ldr	w13, [x9, x12]
     e64:	add	w13, w13, #0x1
     e68:	str	w13, [x9, x12]
     e6c:	b.ne	e4c <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x24>  // b.any
     e70:	ret
     e74:	brk	#0x1
