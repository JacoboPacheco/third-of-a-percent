0000000000000e28 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	ee0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb8>  // b.none
     e34:	asr	x11, x9, #2
     e38:	ldp	x9, x10, [x0]
     e3c:	cmp	x11, #0x1
     e40:	sub	x10, x10, x9
     e44:	csinc	x11, x11, xzr, hi	// hi = pmore
     e48:	sub	x13, x9, x8
     e4c:	asr	x10, x10, #2
     e50:	sub	x12, x11, #0x1
     e54:	cmp	x12, x10
     e58:	csel	x12, x12, x10, cc	// cc = lo, ul, last
     e5c:	cmp	x12, #0x8
     e60:	ccmp	x13, #0x1f, #0x0, cs	// cs = hs, nlast
     e64:	b.hi	e70 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.pmore
     e68:	mov	x12, xzr
     e6c:	b	eb0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x88>
     e70:	add	x12, x12, #0x1
     e74:	mov	w14, #0x8                   	// #8
     e78:	ands	x13, x12, #0x7
     e7c:	csel	x13, x14, x13, eq	// eq = none
     e80:	add	x14, x9, #0x10
     e84:	sub	x12, x12, x13
     e88:	add	x13, x8, #0x10
     e8c:	mov	x15, x12
     e90:	ldp	q0, q1, [x13, #-16]
     e94:	subs	x15, x15, #0x8
     e98:	add	x13, x13, #0x20
     e9c:	add	v0.4s, v0.4s, v0.4s
     ea0:	add	v1.4s, v1.4s, v1.4s
     ea4:	stp	q0, q1, [x14, #-16]
     ea8:	add	x14, x14, #0x20
     eac:	b.ne	e90 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x68>  // b.any
     eb0:	lsl	x13, x12, #2
     eb4:	sub	x10, x10, x12
     eb8:	sub	x11, x11, x12
     ebc:	add	x8, x8, x13
     ec0:	add	x9, x9, x13
     ec4:	cbz	x10, ee4 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xbc>
     ec8:	ldr	w12, [x8], #4
     ecc:	subs	x11, x11, #0x1
     ed0:	sub	x10, x10, #0x1
     ed4:	lsl	w12, w12, #1
     ed8:	str	w12, [x9], #4
     edc:	b.ne	ec4 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9c>  // b.any
     ee0:	ret
     ee4:	brk	#0x1
