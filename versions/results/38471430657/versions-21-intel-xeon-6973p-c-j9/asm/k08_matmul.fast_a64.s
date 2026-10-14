0000000000001240 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	sub    $0x10,%rsp
    124e:	test   %rcx,%rcx
    1251:	je     15ad <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x36d>
    1257:	mov    (%rsi),%r8
    125a:	mov    0x8(%rsi),%rax
    125e:	mov    %r8,-0x8(%rsp)
    1263:	sub    %r8,%rax
    1266:	sar    $0x2,%rax
    126a:	mov    %rax,(%rsp)
    126e:	lea    0x0(,%rcx,4),%rsi
    1276:	lea    -0x1(%rcx),%rax
    127a:	mov    %rax,-0x70(%rsp)
    127f:	mov    $0x10,%eax
    1284:	mov    %rax,-0x68(%rsp)
    1289:	xor    %r14d,%r14d
    128c:	movq   $0x0,-0x60(%rsp)
    1295:	xor    %eax,%eax
    1297:	mov    %rdx,-0x40(%rsp)
    129c:	mov    %rdi,-0x80(%rsp)
    12a1:	mov    %rsi,-0x50(%rsp)
    12a6:	mov    %rcx,%r11
    12a9:	imul   %rax,%r11
    12ad:	mov    %rsi,%r8
    12b0:	mov    %rax,-0x38(%rsp)
    12b5:	imul   %rax,%r8
    12b9:	mov    %r8,-0x20(%rsp)
    12be:	mov    (%rdx),%rbx
    12c1:	mov    0x8(%rdx),%r12
    12c5:	sub    %rbx,%r12
    12c8:	sar    $0x2,%r12
    12cc:	lea    0x4(%rbx),%rax
    12d0:	mov    %rax,-0x28(%rsp)
    12d5:	lea    0x10(%rbx),%r10
    12d9:	mov    %rbx,-0x30(%rsp)
    12de:	movq   $0x0,-0x58(%rsp)
    12e7:	xor    %ebp,%ebp
    12e9:	xor    %r9d,%r9d
    12ec:	mov    %r11,-0x78(%rsp)
    12f1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	cmp    %rbp,%r12
    1303:	mov    %rbp,%r15
    1306:	cmova  %r12,%r15
    130a:	mov    %rcx,%rax
    130d:	imul   %r9,%rax
    1311:	mov    %r12,%rdx
    1314:	sub    %rax,%rdx
    1317:	mov    $0x0,%r13d
    131d:	cmovae %rdx,%r13
    1321:	lea    (%r9,%r11,1),%r8
    1325:	cmp    (%rsp),%r8
    1329:	jae    15bc <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x37c>
    132f:	mov    %r9,-0x48(%rsp)
    1334:	mov    %r12,%r9
    1337:	sub    %rax,%r9
    133a:	mov    $0x0,%eax
    133f:	cmovb  %rax,%r9
    1343:	mov    (%rdi),%rax
    1346:	mov    0x8(%rdi),%rsi
    134a:	sub    %rax,%rsi
    134d:	sar    $0x2,%rsi
    1351:	cmp    %r11,%rsi
    1354:	mov    %r11,%rdx
    1357:	cmova  %rsi,%rdx
    135b:	sub    %r11,%rdx
    135e:	mov    -0x70(%rsp),%r11
    1363:	cmp    %r11,%rdx
    1366:	mov    -0x78(%rsp),%rdi
    136b:	cmovb  %rdx,%r11
    136f:	cmp    %r9,%r11
    1372:	cmovae %r9,%r11
    1376:	mov    -0x8(%rsp),%r9
    137b:	mov    (%r9,%r8,4),%r8d
    137f:	inc    %r11
    1382:	mov    $0x0,%r9d
    1388:	mov    %r11,0x8(%rsp)
    138d:	cmp    $0x8,%r11
    1391:	mov    %rdi,%r11
    1394:	mov    -0x80(%rsp),%rdi
    1399:	jbe    153b <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2fb>
    139f:	mov    -0x50(%rsp),%r9
    13a4:	imul   -0x48(%rsp),%r9
    13aa:	mov    -0x28(%rsp),%rdi
    13af:	add    %r9,%rdi
    13b2:	mov    %rdi,-0x10(%rsp)
    13b7:	mov    -0x20(%rsp),%rdi
    13bc:	add    %rax,%rdi
    13bf:	mov    %rdi,-0x18(%rsp)
    13c4:	cmp    %r11,%rsi
    13c7:	mov    %r11,%rdi
    13ca:	cmova  %rsi,%r11
    13ce:	sub    %rdi,%r11
    13d1:	mov    -0x70(%rsp),%rdi
    13d6:	cmp    %rdi,%r11
    13d9:	cmovae %rdi,%r11
    13dd:	cmp    %r13,%r11
    13e0:	cmovae %r13,%r11
    13e4:	mov    -0x10(%rsp),%rdi
    13e9:	lea    (%rdi,%r11,4),%rdi
    13ed:	mov    -0x18(%rsp),%r13
    13f2:	cmp    %rdi,%r13
    13f5:	jae    1440 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    13f7:	add    -0x30(%rsp),%r9
    13fc:	lea    0x4(,%r11,4),%rdi
    1404:	add    %r13,%rdi
    1407:	cmp    %rdi,%r9
    140a:	jae    1440 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    140c:	xor    %r9d,%r9d
    140f:	jmp    1531 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2f1>
    1414:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1423:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1432:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1440:	add    -0x58(%rsp),%r15
    1445:	mov    0x8(%rsp),%r11
    144a:	mov    %r11d,%r9d
    144d:	and    $0x7,%r9d
    1451:	mov    $0x8,%edi
    1456:	cmove  %rdi,%r9
    145a:	sub    %r9,%r11
    145d:	movd   %r8d,%xmm0
    1462:	pshufd $0x0,%xmm0,%xmm0
    1467:	cmp    %r15,%rdx
    146a:	cmovb  %rdx,%r15
    146e:	mov    -0x68(%rsp),%rdx
    1473:	lea    (%rax,%rdx,1),%rdi
    1477:	mov    -0x70(%rsp),%rdx
    147c:	cmp    %rdx,%r15
    147f:	cmovae %rdx,%r15
    1483:	sub    %r9,%r15
    1486:	inc    %r15
    1489:	pshufd $0xf5,%xmm0,%xmm1
    148e:	xor    %r13d,%r13d
    1491:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14a0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14af:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14be:	xchg   %ax,%ax
    14c0:	movdqu -0x10(%r10,%r13,4),%xmm2
    14c7:	movdqu (%r10,%r13,4),%xmm3
    14cd:	pshufd $0xf5,%xmm2,%xmm4
    14d2:	pmuludq %xmm0,%xmm2
    14d6:	pshufd $0xe8,%xmm2,%xmm2
    14db:	pmuludq %xmm1,%xmm4
    14df:	pshufd $0xe8,%xmm4,%xmm4
    14e4:	punpckldq %xmm4,%xmm2
    14e8:	pshufd $0xf5,%xmm3,%xmm4
    14ed:	pmuludq %xmm0,%xmm3
    14f1:	pshufd $0xe8,%xmm3,%xmm3
    14f6:	pmuludq %xmm1,%xmm4
    14fa:	pshufd $0xe8,%xmm4,%xmm4
    14ff:	punpckldq %xmm4,%xmm3
    1503:	movdqu -0x10(%rdi,%r13,4),%xmm4
    150a:	paddd  %xmm2,%xmm4
    150e:	movdqu (%rdi,%r13,4),%xmm2
    1514:	paddd  %xmm3,%xmm2
    1518:	movdqu %xmm4,-0x10(%rdi,%r13,4)
    151f:	movdqu %xmm2,(%rdi,%r13,4)
    1525:	add    $0x8,%r13
    1529:	cmp    %r13,%r15
    152c:	jne    14c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    152e:	mov    %r11,%r9
    1531:	mov    -0x80(%rsp),%rdi
    1536:	mov    -0x78(%rsp),%r11
    153b:	add    -0x60(%rsp),%rax
    1540:	lea    (%r9,%rbp,1),%rdx
    1544:	cmp    %r12,%rdx
    1547:	jae    15bc <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x37c>
    1549:	lea    (%r14,%r9,1),%rdx
    154d:	cmp    %rsi,%rdx
    1550:	jae    15bc <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x37c>
    1552:	mov    (%rbx,%r9,4),%edx
    1556:	imul   %r8d,%edx
    155a:	add    %edx,(%rax,%r9,4)
    155e:	inc    %r9
    1561:	cmp    %r9,%rcx
    1564:	jne    1540 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x300>
    1566:	mov    -0x48(%rsp),%r9
    156b:	inc    %r9
    156e:	mov    -0x50(%rsp),%rsi
    1573:	add    %rsi,%r10
    1576:	add    %rcx,%rbp
    1579:	sub    %rcx,-0x58(%rsp)
    157e:	add    %rsi,%rbx
    1581:	cmp    %rcx,%r9
    1584:	jne    1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    158a:	mov    -0x38(%rsp),%rax
    158f:	inc    %rax
    1592:	add    %rsi,-0x68(%rsp)
    1597:	add    %rsi,-0x60(%rsp)
    159c:	add    %rcx,%r14
    159f:	cmp    %rcx,%rax
    15a2:	mov    -0x40(%rsp),%rdx
    15a7:	jne    12a6 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x66>
    15ad:	add    $0x10,%rsp
    15b1:	pop    %rbx
    15b2:	pop    %r12
    15b4:	pop    %r13
    15b6:	pop    %r14
    15b8:	pop    %r15
    15ba:	pop    %rbp
    15bb:	ret
    15bc:	ud2
    15be:	xchg   %ax,%ax
