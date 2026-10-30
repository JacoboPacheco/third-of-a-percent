0000000000000e28 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
     e28:	cbz	x2, e48 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x20>
     e2c:	ldr	x8, [x1]
     e30:	ldr	x9, [x0]
     e34:	ldr	w10, [x8], #4
     e38:	subs	x2, x2, #0x1
     e3c:	lsl	w10, w10, #1
     e40:	str	w10, [x9], #4
     e44:	b.ne	e34 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc>  // b.any
     e48:	ret
