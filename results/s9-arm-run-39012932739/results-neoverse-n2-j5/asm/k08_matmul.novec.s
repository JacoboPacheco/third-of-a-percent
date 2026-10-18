0000000000000e28 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
     e28:	cbz	x3, e98 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
     e2c:	ldr	x8, [x1]
     e30:	ldr	x9, [x2]
     e34:	lsl	x10, x3, #2
     e38:	ldr	x11, [x0]
     e3c:	mov	x12, xzr
     e40:	mul	x14, x12, x3
     e44:	mov	x13, xzr
     e48:	mov	x15, x9
     e4c:	add	x14, x8, x14, lsl #2
     e50:	ldr	w16, [x14, x13, lsl #2]
     e54:	mov	x17, xzr
     e58:	lsl	x18, x17, #2
     e5c:	add	x17, x17, #0x1
     e60:	cmp	x3, x17
     e64:	ldr	w0, [x15, x18]
     e68:	ldr	w1, [x11, x18]
     e6c:	madd	w0, w0, w16, w1
     e70:	str	w0, [x11, x18]
     e74:	b.ne	e58 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x30>  // b.any
     e78:	add	x13, x13, #0x1
     e7c:	add	x15, x15, x10
     e80:	cmp	x13, x3
     e84:	b.ne	e50 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x28>  // b.any
     e88:	add	x12, x12, #0x1
     e8c:	add	x11, x11, x10
     e90:	cmp	x12, x3
     e94:	b.ne	e40 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x18>  // b.any
     e98:	ret
