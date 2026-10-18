0000000000000e28 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e60 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x38>  // b.none
     e34:	asr	x10, x9, #2
     e38:	ldr	x9, [x0]
     e3c:	cmp	x10, #0x1
     e40:	csinc	x10, x10, xzr, hi	// hi = pmore
     e44:	ldrb	w11, [x8], #4
     e48:	subs	x10, x10, #0x1
     e4c:	lsl	x11, x11, #2
     e50:	ldr	w12, [x9, x11]
     e54:	add	w12, w12, #0x1
     e58:	str	w12, [x9, x11]
     e5c:	b.ne	e44 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1c>  // b.any
     e60:	ret
