0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	test   %rcx,%rcx
    1283:	je     1526 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2a6>
    1289:	push   %rbp
    128a:	push   %r15
    128c:	push   %r14
    128e:	push   %r13
    1290:	push   %r12
    1292:	push   %rbx
    1293:	mov    (%rdi),%r8
    1296:	mov    0x8(%rdi),%rax
    129a:	sub    %r8,%rax
    129d:	sar    $0x2,%rax
    12a1:	mov    %rax,-0x38(%rsp)
    12a6:	mov    (%rsi),%rax
    12a9:	mov    %rax,-0x40(%rsp)
    12ae:	mov    (%rdx),%rdx
    12b1:	lea    0x0(,%rcx,4),%r9
    12b9:	lea    -0x1(%rcx),%rax
    12bd:	imul   %rcx,%rax
    12c1:	lea    (%rdx,%rax,4),%rax
    12c5:	add    $0x4,%rax
    12c9:	mov    %rax,-0x48(%rsp)
    12ce:	lea    0x4(%r8),%rax
    12d2:	mov    %rax,-0x50(%rsp)
    12d7:	mov    %rdx,-0x60(%rsp)
    12dc:	lea    0x10(%rdx),%rax
    12e0:	mov    %rax,-0x58(%rsp)
    12e5:	mov    %r8,-0x30(%rsp)
    12ea:	lea    0x10(%r8),%r14
    12ee:	xor    %eax,%eax
    12f0:	jmp    1314 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x94>
    12f2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	mov    -0x28(%rsp),%rax
    1305:	inc    %rax
    1308:	add    %r9,%r14
    130b:	cmp    %rcx,%rax
    130e:	je     151c <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x29c>
    1314:	test   %r9,%r9
    1317:	sets   %dil
    131b:	mov    %r9,%r8
    131e:	imul   %rax,%r8
    1322:	mov    -0x30(%rsp),%rdx
    1327:	lea    (%rdx,%r8,1),%r10
    132b:	add    -0x50(%rsp),%r8
    1330:	mov    %rax,-0x28(%rsp)
    1335:	imul   %rcx,%rax
    1339:	mov    -0x38(%rsp),%r12
    133e:	sub    %rax,%r12
    1341:	cmp    $0xffffffffffffffff,%rcx
    1345:	cmovne %rcx,%r12
    1349:	lea    (%rdx,%rax,4),%rbx
    134d:	mov    -0x40(%rsp),%rdx
    1352:	lea    (%rdx,%rax,4),%rbp
    1356:	lea    (%rbx,%r12,4),%rax
    135a:	movabs $0x3fffffffffffffff,%rdx
    1364:	lea    (%r12,%rdx,1),%rsi
    1368:	and    %rdx,%rsi
    136b:	lea    (%r8,%rsi,4),%r8
    136f:	mov    -0x48(%rsp),%rdx
    1374:	lea    (%rdx,%rsi,4),%r11
    1378:	lea    0x1(%rsi),%rdx
    137c:	cmp    %r11,%r10
    137f:	setb   %r10b
    1383:	cmp    %r8,-0x60(%rsp)
    1388:	setb   %r11b
    138c:	and    %r10b,%r11b
    138f:	or     %dil,%r11b
    1392:	mov    %rdx,-0x10(%rsp)
    1397:	mov    %rdx,%r10
    139a:	and    $0xfffffffffffffff8,%r10
    139e:	lea    0x0(,%r10,4),%rdx
    13a6:	mov    %rdx,-0x18(%rsp)
    13ab:	mov    %rbx,-0x8(%rsp)
    13b0:	lea    (%rbx,%r10,4),%rdx
    13b4:	mov    %rdx,-0x20(%rsp)
    13b9:	mov    -0x58(%rsp),%r15
    13be:	xor    %edi,%edi
    13c0:	jmp    140f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x18f>
    13c2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13d1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13e0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13ef:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13fe:	xchg   %ax,%ax
    1400:	inc    %rdi
    1403:	add    %r9,%r15
    1406:	cmp    %rcx,%rdi
    1409:	je     1300 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    140f:	test   %r12,%r12
    1412:	je     1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    1414:	mov    0x0(%rbp,%rdi,4),%ebx
    1418:	cmp    $0x7,%rsi
    141c:	setb   %r13b
    1420:	mov    %rdi,%r8
    1423:	imul   %rcx,%r8
    1427:	mov    -0x60(%rsp),%rdx
    142c:	lea    (%rdx,%r8,4),%r8
    1430:	or     %r11b,%r13b
    1433:	je     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    1435:	mov    -0x8(%rsp),%r13
    143a:	jmp    1500 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    143f:	nop
    1440:	add    -0x18(%rsp),%r8
    1445:	movd   %ebx,%xmm0
    1449:	pshufd $0x0,%xmm0,%xmm0
    144e:	pshufd $0xf5,%xmm0,%xmm1
    1453:	xor    %r13d,%r13d
    1456:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1465:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1474:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1480:	movdqu -0x10(%r14,%r13,4),%xmm2
    1487:	movdqu (%r14,%r13,4),%xmm3
    148d:	movdqu -0x10(%r15,%r13,4),%xmm4
    1494:	movdqu (%r15,%r13,4),%xmm5
    149a:	pshufd $0xf5,%xmm4,%xmm6
    149f:	pmuludq %xmm0,%xmm4
    14a3:	pshufd $0xe8,%xmm4,%xmm4
    14a8:	pmuludq %xmm1,%xmm6
    14ac:	pshufd $0xe8,%xmm6,%xmm6
    14b1:	punpckldq %xmm6,%xmm4
    14b5:	paddd  %xmm2,%xmm4
    14b9:	pshufd $0xf5,%xmm5,%xmm2
    14be:	pmuludq %xmm0,%xmm5
    14c2:	pshufd $0xe8,%xmm5,%xmm5
    14c7:	pmuludq %xmm1,%xmm2
    14cb:	pshufd $0xe8,%xmm2,%xmm2
    14d0:	punpckldq %xmm2,%xmm5
    14d4:	paddd  %xmm3,%xmm5
    14d8:	movdqu %xmm4,-0x10(%r14,%r13,4)
    14df:	movdqu %xmm5,(%r14,%r13,4)
    14e5:	add    $0x8,%r13
    14e9:	cmp    %r13,%r10
    14ec:	jne    1480 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    14ee:	mov    -0x20(%rsp),%r13
    14f3:	cmp    %r10,-0x10(%rsp)
    14f8:	je     1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    14fe:	xchg   %ax,%ax
    1500:	mov    (%r8),%edx
    1503:	imul   %ebx,%edx
    1506:	add    %edx,0x0(%r13)
    150a:	add    $0x4,%r13
    150e:	add    $0x4,%r8
    1512:	cmp    %rax,%r13
    1515:	jne    1500 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    1517:	jmp    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    151c:	pop    %rbx
    151d:	pop    %r12
    151f:	pop    %r13
    1521:	pop    %r14
    1523:	pop    %r15
    1525:	pop    %rbp
    1526:	ret
    1527:	nopw   0x0(%rax,%rax,1)
