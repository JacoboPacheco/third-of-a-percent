0000000000000e40 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x9, x8, [x1]
     e44:	subs	x12, x8, x9
     e48:	b.eq	f18 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>  // b.none
     e4c:	asr	x8, x12, #2
     e50:	ldr	x10, [x0]
     e54:	cmp	x8, #0x8
     e58:	b.cc	eec <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xac>  // b.lo, b.ul, b.last
     e5c:	sub	x11, x9, x10
     e60:	cmp	x11, #0x20
     e64:	b.cc	eec <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xac>  // b.lo, b.ul, b.last
     e68:	lsl	x13, x8, #2
     e6c:	and	x11, x8, #0xfffffffffffffff8
     e70:	ubfx	x12, x12, #2, #3
     e74:	mov	x15, x11
     e78:	sub	x14, x13, #0x10
     e7c:	add	x13, x9, x14
     e80:	add	x14, x10, x14
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
     ec0:	ldp	q1, q0, [x13, #-16]
     ec4:	sub	x15, x15, #0x8
     ec8:	sub	x13, x13, #0x20
     ecc:	add	v0.4s, v0.4s, v0.4s
     ed0:	add	v1.4s, v1.4s, v1.4s
     ed4:	stp	q1, q0, [x14, #-16]
     ed8:	sub	x14, x14, #0x20
     edc:	cbnz	x15, ec0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
     ee0:	cmp	x8, x11
     ee4:	mov	x8, x12
     ee8:	b.eq	f18 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>  // b.none
     eec:	sub	x10, x10, #0x4
     ef0:	sub	x9, x9, #0x4
     ef4:	nop
     ef8:	nop
     efc:	nop
     f00:	lsl	x11, x8, #2
     f04:	subs	x8, x8, #0x1
     f08:	ldr	w12, [x9, x11]
     f0c:	lsl	w12, w12, #1
     f10:	str	w12, [x10, x11]
     f14:	b.ne	f00 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>  // b.any
     f18:	ret
