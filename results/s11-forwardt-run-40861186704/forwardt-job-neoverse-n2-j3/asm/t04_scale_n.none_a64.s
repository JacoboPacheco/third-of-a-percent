0000000000000e40 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
     e40:	cbz	x2, ed4 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x94>
     e44:	ldr	x9, [x1]
     e48:	ldr	x8, [x0]
     e4c:	cmp	x2, #0x8
     e50:	mov	x10, xzr
     e54:	b.cc	ea8 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x68>  // b.lo, b.ul, b.last
     e58:	sub	x11, x8, x9
     e5c:	cmp	x11, #0x20
     e60:	b.cc	ea8 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x68>  // b.lo, b.ul, b.last
     e64:	and	x10, x2, #0xfffffffffffffff8
     e68:	add	x11, x9, #0x10
     e6c:	add	x12, x8, #0x10
     e70:	mov	x13, x10
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	ldp	q0, q1, [x11, #-16]
     e84:	subs	x13, x13, #0x8
     e88:	add	x11, x11, #0x20
     e8c:	add	v0.4s, v0.4s, v0.4s
     e90:	add	v1.4s, v1.4s, v1.4s
     e94:	stp	q0, q1, [x12, #-16]
     e98:	add	x12, x12, #0x20
     e9c:	b.ne	e80 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x40>  // b.any
     ea0:	cmp	x10, x2
     ea4:	b.eq	ed4 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x94>  // b.none
     ea8:	lsl	x11, x10, #2
     eac:	sub	x10, x2, x10
     eb0:	add	x9, x9, x11
     eb4:	add	x8, x8, x11
     eb8:	nop
     ebc:	nop
     ec0:	ldr	w11, [x9], #4
     ec4:	subs	x10, x10, #0x1
     ec8:	lsl	w11, w11, #1
     ecc:	str	w11, [x8], #4
     ed0:	b.ne	ec0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>  // b.any
     ed4:	ret
