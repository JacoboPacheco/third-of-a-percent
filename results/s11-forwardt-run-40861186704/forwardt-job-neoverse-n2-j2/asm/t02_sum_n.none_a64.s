0000000000000e40 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
     e40:	cbz	x1, e5c <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x1c>
     e44:	ldr	x8, [x0]
     e48:	cmp	x1, #0x8
     e4c:	b.cs	e68 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x28>  // b.hs, b.nlast
     e50:	mov	x9, xzr
     e54:	mov	x10, xzr
     e58:	b	efc <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0xbc>
     e5c:	mov	x10, xzr
     e60:	str	x10, [x2]
     e64:	ret
     e68:	movi	v0.2d, #0x0
     e6c:	movi	v1.2d, #0x0
     e70:	and	x9, x1, #0xfffffffffffffff8
     e74:	movi	v2.2d, #0x0
     e78:	movi	v3.2d, #0x0
     e7c:	add	x10, x8, #0x10
     e80:	mov	x11, x9
     e84:	nop
     e88:	nop
     e8c:	nop
     e90:	nop
     e94:	nop
     e98:	nop
     e9c:	nop
     ea0:	nop
     ea4:	nop
     ea8:	nop
     eac:	nop
     eb0:	nop
     eb4:	nop
     eb8:	nop
     ebc:	nop
     ec0:	ldp	q4, q5, [x10, #-16]
     ec4:	subs	x11, x11, #0x8
     ec8:	add	x10, x10, #0x20
     ecc:	saddw2	v1.2d, v1.2d, v4.4s
     ed0:	saddw	v0.2d, v0.2d, v4.2s
     ed4:	saddw2	v3.2d, v3.2d, v5.4s
     ed8:	saddw	v2.2d, v2.2d, v5.2s
     edc:	b.ne	ec0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x80>  // b.any
     ee0:	add	v0.2d, v2.2d, v0.2d
     ee4:	add	v1.2d, v3.2d, v1.2d
     ee8:	cmp	x9, x1
     eec:	add	v0.2d, v0.2d, v1.2d
     ef0:	addp	d0, v0.2d
     ef4:	fmov	x10, d0
     ef8:	b.eq	f50 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x110>  // b.none
     efc:	add	x8, x8, x9, lsl #2
     f00:	sub	x9, x1, x9
     f04:	nop
     f08:	nop
     f0c:	nop
     f10:	nop
     f14:	nop
     f18:	nop
     f1c:	nop
     f20:	nop
     f24:	nop
     f28:	nop
     f2c:	nop
     f30:	nop
     f34:	nop
     f38:	nop
     f3c:	nop
     f40:	ldrsw	x11, [x8], #4
     f44:	subs	x9, x9, #0x1
     f48:	add	x10, x10, x11
     f4c:	b.ne	f40 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x100>  // b.any
     f50:	str	x10, [x2]
     f54:	ret
