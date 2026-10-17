0000000000000e40 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
     e40:	ldp	x8, x9, [x0]
     e44:	subs	x9, x9, x8
     e48:	b.eq	e6c <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2c>  // b.none
     e4c:	asr	x10, x9, #2
     e50:	cmp	x10, #0x1
     e54:	csinc	x9, x10, xzr, hi	// hi = pmore
     e58:	cmp	x10, #0x8
     e5c:	b.cs	e74 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x34>  // b.hs, b.nlast
     e60:	mov	x10, xzr
     e64:	mov	x0, xzr
     e68:	b	efc <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xbc>
     e6c:	mov	x0, xzr
     e70:	ret
     e74:	movi	v0.2d, #0x0
     e78:	movi	v1.2d, #0x0
     e7c:	and	x10, x9, #0xfffffffffffffff8
     e80:	movi	v2.2d, #0x0
     e84:	movi	v3.2d, #0x0
     e88:	add	x11, x8, #0x10
     e8c:	mov	x12, x10
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
     ec0:	ldp	q4, q5, [x11, #-16]
     ec4:	subs	x12, x12, #0x8
     ec8:	add	x11, x11, #0x20
     ecc:	saddw2	v1.2d, v1.2d, v4.4s
     ed0:	saddw	v0.2d, v0.2d, v4.2s
     ed4:	saddw2	v3.2d, v3.2d, v5.4s
     ed8:	saddw	v2.2d, v2.2d, v5.2s
     edc:	b.ne	ec0 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x80>  // b.any
     ee0:	add	v0.2d, v2.2d, v0.2d
     ee4:	add	v1.2d, v3.2d, v1.2d
     ee8:	cmp	x9, x10
     eec:	add	v0.2d, v0.2d, v1.2d
     ef0:	addp	d0, v0.2d
     ef4:	fmov	x0, d0
     ef8:	b.eq	f50 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x110>  // b.none
     efc:	add	x8, x8, x10, lsl #2
     f00:	sub	x9, x9, x10
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
     f40:	ldrsw	x10, [x8], #4
     f44:	subs	x9, x9, #0x1
     f48:	add	x0, x0, x10
     f4c:	b.ne	f40 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x100>  // b.any
     f50:	ret
