0000000000000e28 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
     e28:	cbz	x1, e44 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x1c>
     e2c:	ldr	x8, [x0]
     e30:	cmp	x1, #0x8
     e34:	b.cs	e50 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x28>  // b.hs, b.nlast
     e38:	mov	x9, xzr
     e3c:	mov	x10, xzr
     e40:	b	ea8 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x80>
     e44:	mov	x10, xzr
     e48:	str	x10, [x2]
     e4c:	ret
     e50:	movi	v0.2d, #0x0
     e54:	movi	v1.2d, #0x0
     e58:	and	x9, x1, #0xfffffffffffffff8
     e5c:	movi	v2.2d, #0x0
     e60:	movi	v3.2d, #0x0
     e64:	add	x10, x8, #0x10
     e68:	mov	x11, x9
     e6c:	ldp	q4, q5, [x10, #-16]
     e70:	subs	x11, x11, #0x8
     e74:	add	x10, x10, #0x20
     e78:	saddw2	v1.2d, v1.2d, v4.4s
     e7c:	saddw	v0.2d, v0.2d, v4.2s
     e80:	saddw2	v3.2d, v3.2d, v5.4s
     e84:	saddw	v2.2d, v2.2d, v5.2s
     e88:	b.ne	e6c <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x44>  // b.any
     e8c:	add	v0.2d, v2.2d, v0.2d
     e90:	add	v1.2d, v3.2d, v1.2d
     e94:	cmp	x9, x1
     e98:	add	v0.2d, v0.2d, v1.2d
     e9c:	addp	d0, v0.2d
     ea0:	fmov	x10, d0
     ea4:	b.eq	ec0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x98>  // b.none
     ea8:	add	x8, x8, x9, lsl #2
     eac:	sub	x9, x1, x9
     eb0:	ldrsw	x11, [x8], #4
     eb4:	subs	x9, x9, #0x1
     eb8:	add	x10, x10, x11
     ebc:	b.ne	eb0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x88>  // b.any
     ec0:	str	x10, [x2]
     ec4:	ret
