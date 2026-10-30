0000000000000be8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
 be8:	cmp	w2, #0x1
 bec:	b.lt	c10 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x28>  // b.tstop
 bf0:	ldr	x9, [x0]
 bf4:	ldr	x8, [x1]
 bf8:	mov	w10, w2
 bfc:	add	x9, x9, w3, sxtw #2
 c00:	ldr	w11, [x8], #4
 c04:	subs	x10, x10, #0x1
 c08:	str	w11, [x9], #4
 c0c:	b.ne	c00 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x18>  // b.any
 c10:	ret
