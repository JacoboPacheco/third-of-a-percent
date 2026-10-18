0000000000000e40 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
     e40:	cbz	x3, fe4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1a4>
     e44:	stp	x22, x21, [sp, #-32]!
     e48:	stp	x20, x19, [sp, #16]
     e4c:	mul	x13, x3, x3
     e50:	ldr	x9, [x2]
     e54:	ldr	x10, [x0]
     e58:	lsl	x11, x3, #2
     e5c:	ldr	x12, [x1]
     e60:	mov	x8, xzr
     e64:	and	x15, x3, #0xfffffffffffffff8
     e68:	add	x16, x9, #0x10
     e6c:	add	x17, x10, #0x10
     e70:	add	x14, x10, x11
     e74:	mov	x18, x10
     e78:	add	x13, x9, x13, lsl #2
     e7c:	b	e94 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x54>
     e80:	add	x8, x8, #0x1
     e84:	add	x17, x17, x11
     e88:	add	x18, x18, x11
     e8c:	cmp	x8, x3
     e90:	b.eq	fdc <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x19c>  // b.none
     e94:	mul	x1, x11, x8
     e98:	mov	x0, xzr
     e9c:	mov	x5, x16
     ea0:	mul	x2, x8, x3
     ea4:	add	x4, x10, x1
     ea8:	add	x1, x14, x1
     eac:	cmp	x4, x13
     eb0:	mov	x4, x9
     eb4:	ccmp	x9, x1, #0x2, cc	// cc = lo, ul, last
     eb8:	add	x1, x12, x2, lsl #2
     ebc:	ccmp	x11, #0x0, #0x8, cs	// cs = hs, nlast
     ec0:	cset	w2, lt	// lt = tstop
     ec4:	b	f14 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xd4>
     ec8:	nop
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
     f00:	add	x0, x0, #0x1
     f04:	add	x5, x5, x11
     f08:	add	x4, x4, x11
     f0c:	cmp	x0, x3
     f10:	b.eq	e80 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>  // b.none
     f14:	cmp	x3, #0x8
     f18:	ldr	w6, [x1, x0, lsl #2]
     f1c:	csinc	w7, w2, wzr, cs	// cs = hs, nlast
     f20:	tbz	w7, #0, f40 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
     f24:	mov	x7, xzr
     f28:	b	fb0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x170>
     f2c:	nop
     f30:	nop
     f34:	nop
     f38:	nop
     f3c:	nop
     f40:	dup	v0.4s, w6
     f44:	mov	x7, x15
     f48:	mov	x19, x17
     f4c:	mov	x20, x5
     f50:	nop
     f54:	nop
     f58:	nop
     f5c:	nop
     f60:	nop
     f64:	nop
     f68:	nop
     f6c:	nop
     f70:	nop
     f74:	nop
     f78:	nop
     f7c:	nop
     f80:	ldp	q1, q4, [x19, #-16]
     f84:	subs	x7, x7, #0x8
     f88:	ldp	q2, q3, [x20, #-16]
     f8c:	add	x20, x20, #0x20
     f90:	mla	v1.4s, v2.4s, v0.4s
     f94:	mla	v4.4s, v3.4s, v0.4s
     f98:	stp	q1, q4, [x19, #-16]
     f9c:	add	x19, x19, #0x20
     fa0:	b.ne	f80 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>  // b.any
     fa4:	cmp	x15, x3
     fa8:	mov	x7, x15
     fac:	b.eq	f00 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>  // b.none
     fb0:	lsl	x20, x7, #2
     fb4:	sub	x7, x3, x7
     fb8:	add	x19, x4, x20
     fbc:	add	x20, x18, x20
     fc0:	ldr	w21, [x19], #4
     fc4:	ldr	w22, [x20]
     fc8:	subs	x7, x7, #0x1
     fcc:	madd	w21, w21, w6, w22
     fd0:	str	w21, [x20], #4
     fd4:	b.ne	fc0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>  // b.any
     fd8:	b	f00 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
     fdc:	ldp	x20, x19, [sp, #16]
     fe0:	ldp	x22, x21, [sp], #32
     fe4:	ret
