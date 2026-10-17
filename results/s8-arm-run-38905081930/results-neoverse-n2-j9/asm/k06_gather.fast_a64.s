0000000000000e40 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e40:	ldp	x8, x9, [x2]
     e44:	subs	x11, x9, x8
     e48:	b.eq	ea4 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>  // b.none
     e4c:	ldp	x9, x12, [x1]
     e50:	asr	x14, x11, #2
     e54:	ldp	x10, x13, [x0]
     e58:	cmp	x14, #0x1
     e5c:	sub	x11, x12, x9
     e60:	sub	x12, x13, x10
     e64:	asr	x11, x11, #2
     e68:	csinc	x13, x14, xzr, hi	// hi = pmore
     e6c:	asr	x12, x12, #2
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	ldrsw	x14, [x8], #4
     e84:	cmp	x11, x14
     e88:	b.ls	ea8 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x68>  // b.plast
     e8c:	cbz	x12, ea8 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x68>
     e90:	ldr	w14, [x9, x14, lsl #2]
     e94:	subs	x13, x13, #0x1
     e98:	sub	x12, x12, #0x1
     e9c:	str	w14, [x10], #4
     ea0:	b.ne	e80 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>  // b.any
     ea4:	ret
     ea8:	brk	#0x1
