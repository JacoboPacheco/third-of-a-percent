0000000000000e40 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
     e40:	sub	sp, sp, #0x70
     e44:	stp	x29, x30, [sp, #16]
     e48:	stp	x28, x27, [sp, #32]
     e4c:	stp	x26, x25, [sp, #48]
     e50:	stp	x24, x23, [sp, #64]
     e54:	stp	x22, x21, [sp, #80]
     e58:	stp	x20, x19, [sp, #96]
     e5c:	cbz	x3, 10b4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x274>
     e60:	ldp	x11, x12, [x1]
     e64:	lsl	x13, x3, #2
     e68:	mov	x8, xzr
     e6c:	mov	x9, xzr
     e70:	mov	x10, xzr
     e74:	sub	x14, x3, #0x1
     e78:	mov	w15, #0x10                  	// #16
     e7c:	str	x2, [sp, #8]
     e80:	sub	x12, x12, x11
     e84:	asr	x12, x12, #2
     e88:	ldp	x5, x7, [x2]
     e8c:	mul	x4, x10, x3
     e90:	mov	x17, xzr
     e94:	mov	x18, xzr
     e98:	mov	x1, xzr
     e9c:	mul	x6, x13, x10
     ea0:	mov	x2, x10
     ea4:	sub	x7, x7, x5
     ea8:	add	x19, x5, #0x4
     eac:	add	x20, x5, #0x10
     eb0:	asr	x7, x7, #2
     eb4:	mov	x21, x5
     eb8:	nop
     ebc:	nop
     ec0:	mul	x25, x1, x3
     ec4:	cmp	x7, x18
     ec8:	add	x23, x1, x4
     ecc:	csel	x26, x7, x18, hi	// hi = pmore
     ed0:	subs	x22, x7, x25
     ed4:	csel	x29, xzr, x22, cc	// cc = lo, ul, last
     ed8:	cmp	x12, x23
     edc:	b.ls	10d4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>  // b.plast
     ee0:	ldp	x24, x22, [x0]
     ee4:	subs	x25, x7, x25
     ee8:	csel	x25, xzr, x25, cc	// cc = lo, ul, last
     eec:	ldr	w23, [x11, x23, lsl #2]
     ef0:	sub	x22, x22, x24
     ef4:	asr	x22, x22, #2
     ef8:	cmp	x22, x4
     efc:	csel	x27, x22, x4, hi	// hi = pmore
     f00:	sub	x27, x27, x4
     f04:	cmp	x27, x14
     f08:	csel	x28, x27, x14, cc	// cc = lo, ul, last
     f0c:	cmp	x28, x25
     f10:	csel	x25, x28, x25, cc	// cc = lo, ul, last
     f14:	add	x28, x25, #0x1
     f18:	mov	x25, xzr
     f1c:	cmp	x28, #0x8
     f20:	b.ls	1004 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c4>  // b.plast
     f24:	cmp	x22, x4
     f28:	mul	x30, x13, x1
     f2c:	add	x16, x24, x6
     f30:	csel	x25, x22, x4, hi	// hi = pmore
     f34:	sub	x25, x25, x4
     f38:	cmp	x25, x14
     f3c:	csel	x25, x25, x14, cc	// cc = lo, ul, last
     f40:	cmp	x25, x29
     f44:	csel	x25, x25, x29, cc	// cc = lo, ul, last
     f48:	add	x29, x19, x30
     f4c:	lsl	x25, x25, #2
     f50:	add	x10, x16, x25
     f54:	add	x25, x29, x25
     f58:	add	x29, x5, x30
     f5c:	add	x10, x10, #0x4
     f60:	cmp	x16, x25
     f64:	ccmp	x29, x10, #0x2, cc	// cc = lo, ul, last
     f68:	b.cc	1000 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>  // b.lo, b.ul, b.last
     f6c:	add	x10, x26, x17
     f70:	ands	x16, x28, #0x7
     f74:	mov	w25, #0x8                   	// #8
     f78:	csel	x16, x25, x16, eq	// eq = none
     f7c:	cmp	x27, x10
     f80:	dup	v0.4s, w23
     f84:	csel	x10, x27, x10, cc	// cc = lo, ul, last
     f88:	sub	x25, x28, x16
     f8c:	add	x27, x24, x15
     f90:	cmp	x10, x14
     f94:	mov	x28, x20
     f98:	csel	x10, x10, x14, cc	// cc = lo, ul, last
     f9c:	sub	x10, x10, x16
     fa0:	add	x26, x10, #0x1
     fa4:	nop
     fa8:	nop
     fac:	nop
     fb0:	nop
     fb4:	nop
     fb8:	nop
     fbc:	nop
     fc0:	ldp	q1, q4, [x27, #-16]
     fc4:	subs	x26, x26, #0x8
     fc8:	ldp	q2, q3, [x28, #-16]
     fcc:	add	x28, x28, #0x20
     fd0:	mla	v1.4s, v2.4s, v0.4s
     fd4:	mla	v4.4s, v3.4s, v0.4s
     fd8:	stp	q1, q4, [x27, #-16]
     fdc:	add	x27, x27, #0x20
     fe0:	b.ne	fc0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>  // b.any
     fe4:	b	1004 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c4>
     fe8:	nop
     fec:	nop
     ff0:	nop
     ff4:	nop
     ff8:	nop
     ffc:	nop
    1000:	mov	x25, xzr
    1004:	add	x24, x24, x9
    1008:	nop
    100c:	nop
    1010:	nop
    1014:	nop
    1018:	nop
    101c:	nop
    1020:	nop
    1024:	nop
    1028:	nop
    102c:	nop
    1030:	nop
    1034:	nop
    1038:	nop
    103c:	nop
    1040:	add	x10, x18, x25
    1044:	cmp	x7, x10
    1048:	b.ls	10d4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>  // b.plast
    104c:	add	x10, x8, x25
    1050:	cmp	x22, x10
    1054:	b.ls	10d4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>  // b.plast
    1058:	lsl	x10, x25, #2
    105c:	add	x25, x25, #0x1
    1060:	cmp	x3, x25
    1064:	ldr	w16, [x21, x10]
    1068:	ldr	w26, [x24, x10]
    106c:	madd	w16, w16, w23, w26
    1070:	str	w16, [x24, x10]
    1074:	b.ne	1040 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>  // b.any
    1078:	add	x1, x1, #0x1
    107c:	add	x18, x18, x3
    1080:	sub	x17, x17, x3
    1084:	cmp	x1, x3
    1088:	add	x20, x20, x13
    108c:	add	x21, x21, x13
    1090:	b.ne	ec0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>  // b.any
    1094:	mov	x10, x2
    1098:	add	x15, x15, x13
    109c:	add	x9, x9, x13
    10a0:	add	x10, x2, #0x1
    10a4:	ldr	x2, [sp, #8]
    10a8:	add	x8, x8, x3
    10ac:	cmp	x10, x3
    10b0:	b.ne	e88 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x48>  // b.any
    10b4:	ldp	x20, x19, [sp, #96]
    10b8:	ldp	x22, x21, [sp, #80]
    10bc:	ldp	x24, x23, [sp, #64]
    10c0:	ldp	x26, x25, [sp, #48]
    10c4:	ldp	x28, x27, [sp, #32]
    10c8:	ldp	x29, x30, [sp, #16]
    10cc:	add	sp, sp, #0x70
    10d0:	ret
    10d4:	brk	#0x1
