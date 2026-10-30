0000000000000e28 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
     e28:	cbz	x2, eec <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc4>
     e2c:	ldp	x8, x10, [x0]
     e30:	sub	x12, x2, #0x1
     e34:	ldp	x9, x11, [x1]
     e38:	sub	x10, x10, x8
     e3c:	asr	x10, x10, #2
     e40:	sub	x11, x11, x9
     e44:	sub	x13, x8, x9
     e48:	asr	x11, x11, #2
     e4c:	cmp	x10, x12
     e50:	csel	x12, x10, x12, cc	// cc = lo, ul, last
     e54:	cmp	x12, x11
     e58:	csel	x12, x12, x11, cc	// cc = lo, ul, last
     e5c:	add	x12, x12, #0x1
     e60:	cmp	x12, #0x9
     e64:	ccmp	x13, #0x1f, #0x0, cs	// cs = hs, nlast
     e68:	b.hi	e74 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x4c>  // b.pmore
     e6c:	mov	x12, xzr
     e70:	b	eb0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x88>
     e74:	ands	x13, x12, #0x7
     e78:	mov	w14, #0x8                   	// #8
     e7c:	csel	x13, x14, x13, eq	// eq = none
     e80:	add	x14, x8, #0x10
     e84:	sub	x12, x12, x13
     e88:	add	x13, x9, #0x10
     e8c:	mov	x15, x12
     e90:	ldp	q0, q1, [x13, #-16]
     e94:	subs	x15, x15, #0x8
     e98:	add	x13, x13, #0x20
     e9c:	add	v0.4s, v0.4s, v0.4s
     ea0:	add	v1.4s, v1.4s, v1.4s
     ea4:	stp	q0, q1, [x14, #-16]
     ea8:	add	x14, x14, #0x20
     eac:	b.ne	e90 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x68>  // b.any
     eb0:	lsl	x13, x12, #2
     eb4:	sub	x10, x10, x12
     eb8:	sub	x11, x11, x12
     ebc:	sub	x12, x2, x12
     ec0:	add	x9, x9, x13
     ec4:	add	x8, x8, x13
     ec8:	cbz	x11, ef0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc8>
     ecc:	cbz	x10, ef0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc8>
     ed0:	ldr	w13, [x9], #4
     ed4:	subs	x12, x12, #0x1
     ed8:	sub	x10, x10, #0x1
     edc:	sub	x11, x11, #0x1
     ee0:	lsl	w13, w13, #1
     ee4:	str	w13, [x8], #4
     ee8:	b.ne	ec8 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xa0>  // b.any
     eec:	ret
     ef0:	brk	#0x1
