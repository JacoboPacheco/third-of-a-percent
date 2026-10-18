0000000000000e40 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x0]
     e44:	subs	x9, x9, x8
     e48:	b.eq	f58 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x118>  // b.none
     e4c:	asr	x11, x9, #2
     e50:	ldr	x10, [x1]
     e54:	cmp	x11, #0x1
     e58:	csinc	x9, x11, xzr, hi	// hi = pmore
     e5c:	cmp	x11, #0x8
     e60:	b.cc	ef4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>  // b.lo, b.ul, b.last
     e64:	add	x11, x10, x9, lsl #3
     e68:	add	x12, x8, x9, lsl #2
     e6c:	cmp	x8, x11
     e70:	ccmp	x10, x12, #0x2, cc	// cc = lo, ul, last
     e74:	b.cc	ef4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>  // b.lo, b.ul, b.last
     e78:	and	x11, x9, #0xfffffffffffffff8
     e7c:	add	x12, x10, #0x20
     e80:	add	x13, x8, #0x10
     e84:	mov	x14, x11
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
     ec0:	sub	x15, x12, #0x20
     ec4:	ld2	{v2.4s-v3.4s}, [x12]
     ec8:	subs	x14, x14, #0x8
     ecc:	add	x12, x12, #0x40
     ed0:	ld2	{v0.4s-v1.4s}, [x15]
     ed4:	add	v0.4s, v1.4s, v0.4s
     ed8:	add	v1.4s, v3.4s, v2.4s
     edc:	stp	q0, q1, [x13, #-16]
     ee0:	add	x13, x13, #0x20
     ee4:	b.ne	ec0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>  // b.any
     ee8:	cmp	x9, x11
     eec:	b.ne	ef8 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb8>  // b.any
     ef0:	b	f58 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x118>
     ef4:	mov	x11, xzr
     ef8:	add	x10, x10, x11, lsl #3
     efc:	add	x8, x8, x11, lsl #2
     f00:	sub	x9, x9, x11
     f04:	add	x10, x10, #0x4
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
     f40:	ldp	w11, w12, [x10, #-4]
     f44:	subs	x9, x9, #0x1
     f48:	add	x10, x10, #0x8
     f4c:	add	w11, w12, w11
     f50:	str	w11, [x8], #4
     f54:	b.ne	f40 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>  // b.any
     f58:	ret
