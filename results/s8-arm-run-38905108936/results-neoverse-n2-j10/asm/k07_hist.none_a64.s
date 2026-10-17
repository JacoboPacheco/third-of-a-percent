0000000000000e40 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x1]
     e44:	subs	x9, x9, x8
     e48:	b.eq	e9c <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5c>  // b.none
     e4c:	asr	x10, x9, #2
     e50:	ldr	x9, [x0]
     e54:	cmp	x10, #0x1
     e58:	csinc	x10, x10, xzr, hi	// hi = pmore
     e5c:	nop
     e60:	nop
     e64:	nop
     e68:	nop
     e6c:	nop
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	ldrb	w11, [x8], #4
     e84:	subs	x10, x10, #0x1
     e88:	lsl	x11, x11, #2
     e8c:	ldr	w12, [x9, x11]
     e90:	add	w12, w12, #0x1
     e94:	str	w12, [x9, x11]
     e98:	b.ne	e80 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.any
     e9c:	ret
