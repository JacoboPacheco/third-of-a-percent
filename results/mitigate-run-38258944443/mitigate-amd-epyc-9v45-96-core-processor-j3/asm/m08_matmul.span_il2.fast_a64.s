0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	test   %rcx,%rcx
    128d:	je     15e5 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x365>
    1293:	mov    %rcx,%rbp
    1296:	mov    (%rdi),%r8
    1299:	mov    0x8(%rdi),%rcx
    129d:	sub    %r8,%rcx
    12a0:	sar    $0x2,%rcx
    12a4:	mov    (%rsi),%rax
    12a7:	mov    0x8(%rsi),%rsi
    12ab:	mov    %rax,-0x30(%rsp)
    12b0:	sub    %rax,%rsi
    12b3:	sar    $0x2,%rsi
    12b7:	lea    0x0(,%rbp,4),%rax
    12bf:	mov    %rax,-0x70(%rsp)
    12c4:	lea    -0x1(%rbp),%r10
    12c8:	lea    0x4(%r8),%rax
    12cc:	mov    %rax,-0x38(%rsp)
    12d1:	lea    0x10(%r8),%rbx
    12d5:	xor    %eax,%eax
    12d7:	mov    %r8,%r12
    12da:	mov    %rsi,-0x58(%rsp)
    12df:	mov    %rdx,-0x40(%rsp)
    12e4:	mov    %r8,-0x48(%rsp)
    12e9:	mov    %rcx,-0x50(%rsp)
    12ee:	mov    %rax,-0x68(%rsp)
    12f3:	imul   %rbp,%rax
    12f7:	sub    %rax,%rcx
    12fa:	jb     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    1300:	cmp    $0xffffffffffffffff,%rbp
    1304:	je     1340 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    1306:	cmp    %rbp,%rcx
    1309:	jb     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    130f:	sub    %rax,%rsi
    1312:	jb     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    1318:	mov    %rbp,%rcx
    131b:	mov    %rbp,%r15
    131e:	cmp    %rbp,%rsi
    1321:	jae    134c <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xcc>
    1323:	jmp    15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    1328:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1337:	nopw   0x0(%rax,%rax,1)
    1340:	mov    %rsi,%r15
    1343:	sub    %rax,%r15
    1346:	jb     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    134c:	mov    -0x70(%rsp),%rsi
    1351:	imul   -0x68(%rsp),%rsi
    1357:	lea    (%r8,%rsi,1),%rdi
    135b:	mov    %rdi,-0x10(%rsp)
    1360:	add    -0x38(%rsp),%rsi
    1365:	mov    %rsi,-0x20(%rsp)
    136a:	mov    -0x30(%rsp),%rsi
    136f:	lea    (%rsi,%rax,4),%r9
    1373:	mov    (%rdx),%rax
    1376:	mov    0x8(%rdx),%rdx
    137a:	sub    %rax,%rdx
    137d:	sar    $0x2,%rdx
    1381:	mov    %rdx,-0x8(%rsp)
    1386:	lea    0x4(%rax),%rdx
    138a:	mov    %rdx,-0x18(%rsp)
    138f:	lea    0x10(%rax),%rsi
    1393:	mov    %rax,-0x28(%rsp)
    1398:	xor    %r8d,%r8d
    139b:	mov    %r9,-0x60(%rsp)
    13a0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13af:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13be:	xchg   %ax,%ax
    13c0:	cmp    %r15,%r8
    13c3:	je     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    13c9:	mov    %r8,%r11
    13cc:	imul   %rbp,%r11
    13d0:	mov    -0x8(%rsp),%rdx
    13d5:	sub    %r11,%rdx
    13d8:	jb     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    13de:	mov    (%r9,%r8,4),%r14d
    13e2:	cmp    $0xffffffffffffffff,%rbp
    13e6:	je     13f4 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x174>
    13e8:	cmp    %rbp,%rdx
    13eb:	mov    %rbp,%rdx
    13ee:	jb     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    13f4:	cmp    %rcx,%rdx
    13f7:	mov    %rcx,%r13
    13fa:	cmovb  %rdx,%r13
    13fe:	cmp    %r10,%r13
    1401:	cmovae %r10,%r13
    1405:	inc    %r13
    1408:	cmp    $0x8,%r13
    140c:	ja     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    140e:	xor    %r13d,%r13d
    1411:	jmp    1580 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    1416:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1425:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1434:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1440:	mov    %r15,%r9
    1443:	mov    -0x70(%rsp),%r15
    1448:	imul   %r8,%r15
    144c:	mov    -0x18(%rsp),%rdi
    1451:	add    %r15,%rdi
    1454:	cmp    %rcx,%rdx
    1457:	mov    %rcx,%r11
    145a:	cmovb  %rdx,%r11
    145e:	cmp    %r10,%r11
    1461:	cmovae %r10,%r11
    1465:	lea    (%rdi,%r11,4),%rdi
    1469:	cmp    %rdi,-0x10(%rsp)
    146e:	jae    14c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    1470:	add    -0x28(%rsp),%r15
    1475:	mov    -0x20(%rsp),%rdi
    147a:	lea    (%rdi,%r11,4),%rdi
    147e:	cmp    %rdi,%r15
    1481:	jae    14c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    1483:	xor    %r13d,%r13d
    1486:	jmp    156e <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2ee>
    148b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    149a:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14a9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14b8:	nopl   0x0(%rax,%rax,1)
    14c0:	mov    %r13d,%edi
    14c3:	and    $0x7,%edi
    14c6:	mov    $0x8,%r11d
    14cc:	cmove  %r11,%rdi
    14d0:	sub    %rdi,%r13
    14d3:	movd   %r14d,%xmm0
    14d8:	pshufd $0x0,%xmm0,%xmm0
    14dd:	pshufd $0xf5,%xmm0,%xmm1
    14e2:	xor    %r15d,%r15d
    14e5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14f4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1500:	movdqu -0x10(%rsi,%r15,4),%xmm2
    1507:	movdqu (%rsi,%r15,4),%xmm3
    150d:	pshufd $0xf5,%xmm2,%xmm4
    1512:	pmuludq %xmm0,%xmm2
    1516:	pshufd $0xe8,%xmm2,%xmm2
    151b:	pmuludq %xmm1,%xmm4
    151f:	pshufd $0xe8,%xmm4,%xmm4
    1524:	punpckldq %xmm4,%xmm2
    1528:	pshufd $0xf5,%xmm3,%xmm4
    152d:	pmuludq %xmm0,%xmm3
    1531:	pshufd $0xe8,%xmm3,%xmm3
    1536:	pmuludq %xmm1,%xmm4
    153a:	pshufd $0xe8,%xmm4,%xmm4
    153f:	punpckldq %xmm4,%xmm3
    1543:	movdqu -0x10(%rbx,%r15,4),%xmm4
    154a:	paddd  %xmm2,%xmm4
    154e:	movdqu (%rbx,%r15,4),%xmm2
    1554:	paddd  %xmm3,%xmm2
    1558:	movdqu %xmm4,-0x10(%rbx,%r15,4)
    155f:	movdqu %xmm2,(%rbx,%r15,4)
    1565:	add    $0x8,%r15
    1569:	cmp    %r15,%r13
    156c:	jne    1500 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    156e:	mov    %r9,%r15
    1571:	mov    -0x60(%rsp),%r9
    1576:	cs nopw 0x0(%rax,%rax,1)
    1580:	cmp    %r13,%rdx
    1583:	je     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    1585:	cmp    %r13,%rcx
    1588:	je     15f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x370>
    158a:	mov    (%rax,%r13,4),%edi
    158e:	imul   %r14d,%edi
    1592:	add    %edi,(%r12,%r13,4)
    1596:	inc    %r13
    1599:	cmp    %r13,%rbp
    159c:	jne    1580 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    159e:	inc    %r8
    15a1:	mov    -0x70(%rsp),%rdx
    15a6:	add    %rdx,%rsi
    15a9:	add    %rdx,%rax
    15ac:	cmp    %rbp,%r8
    15af:	jne    13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    15b5:	mov    -0x68(%rsp),%rax
    15ba:	inc    %rax
    15bd:	mov    -0x70(%rsp),%rcx
    15c2:	add    %rcx,%rbx
    15c5:	add    %rcx,%r12
    15c8:	cmp    %rbp,%rax
    15cb:	mov    -0x40(%rsp),%rdx
    15d0:	mov    -0x48(%rsp),%r8
    15d5:	mov    -0x50(%rsp),%rcx
    15da:	mov    -0x58(%rsp),%rsi
    15df:	jne    12ee <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x6e>
    15e5:	pop    %rbx
    15e6:	pop    %r12
    15e8:	pop    %r13
    15ea:	pop    %r14
    15ec:	pop    %r15
    15ee:	pop    %rbp
    15ef:	ret
    15f0:	ud2
    15f2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
