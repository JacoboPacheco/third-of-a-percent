0000000000000e28 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e28:	ldp	x8, x9, [x2]
     e2c:	subs	x11, x9, x8
     e30:	b.eq	e7c <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>  // b.none
     e34:	ldp	x9, x12, [x1]
     e38:	asr	x14, x11, #2
     e3c:	ldp	x10, x13, [x0]
     e40:	cmp	x14, #0x1
     e44:	sub	x11, x12, x9
     e48:	sub	x12, x13, x10
     e4c:	asr	x11, x11, #2
     e50:	csinc	x13, x14, xzr, hi	// hi = pmore
     e54:	asr	x12, x12, #2
     e58:	ldrsw	x14, [x8], #4
     e5c:	cmp	x11, x14
     e60:	b.ls	e80 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>  // b.plast
     e64:	cbz	x12, e80 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>
     e68:	ldr	w14, [x9, x14, lsl #2]
     e6c:	subs	x13, x13, #0x1
     e70:	sub	x12, x12, #0x1
     e74:	str	w14, [x10], #4
     e78:	b.ne	e58 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x30>  // b.any
     e7c:	ret
     e80:	brk	#0x1
