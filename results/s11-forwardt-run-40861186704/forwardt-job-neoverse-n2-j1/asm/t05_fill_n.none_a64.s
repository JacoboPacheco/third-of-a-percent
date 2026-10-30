0000000000000b40 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
 b40:	cmp	w1, #0x1
 b44:	b.lt	bd0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x90>  // b.tstop
 b48:	ldr	x8, [x0]
 b4c:	cmp	w1, #0x8
 b50:	mov	w9, w1
 b54:	b.cs	b60 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x20>  // b.hs, b.nlast
 b58:	mov	x10, xzr
 b5c:	b	ba4 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x64>
 b60:	movi	v0.4s, #0x3
 b64:	movi	v1.4s, #0xc
 b68:	adrp	x11, 0 <__abi_tag-0x278>
 b6c:	movi	v2.4s, #0x8
 b70:	and	x10, x9, #0x7ffffff8
 b74:	ldr	q3, [x11, #3648]
 b78:	add	x11, x8, #0x10
 b7c:	mov	x12, x10
 b80:	mul	v4.4s, v3.4s, v0.4s
 b84:	add	v3.4s, v3.4s, v2.4s
 b88:	subs	x12, x12, #0x8
 b8c:	add	v5.4s, v4.4s, v1.4s
 b90:	stp	q4, q5, [x11, #-16]
 b94:	add	x11, x11, #0x20
 b98:	b.ne	b80 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x40>  // b.any
 b9c:	cmp	x10, x9
 ba0:	b.eq	bd0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x90>  // b.none
 ba4:	add	w11, w10, w10, lsl #1
 ba8:	add	x8, x8, x10, lsl #2
 bac:	sub	x9, x9, x10
 bb0:	nop
 bb4:	nop
 bb8:	nop
 bbc:	nop
 bc0:	subs	x9, x9, #0x1
 bc4:	str	w11, [x8], #4
 bc8:	add	w11, w11, #0x3
 bcc:	b.ne	bc0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>  // b.any
 bd0:	ret
