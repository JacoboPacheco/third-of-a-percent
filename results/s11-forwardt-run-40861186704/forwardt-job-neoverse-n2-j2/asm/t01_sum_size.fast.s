0000000000000e28 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl>:
     e28:	ldp	x8, x9, [x0]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	e54 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x2c>  // b.none
     e34:	asr	x10, x9, #2
     e38:	cmp	x10, #0x1
     e3c:	csinc	x9, x10, xzr, hi	// hi = pmore
     e40:	cmp	x10, #0x8
     e44:	b.cs	e60 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x38>  // b.hs, b.nlast
     e48:	mov	x10, xzr
     e4c:	mov	x11, xzr
     e50:	b	eb8 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x90>
     e54:	mov	x11, xzr
     e58:	str	x11, [x1]
     e5c:	ret
     e60:	movi	v0.2d, #0x0
     e64:	movi	v1.2d, #0x0
     e68:	and	x10, x9, #0xfffffffffffffff8
     e6c:	movi	v2.2d, #0x0
     e70:	movi	v3.2d, #0x0
     e74:	add	x11, x8, #0x10
     e78:	mov	x12, x10
     e7c:	ldp	q4, q5, [x11, #-16]
     e80:	subs	x12, x12, #0x8
     e84:	add	x11, x11, #0x20
     e88:	saddw2	v1.2d, v1.2d, v4.4s
     e8c:	saddw	v0.2d, v0.2d, v4.2s
     e90:	saddw2	v3.2d, v3.2d, v5.4s
     e94:	saddw	v2.2d, v2.2d, v5.2s
     e98:	b.ne	e7c <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x54>  // b.any
     e9c:	add	v0.2d, v2.2d, v0.2d
     ea0:	add	v1.2d, v3.2d, v1.2d
     ea4:	cmp	x9, x10
     ea8:	add	v0.2d, v0.2d, v1.2d
     eac:	addp	d0, v0.2d
     eb0:	fmov	x11, d0
     eb4:	b.eq	ed0 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0xa8>  // b.none
     eb8:	add	x8, x8, x10, lsl #2
     ebc:	sub	x9, x9, x10
     ec0:	ldrsw	x10, [x8], #4
     ec4:	subs	x9, x9, #0x1
     ec8:	add	x11, x11, x10
     ecc:	b.ne	ec0 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x98>  // b.any
     ed0:	str	x11, [x1]
     ed4:	ret
