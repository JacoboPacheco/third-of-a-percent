0000000000000e28 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x0]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	ed0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa8>  // b.none
     e34:	asr	x11, x9, #2
     e38:	ldr	x10, [x1]
     e3c:	cmp	x11, #0x1
     e40:	csinc	x9, x11, xzr, hi	// hi = pmore
     e44:	cmp	x11, #0x8
     e48:	b.cc	ea4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7c>  // b.lo, b.ul, b.last
     e4c:	add	x11, x10, x9, lsl #3
     e50:	add	x12, x8, x9, lsl #2
     e54:	cmp	x8, x11
     e58:	ccmp	x10, x12, #0x2, cc	// cc = lo, ul, last
     e5c:	b.cc	ea4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7c>  // b.lo, b.ul, b.last
     e60:	and	x11, x9, #0xfffffffffffffff8
     e64:	add	x12, x10, #0x20
     e68:	add	x13, x8, #0x10
     e6c:	mov	x14, x11
     e70:	sub	x15, x12, #0x20
     e74:	ld2	{v2.4s-v3.4s}, [x12]
     e78:	subs	x14, x14, #0x8
     e7c:	add	x12, x12, #0x40
     e80:	ld2	{v0.4s-v1.4s}, [x15]
     e84:	add	v0.4s, v1.4s, v0.4s
     e88:	add	v1.4s, v3.4s, v2.4s
     e8c:	stp	q0, q1, [x13, #-16]
     e90:	add	x13, x13, #0x20
     e94:	b.ne	e70 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.any
     e98:	cmp	x9, x11
     e9c:	b.ne	ea8 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>  // b.any
     ea0:	b	ed0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa8>
     ea4:	mov	x11, xzr
     ea8:	add	x10, x10, x11, lsl #3
     eac:	add	x8, x8, x11, lsl #2
     eb0:	sub	x9, x9, x11
     eb4:	add	x10, x10, #0x4
     eb8:	ldp	w11, w12, [x10, #-4]
     ebc:	subs	x9, x9, #0x1
     ec0:	add	x10, x10, #0x8
     ec4:	add	w11, w12, w11
     ec8:	str	w11, [x8], #4
     ecc:	b.ne	eb8 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>  // b.any
     ed0:	ret
