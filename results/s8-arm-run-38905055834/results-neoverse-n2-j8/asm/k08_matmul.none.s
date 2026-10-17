0000000000000e28 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
     e28:	cbz	x3, f50 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x128>
     e2c:	stp	x22, x21, [sp, #-32]!
     e30:	stp	x20, x19, [sp, #16]
     e34:	mul	x13, x3, x3
     e38:	ldr	x9, [x2]
     e3c:	ldr	x10, [x0]
     e40:	lsl	x11, x3, #2
     e44:	ldr	x12, [x1]
     e48:	mov	x8, xzr
     e4c:	and	x15, x3, #0xfffffffffffffff8
     e50:	add	x16, x9, #0x10
     e54:	add	x17, x10, #0x10
     e58:	add	x14, x10, x11
     e5c:	mov	x18, x10
     e60:	add	x13, x9, x13, lsl #2
     e64:	b	e7c <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x54>
     e68:	add	x8, x8, #0x1
     e6c:	add	x17, x17, x11
     e70:	add	x18, x18, x11
     e74:	cmp	x8, x3
     e78:	b.eq	f48 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x120>  // b.none
     e7c:	mul	x1, x11, x8
     e80:	mov	x0, xzr
     e84:	mov	x5, x16
     e88:	mul	x2, x8, x3
     e8c:	add	x4, x10, x1
     e90:	add	x1, x14, x1
     e94:	cmp	x4, x13
     e98:	mov	x4, x9
     e9c:	ccmp	x9, x1, #0x2, cc	// cc = lo, ul, last
     ea0:	add	x1, x12, x2, lsl #2
     ea4:	ccmp	x11, #0x0, #0x8, cs	// cs = hs, nlast
     ea8:	cset	w2, lt	// lt = tstop
     eac:	b	ec4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x9c>
     eb0:	add	x0, x0, #0x1
     eb4:	add	x5, x5, x11
     eb8:	add	x4, x4, x11
     ebc:	cmp	x0, x3
     ec0:	b.eq	e68 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>  // b.none
     ec4:	cmp	x3, #0x8
     ec8:	ldr	w6, [x1, x0, lsl #2]
     ecc:	csinc	w7, w2, wzr, cs	// cs = hs, nlast
     ed0:	tbz	w7, #0, edc <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xb4>
     ed4:	mov	x7, xzr
     ed8:	b	f1c <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf4>
     edc:	dup	v0.4s, w6
     ee0:	mov	x7, x15
     ee4:	mov	x19, x17
     ee8:	mov	x20, x5
     eec:	ldp	q1, q4, [x19, #-16]
     ef0:	subs	x7, x7, #0x8
     ef4:	ldp	q2, q3, [x20, #-16]
     ef8:	add	x20, x20, #0x20
     efc:	mla	v1.4s, v2.4s, v0.4s
     f00:	mla	v4.4s, v3.4s, v0.4s
     f04:	stp	q1, q4, [x19, #-16]
     f08:	add	x19, x19, #0x20
     f0c:	b.ne	eec <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc4>  // b.any
     f10:	cmp	x15, x3
     f14:	mov	x7, x15
     f18:	b.eq	eb0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x88>  // b.none
     f1c:	lsl	x20, x7, #2
     f20:	sub	x7, x3, x7
     f24:	add	x19, x4, x20
     f28:	add	x20, x18, x20
     f2c:	ldr	w21, [x19], #4
     f30:	ldr	w22, [x20]
     f34:	subs	x7, x7, #0x1
     f38:	madd	w21, w21, w6, w22
     f3c:	str	w21, [x20], #4
     f40:	b.ne	f2c <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x104>  // b.any
     f44:	b	eb0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x88>
     f48:	ldp	x20, x19, [sp, #16]
     f4c:	ldp	x22, x21, [sp], #32
     f50:	ret
