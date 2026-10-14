0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	test   %rcx,%rcx
    128d:	je     15df <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x35f>
    1293:	mov    %rcx,%r13
    1296:	mov    (%rdi),%r8
    1299:	mov    0x8(%rdi),%rdi
    129d:	sub    %r8,%rdi
    12a0:	sar    $0x2,%rdi
    12a4:	mov    (%rsi),%r11
    12a7:	mov    0x8(%rsi),%rbx
    12ab:	sub    %r11,%rbx
    12ae:	sar    $0x2,%rbx
    12b2:	lea    0x0(,%rcx,4),%rax
    12ba:	mov    %rax,-0x28(%rsp)
    12bf:	lea    -0x1(%rcx),%r10
    12c3:	lea    0x4(%r8),%r14
    12c7:	xor    %esi,%esi
    12c9:	mov    %r8,%r15
    12cc:	mov    %rdx,-0x30(%rsp)
    12d1:	mov    %r8,-0x38(%rsp)
    12d6:	mov    %rdi,-0x40(%rsp)
    12db:	mov    %r11,-0x48(%rsp)
    12e0:	mov    %rbx,-0x50(%rsp)
    12e5:	mov    %r14,-0x58(%rsp)
    12ea:	mov    %rsi,%rax
    12ed:	imul   %r13,%rax
    12f1:	mov    %rdi,%rcx
    12f4:	sub    %rax,%rcx
    12f7:	jb     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    12fd:	cmp    $0xffffffffffffffff,%r13
    1301:	mov    %rsi,-0x68(%rsp)
    1306:	je     1340 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    1308:	cmp    %r13,%rcx
    130b:	jb     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    1311:	mov    %rbx,%rsi
    1314:	sub    %rax,%rsi
    1317:	jb     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    131d:	mov    %r13,%rcx
    1320:	mov    %r13,%r9
    1323:	cmp    %r13,%rsi
    1326:	jae    134c <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xcc>
    1328:	jmp    15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    132d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133c:	nopl   0x0(%rax)
    1340:	mov    %rbx,%r9
    1343:	sub    %rax,%r9
    1346:	jb     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    134c:	mov    -0x28(%rsp),%rsi
    1351:	mov    %rsi,%rdi
    1354:	imul   -0x68(%rsp),%rdi
    135a:	add    %rdi,%r8
    135d:	mov    %r8,-0x8(%rsp)
    1362:	add    %r14,%rdi
    1365:	mov    %rdi,-0x18(%rsp)
    136a:	lea    (%r11,%rax,4),%r8
    136e:	mov    (%rdx),%r14
    1371:	mov    0x8(%rdx),%rbx
    1375:	mov    %rsi,%rbp
    1378:	sub    %r14,%rbx
    137b:	sar    $0x2,%rbx
    137f:	lea    0x4(%r14),%rax
    1383:	mov    %rax,-0x10(%rsp)
    1388:	mov    %r14,-0x20(%rsp)
    138d:	xor    %esi,%esi
    138f:	mov    %rbx,-0x60(%rsp)
    1394:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13a3:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13b2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13c0:	cmp    %r9,%rsi
    13c3:	je     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    13c9:	mov    %rsi,%rdi
    13cc:	imul   %r13,%rdi
    13d0:	mov    %rbx,%rax
    13d3:	sub    %rdi,%rax
    13d6:	jb     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    13dc:	mov    (%r8,%rsi,4),%r11d
    13e0:	cmp    $0xffffffffffffffff,%r13
    13e4:	je     13f2 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x172>
    13e6:	cmp    %r13,%rax
    13e9:	mov    %r13,%rax
    13ec:	jb     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    13f2:	cmp    %rcx,%rax
    13f5:	mov    %rcx,%r12
    13f8:	cmovb  %rax,%r12
    13fc:	cmp    %r10,%r12
    13ff:	cmovae %r10,%r12
    1403:	inc    %r12
    1406:	cmp    $0x4,%r12
    140a:	ja     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    140c:	xor    %r12d,%r12d
    140f:	jmp    1580 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    1414:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1423:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1432:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1440:	mov    %r9,%rbx
    1443:	mov    %r8,%r9
    1446:	mov    %rbp,%rdx
    1449:	mov    %rbp,%rdi
    144c:	imul   %rsi,%rdi
    1450:	mov    -0x10(%rsp),%r8
    1455:	add    %rdi,%r8
    1458:	cmp    %rcx,%rax
    145b:	mov    %rcx,%rbp
    145e:	cmovb  %rax,%rbp
    1462:	cmp    %r10,%rbp
    1465:	cmovae %r10,%rbp
    1469:	lea    (%r8,%rbp,4),%r8
    146d:	cmp    %r8,-0x8(%rsp)
    1472:	jae    14c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    1474:	add    -0x20(%rsp),%rdi
    1479:	mov    -0x18(%rsp),%r8
    147e:	lea    (%r8,%rbp,4),%r8
    1482:	cmp    %r8,%rdi
    1485:	jae    14c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    1487:	xor    %r12d,%r12d
    148a:	jmp    153a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2ba>
    148f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    149e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14ad:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14bc:	nopl   0x0(%rax)
    14c0:	mov    %r12d,%edi
    14c3:	and    $0x3,%edi
    14c6:	mov    $0x4,%r8d
    14cc:	cmove  %r8,%rdi
    14d0:	sub    %rdi,%r12
    14d3:	movd   %r11d,%xmm0
    14d8:	pshufd $0x0,%xmm0,%xmm0
    14dd:	pshufd $0xf5,%xmm0,%xmm1
    14e2:	xor    %edi,%edi
    14e4:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14f3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1500:	movdqu (%r14,%rdi,4),%xmm2
    1506:	pshufd $0xf5,%xmm2,%xmm3
    150b:	pmuludq %xmm0,%xmm2
    150f:	pshufd $0xe8,%xmm2,%xmm2
    1514:	pmuludq %xmm1,%xmm3
    1518:	pshufd $0xe8,%xmm3,%xmm3
    151d:	punpckldq %xmm3,%xmm2
    1521:	movdqu (%r15,%rdi,4),%xmm3
    1527:	paddd  %xmm2,%xmm3
    152b:	movdqu %xmm3,(%r15,%rdi,4)
    1531:	add    $0x4,%rdi
    1535:	cmp    %rdi,%r12
    1538:	jne    1500 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    153a:	mov    %r9,%r8
    153d:	mov    %rbx,%r9
    1540:	mov    -0x60(%rsp),%rbx
    1545:	mov    %rdx,%rbp
    1548:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1557:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1566:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1575:	data16 cs nopw 0x0(%rax,%rax,1)
    1580:	cmp    %r12,%rax
    1583:	je     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    1585:	cmp    %r12,%rcx
    1588:	je     15ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36a>
    158a:	mov    (%r14,%r12,4),%edi
    158e:	imul   %r11d,%edi
    1592:	add    %edi,(%r15,%r12,4)
    1596:	inc    %r12
    1599:	cmp    %r12,%r13
    159c:	jne    1580 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    159e:	inc    %rsi
    15a1:	add    %rbp,%r14
    15a4:	cmp    %r13,%rsi
    15a7:	jne    13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    15ad:	mov    -0x68(%rsp),%rsi
    15b2:	inc    %rsi
    15b5:	add    %rbp,%r15
    15b8:	cmp    %r13,%rsi
    15bb:	mov    -0x30(%rsp),%rdx
    15c0:	mov    -0x38(%rsp),%r8
    15c5:	mov    -0x40(%rsp),%rdi
    15ca:	mov    -0x48(%rsp),%r11
    15cf:	mov    -0x50(%rsp),%rbx
    15d4:	mov    -0x58(%rsp),%r14
    15d9:	jne    12ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x6a>
    15df:	pop    %rbx
    15e0:	pop    %r12
    15e2:	pop    %r13
    15e4:	pop    %r14
    15e6:	pop    %r15
    15e8:	pop    %rbp
    15e9:	ret
    15ea:	ud2
    15ec:	nopl   0x0(%rax)
