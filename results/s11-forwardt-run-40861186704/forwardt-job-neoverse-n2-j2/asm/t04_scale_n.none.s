0000000000000e28 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
     e28:	cbz	x2, ea8 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>
     e2c:	ldr	x9, [x1]
     e30:	ldr	x8, [x0]
     e34:	cmp	x2, #0x8
     e38:	mov	x10, xzr
     e3c:	b.cc	e84 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x5c>  // b.lo, b.ul, b.last
     e40:	sub	x11, x8, x9
     e44:	cmp	x11, #0x20
     e48:	b.cc	e84 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x5c>  // b.lo, b.ul, b.last
     e4c:	and	x10, x2, #0xfffffffffffffff8
     e50:	add	x11, x9, #0x10
     e54:	add	x12, x8, #0x10
     e58:	mov	x13, x10
     e5c:	ldp	q0, q1, [x11, #-16]
     e60:	subs	x13, x13, #0x8
     e64:	add	x11, x11, #0x20
     e68:	add	v0.4s, v0.4s, v0.4s
     e6c:	add	v1.4s, v1.4s, v1.4s
     e70:	stp	q0, q1, [x12, #-16]
     e74:	add	x12, x12, #0x20
     e78:	b.ne	e5c <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x34>  // b.any
     e7c:	cmp	x10, x2
     e80:	b.eq	ea8 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>  // b.none
     e84:	lsl	x11, x10, #2
     e88:	sub	x10, x2, x10
     e8c:	add	x9, x9, x11
     e90:	add	x8, x8, x11
     e94:	ldr	w11, [x9], #4
     e98:	subs	x10, x10, #0x1
     e9c:	lsl	w11, w11, #1
     ea0:	str	w11, [x8], #4
     ea4:	b.ne	e94 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x6c>  // b.any
     ea8:	ret
