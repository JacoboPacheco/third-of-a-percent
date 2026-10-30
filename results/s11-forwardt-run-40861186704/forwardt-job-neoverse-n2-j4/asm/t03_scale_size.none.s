0000000000000e28 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	eb8 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>  // b.none
     e34:	asr	x11, x9, #2
     e38:	ldr	x9, [x0]
     e3c:	cmp	x11, #0x1
     e40:	csinc	x10, x11, xzr, hi	// hi = pmore
     e44:	cmp	x11, #0x8
     e48:	mov	x11, xzr
     e4c:	b.cc	e94 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x6c>  // b.lo, b.ul, b.last
     e50:	sub	x12, x9, x8
     e54:	cmp	x12, #0x20
     e58:	b.cc	e94 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x6c>  // b.lo, b.ul, b.last
     e5c:	and	x11, x10, #0xfffffffffffffff8
     e60:	add	x12, x8, #0x10
     e64:	add	x13, x9, #0x10
     e68:	mov	x14, x11
     e6c:	ldp	q0, q1, [x12, #-16]
     e70:	subs	x14, x14, #0x8
     e74:	add	x12, x12, #0x20
     e78:	add	v0.4s, v0.4s, v0.4s
     e7c:	add	v1.4s, v1.4s, v1.4s
     e80:	stp	q0, q1, [x13, #-16]
     e84:	add	x13, x13, #0x20
     e88:	b.ne	e6c <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x44>  // b.any
     e8c:	cmp	x10, x11
     e90:	b.eq	eb8 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>  // b.none
     e94:	lsl	x12, x11, #2
     e98:	sub	x10, x10, x11
     e9c:	add	x8, x8, x12
     ea0:	add	x9, x9, x12
     ea4:	ldr	w11, [x8], #4
     ea8:	subs	x10, x10, #0x1
     eac:	lsl	w11, w11, #1
     eb0:	str	w11, [x9], #4
     eb4:	b.ne	ea4 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7c>  // b.any
     eb8:	ret
