0000000000001220 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	push   %rbx
    1221:	mov    (%rsi),%rax
    1224:	mov    0x8(%rsi),%rcx
    1228:	sub    %rax,%rcx
    122b:	sar    $0x2,%rcx
    122f:	cmp    $0x3,%rcx
    1233:	jb     1365 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x145>
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
    1270:	jbe    1330 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    1276:	cmp    %r10,%r11
    1279:	cmovb  %r11,%r10
    127d:	lea    0x4(%rdx),%r11
    1281:	lea    (%rdx,%r10,4),%rbx
    1285:	add    $0x8,%rbx
    1289:	lea    (%rax,%r10,4),%r10
    128d:	add    $0xc,%r10
    1291:	cmp    %r10,%r11
    1294:	setb   %r10b
    1298:	cmp    %rbx,%rax
    129b:	setb   %r11b
    129f:	test   %r11b,%r10b
    12a2:	jne    1330 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    12a8:	inc    %r9
    12ab:	mov    %r9d,%edi
    12ae:	and    $0x7,%edi
    12b1:	mov    $0x8,%r8d
    12b7:	cmovne %rdi,%r8
    12bb:	mov    %r9,%r10
    12be:	sub    %r8,%r10
    12c1:	neg    %r8
    12c4:	add    %r9,%r8
    12c7:	add    $0x2,%r8
    12cb:	lea    0x1(%r10),%rdi
    12cf:	xor    %r9d,%r9d
    12d2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e0:	movdqu (%rax,%r9,4),%xmm0
    12e6:	movdqu 0x4(%rax,%r9,4),%xmm1
    12ed:	paddd  %xmm0,%xmm1
    12f1:	movdqu 0x8(%rax,%r9,4),%xmm0
    12f8:	paddd  %xmm1,%xmm0
    12fc:	movdqu 0x10(%rax,%r9,4),%xmm1
    1303:	movdqu 0x14(%rax,%r9,4),%xmm2
    130a:	paddd  %xmm1,%xmm2
    130e:	movdqu 0x18(%rax,%r9,4),%xmm1
    1315:	paddd  %xmm2,%xmm1
    1319:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1320:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1327:	add    $0x8,%r9
    132b:	cmp    %r9,%r10
    132e:	jne    12e0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1330:	inc    %rsi
    1333:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	cmp    %r8,%rsi
    1343:	je     1367 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x147>
    1345:	mov    %r8,%r9
    1348:	mov    (%rax,%rdi,4),%r8d
    134c:	add    -0x4(%rax,%rdi,4),%r8d
    1351:	add    (%rax,%r9,4),%r8d
    1355:	mov    %r8d,(%rdx,%rdi,4)
    1359:	lea    0x1(%r9),%r8
    135d:	mov    %r9,%rdi
    1360:	cmp    %r8,%rcx
    1363:	jne    1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x120>
    1365:	pop    %rbx
    1366:	ret
    1367:	ud2
    1369:	nopl   0x0(%rax)
