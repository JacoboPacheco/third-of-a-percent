0000000000000e28 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e80 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>  // b.none
     e34:	asr	x12, x9, #2
     e38:	ldr	x9, [x2]
     e3c:	ldr	x10, [x0]
     e40:	cmp	x12, #0x1
     e44:	csinc	x11, x12, xzr, hi	// hi = pmore
     e48:	cmp	x12, #0x8
     e4c:	b.cs	e84 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5c>  // b.hs, b.nlast
     e50:	mov	x12, xzr
     e54:	lsl	x13, x12, #2
     e58:	sub	x11, x11, x12
     e5c:	add	x8, x8, x13
     e60:	add	x9, x9, x13
     e64:	add	x10, x10, x13
     e68:	ldr	w12, [x8], #4
     e6c:	subs	x11, x11, #0x1
     e70:	ldr	w13, [x9], #4
     e74:	add	w12, w13, w12
     e78:	str	w12, [x10], #4
     e7c:	b.ne	e68 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>  // b.any
     e80:	ret
     e84:	sub	x12, x10, x8
     e88:	cmp	x12, #0x20
     e8c:	mov	x12, xzr
     e90:	b.cc	e54 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2c>  // b.lo, b.ul, b.last
     e94:	sub	x13, x10, x9
     e98:	cmp	x13, #0x20
     e9c:	b.cc	e54 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2c>  // b.lo, b.ul, b.last
     ea0:	and	x12, x11, #0xfffffffffffffff8
     ea4:	add	x13, x8, #0x10
     ea8:	add	x14, x9, #0x10
     eac:	add	x15, x10, #0x10
     eb0:	mov	x16, x12
     eb4:	ldp	q0, q3, [x14, #-16]
     eb8:	subs	x16, x16, #0x8
     ebc:	ldp	q1, q2, [x13, #-16]
     ec0:	add	x13, x13, #0x20
     ec4:	add	x14, x14, #0x20
     ec8:	add	v0.4s, v0.4s, v1.4s
     ecc:	add	v1.4s, v3.4s, v2.4s
     ed0:	stp	q0, q1, [x15, #-16]
     ed4:	add	x15, x15, #0x20
     ed8:	b.ne	eb4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x8c>  // b.any
     edc:	cmp	x11, x12
     ee0:	b.ne	e54 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2c>  // b.any
     ee4:	b	e80 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>
