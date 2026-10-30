0000000000000e40 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
     e40:	cbz	x2, f24 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xe4>
     e44:	ldp	x8, x10, [x0]
     e48:	sub	x12, x2, #0x1
     e4c:	ldp	x9, x11, [x1]
     e50:	sub	x10, x10, x8
     e54:	asr	x10, x10, #2
     e58:	sub	x11, x11, x9
     e5c:	sub	x13, x8, x9
     e60:	asr	x11, x11, #2
     e64:	cmp	x10, x12
     e68:	csel	x12, x10, x12, cc	// cc = lo, ul, last
     e6c:	cmp	x12, x11
     e70:	csel	x12, x12, x11, cc	// cc = lo, ul, last
     e74:	add	x12, x12, #0x1
     e78:	cmp	x12, #0x9
     e7c:	ccmp	x13, #0x1f, #0x0, cs	// cs = hs, nlast
     e80:	b.hi	e8c <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x4c>  // b.pmore
     e84:	mov	x12, xzr
     e88:	b	ee0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xa0>
     e8c:	ands	x13, x12, #0x7
     e90:	mov	w14, #0x8                   	// #8
     e94:	csel	x13, x14, x13, eq	// eq = none
     e98:	add	x14, x8, #0x10
     e9c:	sub	x12, x12, x13
     ea0:	add	x13, x9, #0x10
     ea4:	mov	x15, x12
     ea8:	nop
     eac:	nop
     eb0:	nop
     eb4:	nop
     eb8:	nop
     ebc:	nop
     ec0:	ldp	q0, q1, [x13, #-16]
     ec4:	subs	x15, x15, #0x8
     ec8:	add	x13, x13, #0x20
     ecc:	add	v0.4s, v0.4s, v0.4s
     ed0:	add	v1.4s, v1.4s, v1.4s
     ed4:	stp	q0, q1, [x14, #-16]
     ed8:	add	x14, x14, #0x20
     edc:	b.ne	ec0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>  // b.any
     ee0:	lsl	x13, x12, #2
     ee4:	sub	x10, x10, x12
     ee8:	sub	x11, x11, x12
     eec:	sub	x12, x2, x12
     ef0:	add	x9, x9, x13
     ef4:	add	x8, x8, x13
     ef8:	nop
     efc:	nop
     f00:	cbz	x11, f28 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xe8>
     f04:	cbz	x10, f28 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xe8>
     f08:	ldr	w13, [x9], #4
     f0c:	subs	x12, x12, #0x1
     f10:	sub	x10, x10, #0x1
     f14:	sub	x11, x11, #0x1
     f18:	lsl	w13, w13, #1
     f1c:	str	w13, [x8], #4
     f20:	b.ne	f00 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc0>  // b.any
     f24:	ret
     f28:	brk	#0x1
