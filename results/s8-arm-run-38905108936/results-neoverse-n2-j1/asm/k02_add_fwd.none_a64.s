0000000000000e40 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e40:	ldp	x8, x9, [x1]
     e44:	subs	x9, x9, x8
     e48:	b.eq	e98 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>  // b.none
     e4c:	asr	x12, x9, #2
     e50:	ldr	x9, [x2]
     e54:	ldr	x10, [x0]
     e58:	cmp	x12, #0x1
     e5c:	csinc	x11, x12, xzr, hi	// hi = pmore
     e60:	cmp	x12, #0x8
     e64:	b.cs	e9c <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5c>  // b.hs, b.nlast
     e68:	mov	x12, xzr
     e6c:	lsl	x13, x12, #2
     e70:	sub	x11, x11, x12
     e74:	add	x8, x8, x13
     e78:	add	x9, x9, x13
     e7c:	add	x10, x10, x13
     e80:	ldr	w12, [x8], #4
     e84:	subs	x11, x11, #0x1
     e88:	ldr	w13, [x9], #4
     e8c:	add	w12, w13, w12
     e90:	str	w12, [x10], #4
     e94:	b.ne	e80 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>  // b.any
     e98:	ret
     e9c:	sub	x12, x10, x8
     ea0:	cmp	x12, #0x20
     ea4:	mov	x12, xzr
     ea8:	b.cc	e6c <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2c>  // b.lo, b.ul, b.last
     eac:	sub	x13, x10, x9
     eb0:	cmp	x13, #0x20
     eb4:	b.cc	e6c <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2c>  // b.lo, b.ul, b.last
     eb8:	and	x12, x11, #0xfffffffffffffff8
     ebc:	add	x13, x8, #0x10
     ec0:	add	x14, x9, #0x10
     ec4:	add	x15, x10, #0x10
     ec8:	mov	x16, x12
     ecc:	nop
     ed0:	nop
     ed4:	nop
     ed8:	nop
     edc:	nop
     ee0:	nop
     ee4:	nop
     ee8:	nop
     eec:	nop
     ef0:	nop
     ef4:	nop
     ef8:	nop
     efc:	nop
     f00:	ldp	q0, q3, [x14, #-16]
     f04:	subs	x16, x16, #0x8
     f08:	ldp	q1, q2, [x13, #-16]
     f0c:	add	x13, x13, #0x20
     f10:	add	x14, x14, #0x20
     f14:	add	v0.4s, v0.4s, v1.4s
     f18:	add	v1.4s, v3.4s, v2.4s
     f1c:	stp	q0, q1, [x15, #-16]
     f20:	add	x15, x15, #0x20
     f24:	b.ne	f00 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>  // b.any
     f28:	cmp	x11, x12
     f2c:	b.ne	e6c <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2c>  // b.any
     f30:	b	e98 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>
