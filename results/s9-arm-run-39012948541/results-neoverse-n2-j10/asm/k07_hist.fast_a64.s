0000000000000e40 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x1]
     e44:	subs	x10, x9, x8
     e48:	b.eq	ea4 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>  // b.none
     e4c:	ldp	x9, x11, [x0]
     e50:	asr	x12, x10, #2
     e54:	cmp	x12, #0x1
     e58:	sub	x10, x11, x9
     e5c:	csinc	x11, x12, xzr, hi	// hi = pmore
     e60:	asr	x10, x10, #2
     e64:	nop
     e68:	nop
     e6c:	nop
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	ldrb	w12, [x8], #4
     e84:	cmp	x10, x12
     e88:	b.ls	ea8 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x68>  // b.plast
     e8c:	lsl	x12, x12, #2
     e90:	subs	x11, x11, #0x1
     e94:	ldr	w13, [x9, x12]
     e98:	add	w13, w13, #0x1
     e9c:	str	w13, [x9, x12]
     ea0:	b.ne	e80 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.any
     ea4:	ret
     ea8:	brk	#0x1
