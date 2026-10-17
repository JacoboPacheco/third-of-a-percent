0000000000000e40 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x0]
     e44:	subs	x11, x9, x8
     e48:	b.eq	eb0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>  // b.none
     e4c:	ldp	x10, x12, [x1]
     e50:	asr	x13, x11, #2
     e54:	mov	x9, xzr
     e58:	cmp	x13, #0x1
     e5c:	sub	x11, x12, x10
     e60:	csinc	x12, x13, xzr, hi	// hi = pmore
     e64:	asr	x11, x11, #2
     e68:	nop
     e6c:	nop
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	cmp	x11, x9
     e84:	b.ls	eb4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>  // b.plast
     e88:	add	x13, x9, #0x1
     e8c:	cmp	x11, x13
     e90:	b.ls	eb4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>  // b.plast
     e94:	add	x13, x10, x9, lsl #2
     e98:	subs	x12, x12, #0x1
     e9c:	add	x9, x9, #0x2
     ea0:	ldp	w14, w13, [x13]
     ea4:	add	w13, w13, w14
     ea8:	str	w13, [x8], #4
     eac:	b.ne	e80 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.any
     eb0:	ret
     eb4:	brk	#0x1
