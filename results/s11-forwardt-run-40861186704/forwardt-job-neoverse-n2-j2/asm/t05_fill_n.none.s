0000000000000b28 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
 b28:	cmp	w1, #0x1
 b2c:	b.lt	ba8 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>  // b.tstop
 b30:	ldr	x8, [x0]
 b34:	cmp	w1, #0x8
 b38:	mov	w9, w1
 b3c:	b.cs	b48 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x20>  // b.hs, b.nlast
 b40:	mov	x10, xzr
 b44:	b	b8c <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x64>
 b48:	movi	v0.4s, #0x3
 b4c:	movi	v1.4s, #0xc
 b50:	adrp	x11, 0 <__abi_tag-0x278>
 b54:	movi	v2.4s, #0x8
 b58:	and	x10, x9, #0x7ffffff8
 b5c:	ldr	q3, [x11, #3520]
 b60:	add	x11, x8, #0x10
 b64:	mov	x12, x10
 b68:	mul	v4.4s, v3.4s, v0.4s
 b6c:	add	v3.4s, v3.4s, v2.4s
 b70:	subs	x12, x12, #0x8
 b74:	add	v5.4s, v4.4s, v1.4s
 b78:	stp	q4, q5, [x11, #-16]
 b7c:	add	x11, x11, #0x20
 b80:	b.ne	b68 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x40>  // b.any
 b84:	cmp	x10, x9
 b88:	b.eq	ba8 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>  // b.none
 b8c:	add	w11, w10, w10, lsl #1
 b90:	add	x8, x8, x10, lsl #2
 b94:	sub	x9, x9, x10
 b98:	subs	x9, x9, #0x1
 b9c:	str	w11, [x8], #4
 ba0:	add	w11, w11, #0x3
 ba4:	b.ne	b98 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x70>  // b.any
 ba8:	ret
