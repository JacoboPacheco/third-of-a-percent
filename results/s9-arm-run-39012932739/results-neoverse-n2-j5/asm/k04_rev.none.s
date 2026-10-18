0000000000000e28 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x9, x8, [x1]
     e2c:	subs	x12, x8, x9
     e30:	b.eq	eb8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>  // b.none
     e34:	asr	x8, x12, #2
     e38:	ldr	x10, [x0]
     e3c:	cmp	x8, #0x8
     e40:	b.cc	e98 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>  // b.lo, b.ul, b.last
     e44:	sub	x11, x9, x10
     e48:	cmp	x11, #0x20
     e4c:	b.cc	e98 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>  // b.lo, b.ul, b.last
     e50:	lsl	x13, x8, #2
     e54:	and	x11, x8, #0xfffffffffffffff8
     e58:	ubfx	x12, x12, #2, #3
     e5c:	mov	x15, x11
     e60:	sub	x14, x13, #0x10
     e64:	add	x13, x9, x14
     e68:	add	x14, x10, x14
     e6c:	ldp	q1, q0, [x13, #-16]
     e70:	sub	x15, x15, #0x8
     e74:	sub	x13, x13, #0x20
     e78:	add	v0.4s, v0.4s, v0.4s
     e7c:	add	v1.4s, v1.4s, v1.4s
     e80:	stp	q1, q0, [x14, #-16]
     e84:	sub	x14, x14, #0x20
     e88:	cbnz	x15, e6c <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x44>
     e8c:	cmp	x8, x11
     e90:	mov	x8, x12
     e94:	b.eq	eb8 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>  // b.none
     e98:	sub	x10, x10, #0x4
     e9c:	sub	x9, x9, #0x4
     ea0:	lsl	x11, x8, #2
     ea4:	subs	x8, x8, #0x1
     ea8:	ldr	w12, [x9, x11]
     eac:	lsl	w12, w12, #1
     eb0:	str	w12, [x10, x11]
     eb4:	b.ne	ea0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x78>  // b.any
     eb8:	ret
