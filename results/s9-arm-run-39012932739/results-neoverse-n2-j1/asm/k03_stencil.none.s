0000000000000e28 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x12, [x1]
     e2c:	sub	x11, x12, x8
     e30:	asr	x9, x11, #2
     e34:	cmp	x9, #0x3
     e38:	b.cc	ea0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x78>  // b.lo, b.ul, b.last
     e3c:	sub	x13, x9, #0x2
     e40:	ldr	x10, [x0]
     e44:	cmp	x13, #0x8
     e48:	b.cc	e68 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>  // b.lo, b.ul, b.last
     e4c:	add	x14, x10, #0x4
     e50:	cmp	x14, x12
     e54:	b.cs	ea4 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7c>  // b.hs, b.nlast
     e58:	add	x11, x10, x11
     e5c:	sub	x11, x11, #0x4
     e60:	cmp	x8, x11
     e64:	b.cs	ea4 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7c>  // b.hs, b.nlast
     e68:	mov	w12, #0x1                   	// #1
     e6c:	mov	w11, #0x2                   	// #2
     e70:	sub	x13, x8, #0x4
     e74:	lsl	x14, x12, #2
     e78:	mov	x12, x11
     e7c:	ldr	w17, [x8, x11, lsl #2]
     e80:	add	x11, x11, #0x1
     e84:	ldr	w15, [x13, x14]
     e88:	ldr	w16, [x8, x14]
     e8c:	cmp	x9, x11
     e90:	add	w15, w16, w15
     e94:	add	w15, w15, w17
     e98:	str	w15, [x10, x14]
     e9c:	b.ne	e74 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4c>  // b.any
     ea0:	ret
     ea4:	and	x14, x13, #0xfffffffffffffff8
     ea8:	add	x15, x10, #0x14
     eac:	add	x16, x8, #0x10
     eb0:	orr	x11, x14, #0x2
     eb4:	orr	x12, x14, #0x1
     eb8:	mov	x17, x14
     ebc:	ldp	q0, q2, [x16, #-16]
     ec0:	subs	x17, x17, #0x8
     ec4:	ldur	q1, [x16, #-12]
     ec8:	ldur	q3, [x16, #4]
     ecc:	add	v0.4s, v1.4s, v0.4s
     ed0:	add	v1.4s, v3.4s, v2.4s
     ed4:	ldur	q2, [x16, #-8]
     ed8:	ldur	q3, [x16, #8]
     edc:	add	x16, x16, #0x20
     ee0:	add	v0.4s, v0.4s, v2.4s
     ee4:	add	v1.4s, v1.4s, v3.4s
     ee8:	stp	q0, q1, [x15, #-16]
     eec:	add	x15, x15, #0x20
     ef0:	b.ne	ebc <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x94>  // b.any
     ef4:	cmp	x13, x14
     ef8:	b.ne	e70 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>  // b.any
     efc:	b	ea0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x78>
