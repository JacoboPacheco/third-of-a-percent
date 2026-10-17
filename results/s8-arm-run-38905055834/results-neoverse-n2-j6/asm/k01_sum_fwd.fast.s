0000000000000e28 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
     e28:	ldp	x8, x9, [x0]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e54 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2c>  // b.none
     e34:	asr	x10, x9, #2
     e38:	cmp	x10, #0x1
     e3c:	csinc	x9, x10, xzr, hi	// hi = pmore
     e40:	cmp	x10, #0x8
     e44:	b.cs	e5c <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x34>  // b.hs, b.nlast
     e48:	mov	x10, xzr
     e4c:	mov	x0, xzr
     e50:	b	eb4 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x8c>
     e54:	mov	x0, xzr
     e58:	ret
     e5c:	movi	v0.2d, #0x0
     e60:	movi	v1.2d, #0x0
     e64:	and	x10, x9, #0xfffffffffffffff8
     e68:	movi	v2.2d, #0x0
     e6c:	movi	v3.2d, #0x0
     e70:	add	x11, x8, #0x10
     e74:	mov	x12, x10
     e78:	ldp	q4, q5, [x11, #-16]
     e7c:	subs	x12, x12, #0x8
     e80:	add	x11, x11, #0x20
     e84:	saddw2	v1.2d, v1.2d, v4.4s
     e88:	saddw	v0.2d, v0.2d, v4.2s
     e8c:	saddw2	v3.2d, v3.2d, v5.4s
     e90:	saddw	v2.2d, v2.2d, v5.2s
     e94:	b.ne	e78 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x50>  // b.any
     e98:	add	v0.2d, v2.2d, v0.2d
     e9c:	add	v1.2d, v3.2d, v1.2d
     ea0:	cmp	x9, x10
     ea4:	add	v0.2d, v0.2d, v1.2d
     ea8:	addp	d0, v0.2d
     eac:	fmov	x0, d0
     eb0:	b.eq	ecc <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xa4>  // b.none
     eb4:	add	x8, x8, x10, lsl #2
     eb8:	sub	x9, x9, x10
     ebc:	ldrsw	x10, [x8], #4
     ec0:	subs	x9, x9, #0x1
     ec4:	add	x0, x0, x10
     ec8:	b.ne	ebc <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x94>  // b.any
     ecc:	ret
