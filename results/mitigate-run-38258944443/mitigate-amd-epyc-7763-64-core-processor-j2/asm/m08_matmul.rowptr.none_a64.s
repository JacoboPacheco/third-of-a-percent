0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	mov    %rdx,%r8
    128d:	mov    %rcx,%rax
    1290:	mul    %rcx
    1293:	jo     1574 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2f4>
    1299:	mov    (%rsi),%r9
    129c:	mov    0x8(%rsi),%rdx
    12a0:	mov    %r9,-0x18(%rsp)
    12a5:	sub    %r9,%rdx
    12a8:	sar    $0x2,%rdx
    12ac:	cmp    %rax,%rdx
    12af:	jb     1574 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2f4>
    12b5:	mov    (%r8),%rsi
    12b8:	mov    0x8(%r8),%rdx
    12bc:	mov    %rsi,-0x48(%rsp)
    12c1:	sub    %rsi,%rdx
    12c4:	sar    $0x2,%rdx
    12c8:	cmp    %rax,%rdx
    12cb:	jb     1574 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2f4>
    12d1:	mov    (%rdi),%rsi
    12d4:	mov    0x8(%rdi),%rdx
    12d8:	mov    %rsi,-0x40(%rsp)
    12dd:	sub    %rsi,%rdx
    12e0:	sar    $0x2,%rdx
    12e4:	cmp    %rax,%rdx
    12e7:	jb     1574 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2f4>
    12ed:	test   %rcx,%rcx
    12f0:	je     1569 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e9>
    12f6:	lea    0x0(,%rcx,4),%rax
    12fe:	mov    %rcx,%rdx
    1301:	imul   %rcx,%rdx
    1305:	mov    -0x48(%rsp),%rsi
    130a:	lea    (%rsi,%rdx,4),%rdx
    130e:	mov    %rdx,-0x20(%rsp)
    1313:	mov    -0x40(%rsp),%r13
    1318:	lea    0x0(,%rcx,4),%rdx
    1320:	add    %r13,%rdx
    1323:	mov    %rdx,-0x28(%rsp)
    1328:	mov    %rcx,%r10
    132b:	and    $0xfffffffffffffff8,%r10
    132f:	lea    -0x1(%rcx),%r11
    1333:	lea    0x10(%rsi),%rdx
    1337:	mov    %rdx,-0x30(%rsp)
    133c:	lea    0x10(%r13),%r14
    1340:	lea    0x4(%rsi),%rdx
    1344:	mov    %rdx,-0x38(%rsp)
    1349:	xor    %edx,%edx
    134b:	jmp    1397 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x117>
    134d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    135c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137a:	nopw   0x0(%rax,%rax,1)
    1380:	mov    -0x10(%rsp),%rdx
    1385:	inc    %rdx
    1388:	add    %rax,%r14
    138b:	add    %rax,%r13
    138e:	cmp    %rcx,%rdx
    1391:	je     1569 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e9>
    1397:	test   %rax,%rax
    139a:	sets   %sil
    139e:	mov    %rax,%rdi
    13a1:	imul   %rdx,%rdi
    13a5:	mov    -0x40(%rsp),%r9
    13aa:	lea    (%r9,%rdi,1),%r8
    13ae:	add    -0x28(%rsp),%rdi
    13b3:	mov    %rdx,-0x10(%rsp)
    13b8:	imul   %rcx,%rdx
    13bc:	lea    (%r9,%rdx,4),%r9
    13c0:	mov    %r9,-0x8(%rsp)
    13c5:	mov    -0x18(%rsp),%r9
    13ca:	lea    (%r9,%rdx,4),%rdx
    13ce:	cmp    -0x20(%rsp),%r8
    13d3:	setb   %r8b
    13d7:	cmp    %rdi,-0x48(%rsp)
    13dc:	setb   %dil
    13e0:	and    %r8b,%dil
    13e3:	or     %sil,%dil
    13e6:	mov    -0x38(%rsp),%r15
    13eb:	mov    -0x30(%rsp),%rbx
    13f0:	xor    %r9d,%r9d
    13f3:	jmp    1412 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x192>
    13f5:	data16 cs nopw 0x0(%rax,%rax,1)
    1400:	inc    %r9
    1403:	add    %rax,%rbx
    1406:	add    %rax,%r15
    1409:	cmp    %rcx,%r9
    140c:	je     1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    1412:	cmp    $0x8,%rcx
    1416:	setb   %sil
    141a:	mov    (%rdx,%r9,4),%r8d
    141e:	or     %dil,%sil
    1421:	je     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    1423:	xor    %esi,%esi
    1425:	jmp    14fa <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x27a>
    142a:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1439:	nopl   0x0(%rax)
    1440:	movd   %r8d,%xmm0
    1445:	pshufd $0x0,%xmm0,%xmm0
    144a:	pshufd $0xf5,%xmm0,%xmm1
    144f:	xor    %r12d,%r12d
    1452:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1461:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1470:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    147f:	nop
    1480:	movdqu -0x10(%rbx,%r12,4),%xmm2
    1487:	movdqu (%rbx,%r12,4),%xmm3
    148d:	pshufd $0xf5,%xmm2,%xmm4
    1492:	pmuludq %xmm0,%xmm2
    1496:	pshufd $0xe8,%xmm2,%xmm2
    149b:	pmuludq %xmm1,%xmm4
    149f:	pshufd $0xe8,%xmm4,%xmm4
    14a4:	punpckldq %xmm4,%xmm2
    14a8:	pshufd $0xf5,%xmm3,%xmm4
    14ad:	pmuludq %xmm0,%xmm3
    14b1:	pshufd $0xe8,%xmm3,%xmm3
    14b6:	pmuludq %xmm1,%xmm4
    14ba:	pshufd $0xe8,%xmm4,%xmm4
    14bf:	punpckldq %xmm4,%xmm3
    14c3:	movdqu -0x10(%r14,%r12,4),%xmm4
    14ca:	paddd  %xmm2,%xmm4
    14ce:	movdqu (%r14,%r12,4),%xmm2
    14d4:	paddd  %xmm3,%xmm2
    14d8:	movdqu %xmm4,-0x10(%r14,%r12,4)
    14df:	movdqu %xmm2,(%r14,%r12,4)
    14e5:	add    $0x8,%r12
    14e9:	cmp    %r12,%r10
    14ec:	jne    1480 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    14ee:	mov    %r10,%rsi
    14f1:	cmp    %rcx,%r10
    14f4:	je     1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    14fa:	mov    %rsi,%r12
    14fd:	test   $0x1,%cl
    1500:	je     1532 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2b2>
    1502:	mov    %r9,%r12
    1505:	imul   %rcx,%r12
    1509:	mov    -0x48(%rsp),%rbp
    150e:	lea    0x0(,%r12,4),%r12
    1516:	add    %rbp,%r12
    1519:	mov    (%r12,%rsi,4),%r12d
    151d:	imul   %r8d,%r12d
    1521:	mov    -0x8(%rsp),%rbp
    1526:	add    %r12d,0x0(%rbp,%rsi,4)
    152b:	mov    %rsi,%r12
    152e:	or     $0x1,%r12
    1532:	cmp    %r11,%rsi
    1535:	je     1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    153b:	nopl   0x0(%rax,%rax,1)
    1540:	mov    -0x4(%r15,%r12,4),%esi
    1545:	imul   %r8d,%esi
    1549:	add    %esi,0x0(%r13,%r12,4)
    154e:	mov    (%r15,%r12,4),%esi
    1552:	imul   %r8d,%esi
    1556:	add    %esi,0x4(%r13,%r12,4)
    155b:	add    $0x2,%r12
    155f:	cmp    %r12,%rcx
    1562:	jne    1540 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c0>
    1564:	jmp    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    1569:	pop    %rbx
    156a:	pop    %r12
    156c:	pop    %r13
    156e:	pop    %r14
    1570:	pop    %r15
    1572:	pop    %rbp
    1573:	ret
    1574:	ud2
    1576:	cs nopw 0x0(%rax,%rax,1)
