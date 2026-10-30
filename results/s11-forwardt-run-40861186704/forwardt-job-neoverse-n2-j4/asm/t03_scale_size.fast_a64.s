0000000000000e40 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x1]
     e44:	subs	x9, x9, x8
     e48:	b.eq	f1c <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xdc>  // b.none
     e4c:	asr	x11, x9, #2
     e50:	ldp	x9, x10, [x0]
     e54:	cmp	x11, #0x1
     e58:	sub	x10, x10, x9
     e5c:	csinc	x11, x11, xzr, hi	// hi = pmore
     e60:	sub	x13, x9, x8
     e64:	asr	x10, x10, #2
     e68:	sub	x12, x11, #0x1
     e6c:	cmp	x12, x10
     e70:	csel	x12, x12, x10, cc	// cc = lo, ul, last
     e74:	cmp	x12, #0x8
     e78:	ccmp	x13, #0x1f, #0x0, cs	// cs = hs, nlast
     e7c:	b.hi	e88 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.pmore
     e80:	mov	x12, xzr
     e84:	b	ee0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
     e88:	add	x12, x12, #0x1
     e8c:	mov	w14, #0x8                   	// #8
     e90:	ands	x13, x12, #0x7
     e94:	csel	x13, x14, x13, eq	// eq = none
     e98:	add	x14, x9, #0x10
     e9c:	sub	x12, x12, x13
     ea0:	add	x13, x8, #0x10
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
     edc:	b.ne	ec0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>  // b.any
     ee0:	lsl	x13, x12, #2
     ee4:	sub	x10, x10, x12
     ee8:	sub	x11, x11, x12
     eec:	add	x8, x8, x13
     ef0:	add	x9, x9, x13
     ef4:	nop
     ef8:	nop
     efc:	nop
     f00:	cbz	x10, f20 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe0>
     f04:	ldr	w12, [x8], #4
     f08:	subs	x11, x11, #0x1
     f0c:	sub	x10, x10, #0x1
     f10:	lsl	w12, w12, #1
     f14:	str	w12, [x9], #4
     f18:	b.ne	f00 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>  // b.any
     f1c:	ret
     f20:	brk	#0x1
