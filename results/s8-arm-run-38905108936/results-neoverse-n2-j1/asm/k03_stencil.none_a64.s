0000000000000e40 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x12, [x1]
     e44:	sub	x11, x12, x8
     e48:	asr	x9, x11, #2
     e4c:	cmp	x9, #0x3
     e50:	b.cc	eec <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xac>  // b.lo, b.ul, b.last
     e54:	sub	x13, x9, #0x2
     e58:	ldr	x10, [x0]
     e5c:	cmp	x13, #0x8
     e60:	b.cc	e80 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.lo, b.ul, b.last
     e64:	add	x14, x10, #0x4
     e68:	cmp	x14, x12
     e6c:	b.cs	ef0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>  // b.hs, b.nlast
     e70:	add	x11, x10, x11
     e74:	sub	x11, x11, #0x4
     e78:	cmp	x8, x11
     e7c:	b.cs	ef0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>  // b.hs, b.nlast
     e80:	mov	w12, #0x1                   	// #1
     e84:	mov	w11, #0x2                   	// #2
     e88:	sub	x13, x8, #0x4
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
     ec0:	lsl	x14, x12, #2
     ec4:	mov	x12, x11
     ec8:	ldr	w17, [x8, x11, lsl #2]
     ecc:	add	x11, x11, #0x1
     ed0:	ldr	w15, [x13, x14]
     ed4:	ldr	w16, [x8, x14]
     ed8:	cmp	x9, x11
     edc:	add	w15, w16, w15
     ee0:	add	w15, w15, w17
     ee4:	str	w15, [x10, x14]
     ee8:	b.ne	ec0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>  // b.any
     eec:	ret
     ef0:	and	x14, x13, #0xfffffffffffffff8
     ef4:	add	x15, x10, #0x14
     ef8:	add	x16, x8, #0x10
     efc:	orr	x11, x14, #0x2
     f00:	orr	x12, x14, #0x1
     f04:	mov	x17, x14
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
     f40:	ldp	q0, q2, [x16, #-16]
     f44:	subs	x17, x17, #0x8
     f48:	ldur	q1, [x16, #-12]
     f4c:	ldur	q3, [x16, #4]
     f50:	add	v0.4s, v1.4s, v0.4s
     f54:	add	v1.4s, v3.4s, v2.4s
     f58:	ldur	q2, [x16, #-8]
     f5c:	ldur	q3, [x16, #8]
     f60:	add	x16, x16, #0x20
     f64:	add	v0.4s, v0.4s, v2.4s
     f68:	add	v1.4s, v1.4s, v3.4s
     f6c:	stp	q0, q1, [x15, #-16]
     f70:	add	x15, x15, #0x20
     f74:	b.ne	f40 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>  // b.any
     f78:	cmp	x13, x14
     f7c:	b.ne	e88 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.any
     f80:	b	eec <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xac>
