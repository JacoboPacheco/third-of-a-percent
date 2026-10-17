0000000000000e28 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
     e28:	sub	sp, sp, #0x70
     e2c:	stp	x29, x30, [sp, #16]
     e30:	stp	x28, x27, [sp, #32]
     e34:	stp	x26, x25, [sp, #48]
     e38:	stp	x24, x23, [sp, #64]
     e3c:	stp	x22, x21, [sp, #80]
     e40:	stp	x20, x19, [sp, #96]
     e44:	cbz	x3, 1028 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
     e48:	ldp	x11, x12, [x1]
     e4c:	lsl	x13, x3, #2
     e50:	mov	x8, xzr
     e54:	mov	x9, xzr
     e58:	mov	x10, xzr
     e5c:	sub	x14, x3, #0x1
     e60:	mov	w15, #0x10                  	// #16
     e64:	str	x2, [sp, #8]
     e68:	sub	x12, x12, x11
     e6c:	asr	x12, x12, #2
     e70:	ldp	x5, x7, [x2]
     e74:	mul	x4, x10, x3
     e78:	mov	x17, xzr
     e7c:	mov	x18, xzr
     e80:	mov	x1, xzr
     e84:	mul	x6, x13, x10
     e88:	mov	x2, x10
     e8c:	sub	x7, x7, x5
     e90:	add	x19, x5, #0x4
     e94:	add	x20, x5, #0x10
     e98:	asr	x7, x7, #2
     e9c:	mov	x21, x5
     ea0:	mul	x25, x1, x3
     ea4:	cmp	x7, x18
     ea8:	add	x23, x1, x4
     eac:	csel	x26, x7, x18, hi	// hi = pmore
     eb0:	subs	x22, x7, x25
     eb4:	csel	x29, xzr, x22, cc	// cc = lo, ul, last
     eb8:	cmp	x12, x23
     ebc:	b.ls	1048 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x220>  // b.plast
     ec0:	ldp	x24, x22, [x0]
     ec4:	subs	x25, x7, x25
     ec8:	csel	x25, xzr, x25, cc	// cc = lo, ul, last
     ecc:	ldr	w23, [x11, x23, lsl #2]
     ed0:	sub	x22, x22, x24
     ed4:	asr	x22, x22, #2
     ed8:	cmp	x22, x4
     edc:	csel	x27, x22, x4, hi	// hi = pmore
     ee0:	sub	x27, x27, x4
     ee4:	cmp	x27, x14
     ee8:	csel	x28, x27, x14, cc	// cc = lo, ul, last
     eec:	cmp	x28, x25
     ef0:	csel	x25, x28, x25, cc	// cc = lo, ul, last
     ef4:	add	x28, x25, #0x1
     ef8:	mov	x25, xzr
     efc:	cmp	x28, #0x8
     f00:	b.ls	fb0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x188>  // b.plast
     f04:	cmp	x22, x4
     f08:	mul	x30, x13, x1
     f0c:	add	x16, x24, x6
     f10:	csel	x25, x22, x4, hi	// hi = pmore
     f14:	sub	x25, x25, x4
     f18:	cmp	x25, x14
     f1c:	csel	x25, x25, x14, cc	// cc = lo, ul, last
     f20:	cmp	x25, x29
     f24:	csel	x25, x25, x29, cc	// cc = lo, ul, last
     f28:	add	x29, x19, x30
     f2c:	lsl	x25, x25, #2
     f30:	add	x10, x16, x25
     f34:	add	x25, x29, x25
     f38:	add	x29, x5, x30
     f3c:	add	x10, x10, #0x4
     f40:	cmp	x16, x25
     f44:	ccmp	x29, x10, #0x2, cc	// cc = lo, ul, last
     f48:	b.cc	fac <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x184>  // b.lo, b.ul, b.last
     f4c:	add	x10, x26, x17
     f50:	ands	x16, x28, #0x7
     f54:	mov	w25, #0x8                   	// #8
     f58:	csel	x16, x25, x16, eq	// eq = none
     f5c:	cmp	x27, x10
     f60:	dup	v0.4s, w23
     f64:	csel	x10, x27, x10, cc	// cc = lo, ul, last
     f68:	sub	x25, x28, x16
     f6c:	add	x27, x24, x15
     f70:	cmp	x10, x14
     f74:	mov	x28, x20
     f78:	csel	x10, x10, x14, cc	// cc = lo, ul, last
     f7c:	sub	x10, x10, x16
     f80:	add	x26, x10, #0x1
     f84:	ldp	q1, q4, [x27, #-16]
     f88:	subs	x26, x26, #0x8
     f8c:	ldp	q2, q3, [x28, #-16]
     f90:	add	x28, x28, #0x20
     f94:	mla	v1.4s, v2.4s, v0.4s
     f98:	mla	v4.4s, v3.4s, v0.4s
     f9c:	stp	q1, q4, [x27, #-16]
     fa0:	add	x27, x27, #0x20
     fa4:	b.ne	f84 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15c>  // b.any
     fa8:	b	fb0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x188>
     fac:	mov	x25, xzr
     fb0:	add	x24, x24, x9
     fb4:	add	x10, x18, x25
     fb8:	cmp	x7, x10
     fbc:	b.ls	1048 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x220>  // b.plast
     fc0:	add	x10, x8, x25
     fc4:	cmp	x22, x10
     fc8:	b.ls	1048 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x220>  // b.plast
     fcc:	lsl	x10, x25, #2
     fd0:	add	x25, x25, #0x1
     fd4:	cmp	x3, x25
     fd8:	ldr	w16, [x21, x10]
     fdc:	ldr	w26, [x24, x10]
     fe0:	madd	w16, w16, w23, w26
     fe4:	str	w16, [x24, x10]
     fe8:	b.ne	fb4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x18c>  // b.any
     fec:	add	x1, x1, #0x1
     ff0:	add	x18, x18, x3
     ff4:	sub	x17, x17, x3
     ff8:	cmp	x1, x3
     ffc:	add	x20, x20, x13
    1000:	add	x21, x21, x13
    1004:	b.ne	ea0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x78>  // b.any
    1008:	mov	x10, x2
    100c:	add	x15, x15, x13
    1010:	add	x9, x9, x13
    1014:	add	x10, x2, #0x1
    1018:	ldr	x2, [sp, #8]
    101c:	add	x8, x8, x3
    1020:	cmp	x10, x3
    1024:	b.ne	e70 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x48>  // b.any
    1028:	ldp	x20, x19, [sp, #96]
    102c:	ldp	x22, x21, [sp, #80]
    1030:	ldp	x24, x23, [sp, #64]
    1034:	ldp	x26, x25, [sp, #48]
    1038:	ldp	x28, x27, [sp, #32]
    103c:	ldp	x29, x30, [sp, #16]
    1040:	add	sp, sp, #0x70
    1044:	ret
    1048:	brk	#0x1
