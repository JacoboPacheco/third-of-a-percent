0000000000000e28 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
     e28:	ldp	x8, x9, [x0]
     e2c:	mov	x0, xzr
     e30:	subs	x9, x9, x8
     e34:	b.eq	e54 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2c>  // b.none
     e38:	asr	x9, x9, #2
     e3c:	cmp	x9, #0x1
     e40:	csinc	x9, x9, xzr, hi	// hi = pmore
     e44:	ldrsw	x10, [x8], #4
     e48:	subs	x9, x9, #0x1
     e4c:	add	x0, x0, x10
     e50:	b.ne	e44 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x1c>  // b.any
     e54:	ret
