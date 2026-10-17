0000000000000e40 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e40:	ldp	x8, x9, [x2]
     e44:	subs	x9, x9, x8
     e48:	b.eq	e94 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>  // b.none
     e4c:	asr	x11, x9, #2
     e50:	ldr	x9, [x1]
     e54:	ldr	x10, [x0]
     e58:	cmp	x11, #0x1
     e5c:	csinc	x11, x11, xzr, hi	// hi = pmore
     e60:	nop
     e64:	nop
     e68:	nop
     e6c:	nop
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	ldrsw	x12, [x8], #4
     e84:	subs	x11, x11, #0x1
     e88:	ldr	w12, [x9, x12, lsl #2]
     e8c:	str	w12, [x10], #4
     e90:	b.ne	e80 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>  // b.any
     e94:	ret
