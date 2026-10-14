0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	mov    %rdx,-0x40(%rsp)
    128f:	test   %rcx,%rcx
    1292:	je     159a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x31a>
    1298:	mov    (%rdi),%rax
    129b:	mov    0x8(%rdi),%rdx
    129f:	sub    %rax,%rdx
    12a2:	sar    $0x2,%rdx
    12a6:	mov    %rdx,-0x48(%rsp)
    12ab:	mov    (%rsi),%rdx
    12ae:	mov    0x8(%rsi),%rsi
    12b2:	mov    %rdx,-0x58(%rsp)
    12b7:	sub    %rdx,%rsi
    12ba:	sar    $0x2,%rsi
    12be:	mov    %rsi,-0x68(%rsp)
    12c3:	lea    0x0(,%rcx,4),%rdx
    12cb:	mov    %rdx,-0x70(%rsp)
    12d0:	lea    -0x1(%rcx),%rdx
    12d4:	imul   %rcx,%rdx
    12d8:	shl    $0x2,%rdx
    12dc:	mov    %rdx,-0x60(%rsp)
    12e1:	mov    %rax,-0x50(%rsp)
    12e6:	lea    0x10(%rax),%rbx
    12ea:	xor    %esi,%esi
    12ec:	jmp    1316 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x96>
    12ee:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fd:	nopl   (%rax)
    1300:	mov    -0x38(%rsp),%rsi
    1305:	inc    %rsi
    1308:	add    -0x70(%rsp),%rbx
    130d:	cmp    %rcx,%rsi
    1310:	je     159a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x31a>
    1316:	mov    %rsi,%rax
    1319:	imul   %rcx,%rax
    131d:	mov    -0x48(%rsp),%r15
    1322:	sub    %rax,%r15
    1325:	jb     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    132b:	cmp    $0xffffffffffffffff,%rcx
    132f:	je     1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    1331:	cmp    %rcx,%r15
    1334:	jb     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    133a:	mov    -0x68(%rsp),%rdx
    133f:	sub    %rax,%rdx
    1342:	jb     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    1348:	mov    %rcx,%r15
    134b:	mov    %rcx,%r12
    134e:	cmp    %rcx,%rdx
    1351:	jae    138e <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x10e>
    1353:	jmp    15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    1358:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1367:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1376:	cs nopw 0x0(%rax,%rax,1)
    1380:	mov    -0x68(%rsp),%r12
    1385:	sub    %rax,%r12
    1388:	jb     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    138e:	mov    -0x70(%rsp),%rdi
    1393:	mov    %rdi,%rdx
    1396:	mov    %rsi,-0x38(%rsp)
    139b:	imul   %rsi,%rdx
    139f:	mov    -0x50(%rsp),%rsi
    13a4:	add    %rsi,%rdx
    13a7:	test   %rdi,%rdi
    13aa:	sets   %r10b
    13ae:	lea    (%rsi,%rax,4),%r14
    13b2:	mov    -0x58(%rsp),%rsi
    13b7:	lea    (%rsi,%rax,4),%rbp
    13bb:	mov    -0x40(%rsp),%rax
    13c0:	mov    (%rax),%r13
    13c3:	mov    0x8(%rax),%r9
    13c7:	sub    %r13,%r9
    13ca:	sar    $0x2,%r9
    13ce:	lea    (%r14,%r15,4),%rdi
    13d2:	lea    (%rdx,%r15,4),%rax
    13d6:	mov    -0x60(%rsp),%rsi
    13db:	add    %r13,%rsi
    13de:	lea    (%rsi,%r15,4),%r8
    13e2:	movabs $0x3fffffffffffffff,%rsi
    13ec:	lea    (%r15,%rsi,1),%r11
    13f0:	and    %rsi,%r11
    13f3:	mov    %r11,-0x10(%rsp)
    13f8:	inc    %r11
    13fb:	cmp    %r8,%rdx
    13fe:	setb   %dl
    1401:	cmp    %rax,%r13
    1404:	setb   %r8b
    1408:	and    %dl,%r8b
    140b:	or     %r10b,%r8b
    140e:	mov    %r11,-0x20(%rsp)
    1413:	and    $0xfffffffffffffff8,%r11
    1417:	lea    0x0(,%r11,4),%rax
    141f:	mov    %rax,-0x28(%rsp)
    1424:	mov    %r14,-0x18(%rsp)
    1429:	lea    (%r14,%r11,4),%rax
    142d:	mov    %rax,-0x30(%rsp)
    1432:	mov    %r13,-0x8(%rsp)
    1437:	lea    0x10(%r13),%r14
    143b:	xor    %r13d,%r13d
    143e:	jmp    1451 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1d1>
    1440:	inc    %r13
    1443:	add    -0x70(%rsp),%r14
    1448:	cmp    %rcx,%r13
    144b:	je     1300 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1451:	cmp    %r12,%r13
    1454:	je     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    145a:	mov    %r13,%rax
    145d:	imul   %rcx,%rax
    1461:	mov    %r9,%r10
    1464:	sub    %rax,%r10
    1467:	jb     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    146d:	mov    0x0(%rbp,%r13,4),%edx
    1472:	cmp    $0xffffffffffffffff,%rcx
    1476:	je     1481 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x201>
    1478:	cmp    %rcx,%r10
    147b:	jb     15a5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x325>
    1481:	test   %r15,%r15
    1484:	je     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    1486:	cmpq   $0x7,-0x10(%rsp)
    148c:	setb   %r10b
    1490:	mov    -0x8(%rsp),%rsi
    1495:	lea    (%rsi,%rax,4),%rax
    1499:	or     %r8b,%r10b
    149c:	je     14c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    149e:	mov    -0x18(%rsp),%r10
    14a3:	jmp    1580 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    14a8:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14b7:	nopw   0x0(%rax,%rax,1)
    14c0:	add    -0x28(%rsp),%rax
    14c5:	movd   %edx,%xmm0
    14c9:	pshufd $0x0,%xmm0,%xmm0
    14ce:	pshufd $0xf5,%xmm0,%xmm1
    14d3:	xor    %r10d,%r10d
    14d6:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14e5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14f4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1500:	movdqu -0x10(%rbx,%r10,4),%xmm2
    1507:	movdqu (%rbx,%r10,4),%xmm3
    150d:	movdqu -0x10(%r14,%r10,4),%xmm4
    1514:	movdqu (%r14,%r10,4),%xmm5
    151a:	pshufd $0xf5,%xmm4,%xmm6
    151f:	pmuludq %xmm0,%xmm4
    1523:	pshufd $0xe8,%xmm4,%xmm4
    1528:	pmuludq %xmm1,%xmm6
    152c:	pshufd $0xe8,%xmm6,%xmm6
    1531:	punpckldq %xmm6,%xmm4
    1535:	paddd  %xmm2,%xmm4
    1539:	pshufd $0xf5,%xmm5,%xmm2
    153e:	pmuludq %xmm0,%xmm5
    1542:	pshufd $0xe8,%xmm5,%xmm5
    1547:	pmuludq %xmm1,%xmm2
    154b:	pshufd $0xe8,%xmm2,%xmm2
    1550:	punpckldq %xmm2,%xmm5
    1554:	paddd  %xmm3,%xmm5
    1558:	movdqu %xmm4,-0x10(%rbx,%r10,4)
    155f:	movdqu %xmm5,(%rbx,%r10,4)
    1565:	add    $0x8,%r10
    1569:	cmp    %r10,%r11
    156c:	jne    1500 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    156e:	mov    -0x30(%rsp),%r10
    1573:	cmp    %r11,-0x20(%rsp)
    1578:	je     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    157e:	xchg   %ax,%ax
    1580:	mov    (%rax),%esi
    1582:	imul   %edx,%esi
    1585:	add    %esi,(%r10)
    1588:	add    $0x4,%r10
    158c:	add    $0x4,%rax
    1590:	cmp    %rdi,%r10
    1593:	jne    1580 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    1595:	jmp    1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    159a:	pop    %rbx
    159b:	pop    %r12
    159d:	pop    %r13
    159f:	pop    %r14
    15a1:	pop    %r15
    15a3:	pop    %rbp
    15a4:	ret
    15a5:	ud2
    15a7:	nopw   0x0(%rax,%rax,1)
