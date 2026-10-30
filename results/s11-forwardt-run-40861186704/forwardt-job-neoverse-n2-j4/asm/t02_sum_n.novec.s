0000000000000e28 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
     e28:	cbz	x1, e4c <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x24>
     e2c:	ldr	x8, [x0]
     e30:	mov	x9, xzr
     e34:	ldrsw	x10, [x8], #4
     e38:	subs	x1, x1, #0x1
     e3c:	add	x9, x9, x10
     e40:	b.ne	e34 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0xc>  // b.any
     e44:	str	x9, [x2]
     e48:	ret
     e4c:	mov	x9, xzr
     e50:	str	x9, [x2]
     e54:	ret
