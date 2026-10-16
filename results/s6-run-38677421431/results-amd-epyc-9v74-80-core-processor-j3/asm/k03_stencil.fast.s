0000000000001220 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	push   %rbx
    1221:	mov    (%rsi),%rax
    1224:	mov    0x8(%rsi),%rcx
    1228:	sub    %rax,%rcx
    122b:	sar    $0x2,%rcx
    122f:	cmp    $0x3,%rcx
    1233:	jb     1355 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x135>
    1239:	mov    (%rdi),%rdx
    123c:	mov    0x8(%rdi),%rsi
    1240:	sub    %rdx,%rsi
    1243:	sar    $0x2,%rsi
    1247:	cmp    $0x1,%rsi
    124b:	adc    $0x0,%rsi
    124f:	lea    -0x1(%rsi),%r11
    1253:	lea    -0x3(%rcx),%r10
    1257:	cmp    %r10,%r11
    125a:	mov    %r10,%r9
    125d:	cmovb  %r11,%r9
    1261:	mov    $0x1,%edi
    1266:	mov    $0x2,%r8d
    126c:	cmp    $0xb,%r9
    1270:	jbe    1320 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1276:	lea    0x4(%rdx),%rbx
    127a:	cmp    %r10,%r11
    127d:	cmovb  %r11,%r10
    1281:	lea    (%rax,%r10,4),%r11
    1285:	add    $0xc,%r11
    1289:	cmp    %r11,%rbx
    128c:	jae    129f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7f>
    128e:	lea    (%rdx,%r10,4),%r10
    1292:	add    $0x8,%r10
    1296:	cmp    %r10,%rax
    1299:	jb     1320 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    129f:	inc    %r9
    12a2:	mov    %r9d,%edi
    12a5:	and    $0x7,%edi
    12a8:	mov    $0x8,%r8d
    12ae:	cmovne %rdi,%r8
    12b2:	mov    %r9,%r10
    12b5:	sub    %r8,%r10
    12b8:	neg    %r8
    12bb:	add    %r9,%r8
    12be:	add    $0x2,%r8
    12c2:	lea    0x1(%r10),%rdi
    12c6:	xor    %r9d,%r9d
    12c9:	nopl   0x0(%rax)
    12d0:	movdqu (%rax,%r9,4),%xmm0
    12d6:	movdqu 0x4(%rax,%r9,4),%xmm1
    12dd:	paddd  %xmm0,%xmm1
    12e1:	movdqu 0x8(%rax,%r9,4),%xmm0
    12e8:	paddd  %xmm1,%xmm0
    12ec:	movdqu 0x10(%rax,%r9,4),%xmm1
    12f3:	movdqu 0x14(%rax,%r9,4),%xmm2
    12fa:	paddd  %xmm1,%xmm2
    12fe:	movdqu 0x18(%rax,%r9,4),%xmm1
    1305:	paddd  %xmm2,%xmm1
    1309:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1310:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1317:	add    $0x8,%r9
    131b:	cmp    %r9,%r10
    131e:	jne    12d0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>
    1320:	inc    %rsi
    1323:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1330:	cmp    %r8,%rsi
    1333:	je     1357 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1335:	mov    %r8,%r9
    1338:	mov    (%rax,%rdi,4),%r8d
    133c:	add    -0x4(%rax,%rdi,4),%r8d
    1341:	add    (%rax,%r9,4),%r8d
    1345:	mov    %r8d,(%rdx,%rdi,4)
    1349:	lea    0x1(%r9),%r8
    134d:	mov    %r9,%rdi
    1350:	cmp    %r8,%rcx
    1353:	jne    1330 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    1355:	pop    %rbx
    1356:	ret
    1357:	ud2
    1359:	nopl   0x0(%rax)
