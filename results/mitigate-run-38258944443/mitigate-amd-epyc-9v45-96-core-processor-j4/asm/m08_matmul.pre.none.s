0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	mov    %rdx,%r8
    124d:	mov    %rcx,%rax
    1250:	mul    %rcx
    1253:	jo     14c3 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x283>
    1259:	mov    (%rsi),%r9
    125c:	mov    0x8(%rsi),%rdx
    1260:	mov    %r9,-0x18(%rsp)
    1265:	sub    %r9,%rdx
    1268:	sar    $0x2,%rdx
    126c:	cmp    %rax,%rdx
    126f:	jb     14c3 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x283>
    1275:	mov    (%r8),%rsi
    1278:	mov    0x8(%r8),%rdx
    127c:	mov    %rsi,-0x40(%rsp)
    1281:	sub    %rsi,%rdx
    1284:	sar    $0x2,%rdx
    1288:	cmp    %rax,%rdx
    128b:	jb     14c3 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x283>
    1291:	mov    (%rdi),%rsi
    1294:	mov    0x8(%rdi),%rdx
    1298:	mov    %rsi,-0x38(%rsp)
    129d:	sub    %rsi,%rdx
    12a0:	sar    $0x2,%rdx
    12a4:	cmp    %rax,%rdx
    12a7:	jb     14c3 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x283>
    12ad:	test   %rcx,%rcx
    12b0:	je     14b8 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x278>
    12b6:	lea    0x0(,%rcx,4),%rax
    12be:	mov    %rcx,%rdx
    12c1:	imul   %rcx,%rdx
    12c5:	mov    -0x40(%rsp),%rsi
    12ca:	lea    (%rsi,%rdx,4),%rdx
    12ce:	mov    %rdx,-0x20(%rsp)
    12d3:	mov    -0x38(%rsp),%r12
    12d8:	lea    (%r12,%rcx,4),%rdx
    12dc:	mov    %rdx,-0x28(%rsp)
    12e1:	mov    %rcx,%r10
    12e4:	and    $0xfffffffffffffff8,%r10
    12e8:	lea    -0x1(%rcx),%r11
    12ec:	lea    0x10(%rsi),%rdx
    12f0:	mov    %rdx,-0x30(%rsp)
    12f5:	lea    0x10(%r12),%r14
    12fa:	xor    %r8d,%r8d
    12fd:	jmp    1317 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xd7>
    12ff:	nop
    1300:	mov    -0x10(%rsp),%r8
    1305:	inc    %r8
    1308:	add    %rax,%r14
    130b:	add    %rax,%r12
    130e:	cmp    %rcx,%r8
    1311:	je     14b8 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x278>
    1317:	test   %rax,%rax
    131a:	sets   %sil
    131e:	mov    %rax,%rdx
    1321:	imul   %r8,%rdx
    1325:	mov    -0x38(%rsp),%rbx
    132a:	lea    (%rbx,%rdx,1),%rdi
    132e:	add    -0x28(%rsp),%rdx
    1333:	mov    %r8,-0x10(%rsp)
    1338:	imul   %rcx,%r8
    133c:	mov    -0x18(%rsp),%r9
    1341:	lea    (%r9,%r8,4),%r13
    1345:	lea    (%rbx,%r8,4),%r8
    1349:	mov    %r8,-0x8(%rsp)
    134e:	cmp    -0x20(%rsp),%rdi
    1353:	setb   %dil
    1357:	mov    -0x40(%rsp),%r8
    135c:	cmp    %rdx,%r8
    135f:	setb   %dl
    1362:	and    %dil,%dl
    1365:	or     %sil,%dl
    1368:	mov    %r8,%rsi
    136b:	mov    -0x30(%rsp),%rbx
    1370:	xor    %edi,%edi
    1372:	jmp    1392 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x152>
    1374:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	inc    %rdi
    1383:	add    %rax,%rbx
    1386:	add    %rax,%rsi
    1389:	cmp    %rcx,%rdi
    138c:	je     1300 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    1392:	cmp    $0x8,%rcx
    1396:	setb   %r9b
    139a:	mov    0x0(%r13,%rdi,4),%r8d
    139f:	or     %dl,%r9b
    13a2:	je     13b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x170>
    13a4:	xor    %r9d,%r9d
    13a7:	jmp    144a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x20a>
    13ac:	nopl   0x0(%rax)
    13b0:	movd   %r8d,%xmm0
    13b5:	pshufd $0x0,%xmm0,%xmm0
    13ba:	pshufd $0xf5,%xmm0,%xmm1
    13bf:	xor    %r15d,%r15d
    13c2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13d0:	movdqu -0x10(%rbx,%r15,4),%xmm2
    13d7:	movdqu (%rbx,%r15,4),%xmm3
    13dd:	pshufd $0xf5,%xmm2,%xmm4
    13e2:	pmuludq %xmm0,%xmm2
    13e6:	pshufd $0xe8,%xmm2,%xmm2
    13eb:	pmuludq %xmm1,%xmm4
    13ef:	pshufd $0xe8,%xmm4,%xmm4
    13f4:	punpckldq %xmm4,%xmm2
    13f8:	pshufd $0xf5,%xmm3,%xmm4
    13fd:	pmuludq %xmm0,%xmm3
    1401:	pshufd $0xe8,%xmm3,%xmm3
    1406:	pmuludq %xmm1,%xmm4
    140a:	pshufd $0xe8,%xmm4,%xmm4
    140f:	punpckldq %xmm4,%xmm3
    1413:	movdqu -0x10(%r14,%r15,4),%xmm4
    141a:	paddd  %xmm2,%xmm4
    141e:	movdqu (%r14,%r15,4),%xmm2
    1424:	paddd  %xmm3,%xmm2
    1428:	movdqu %xmm4,-0x10(%r14,%r15,4)
    142f:	movdqu %xmm2,(%r14,%r15,4)
    1435:	add    $0x8,%r15
    1439:	cmp    %r15,%r10
    143c:	jne    13d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x190>
    143e:	mov    %r10,%r9
    1441:	cmp    %rcx,%r10
    1444:	je     1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    144a:	mov    %r9,%r15
    144d:	test   $0x1,%cl
    1450:	je     1482 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x242>
    1452:	mov    %rdi,%r15
    1455:	imul   %rcx,%r15
    1459:	mov    -0x40(%rsp),%rbp
    145e:	lea    0x0(,%r15,4),%r15
    1466:	add    %rbp,%r15
    1469:	mov    (%r15,%r9,4),%r15d
    146d:	imul   %r8d,%r15d
    1471:	mov    -0x8(%rsp),%rbp
    1476:	add    %r15d,0x0(%rbp,%r9,4)
    147b:	mov    %r9,%r15
    147e:	or     $0x1,%r15
    1482:	cmp    %r11,%r9
    1485:	je     1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    148b:	nopl   0x0(%rax,%rax,1)
    1490:	mov    (%rsi,%r15,4),%r9d
    1494:	imul   %r8d,%r9d
    1498:	add    %r9d,(%r12,%r15,4)
    149c:	mov    0x4(%rsi,%r15,4),%r9d
    14a1:	imul   %r8d,%r9d
    14a5:	add    %r9d,0x4(%r12,%r15,4)
    14aa:	add    $0x2,%r15
    14ae:	cmp    %r15,%rcx
    14b1:	jne    1490 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x250>
    14b3:	jmp    1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    14b8:	pop    %rbx
    14b9:	pop    %r12
    14bb:	pop    %r13
    14bd:	pop    %r14
    14bf:	pop    %r15
    14c1:	pop    %rbp
    14c2:	ret
    14c3:	ud2
    14c5:	data16 cs nopw 0x0(%rax,%rax,1)
