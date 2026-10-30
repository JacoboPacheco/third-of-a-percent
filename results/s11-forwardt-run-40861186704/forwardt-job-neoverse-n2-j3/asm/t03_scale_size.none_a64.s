0000000000000e40 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x1]
     e44:	subs	x9, x9, x8
     e48:	b.eq	f14 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd4>  // b.none
     e4c:	asr	x11, x9, #2
     e50:	ldr	x9, [x0]
     e54:	cmp	x11, #0x1
     e58:	csinc	x10, x11, xzr, hi	// hi = pmore
     e5c:	cmp	x11, #0x8
     e60:	mov	x11, xzr
     e64:	b.cc	ee8 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa8>  // b.lo, b.ul, b.last
     e68:	sub	x12, x9, x8
     e6c:	cmp	x12, #0x20
     e70:	b.cc	ee8 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa8>  // b.lo, b.ul, b.last
     e74:	and	x11, x10, #0xfffffffffffffff8
     e78:	add	x12, x8, #0x10
     e7c:	add	x13, x9, #0x10
     e80:	mov	x14, x11
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
     ec0:	ldp	q0, q1, [x12, #-16]
     ec4:	subs	x14, x14, #0x8
     ec8:	add	x12, x12, #0x20
     ecc:	add	v0.4s, v0.4s, v0.4s
     ed0:	add	v1.4s, v1.4s, v1.4s
     ed4:	stp	q0, q1, [x13, #-16]
     ed8:	add	x13, x13, #0x20
     edc:	b.ne	ec0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>  // b.any
     ee0:	cmp	x10, x11
     ee4:	b.eq	f14 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd4>  // b.none
     ee8:	lsl	x12, x11, #2
     eec:	sub	x10, x10, x11
     ef0:	add	x8, x8, x12
     ef4:	add	x9, x9, x12
     ef8:	nop
     efc:	nop
     f00:	ldr	w11, [x8], #4
     f04:	subs	x10, x10, #0x1
     f08:	lsl	w11, w11, #1
     f0c:	str	w11, [x9], #4
     f10:	b.ne	f00 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>  // b.any
     f14:	ret
