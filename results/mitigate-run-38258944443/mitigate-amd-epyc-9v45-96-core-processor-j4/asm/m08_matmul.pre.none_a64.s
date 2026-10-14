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
    1293:	jo     1533 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2b3>
    1299:	mov    (%rsi),%r9
    129c:	mov    0x8(%rsi),%rdx
    12a0:	mov    %r9,-0x18(%rsp)
    12a5:	sub    %r9,%rdx
    12a8:	sar    $0x2,%rdx
    12ac:	cmp    %rax,%rdx
    12af:	jb     1533 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2b3>
    12b5:	mov    (%r8),%rsi
    12b8:	mov    0x8(%r8),%rdx
    12bc:	mov    %rsi,-0x40(%rsp)
    12c1:	sub    %rsi,%rdx
    12c4:	sar    $0x2,%rdx
    12c8:	cmp    %rax,%rdx
    12cb:	jb     1533 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2b3>
    12d1:	mov    (%rdi),%rsi
    12d4:	mov    0x8(%rdi),%rdx
    12d8:	mov    %rsi,-0x38(%rsp)
    12dd:	sub    %rsi,%rdx
    12e0:	sar    $0x2,%rdx
    12e4:	cmp    %rax,%rdx
    12e7:	jb     1533 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2b3>
    12ed:	test   %rcx,%rcx
    12f0:	je     1528 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2a8>
    12f6:	lea    0x0(,%rcx,4),%rax
    12fe:	mov    %rcx,%rdx
    1301:	imul   %rcx,%rdx
    1305:	mov    -0x40(%rsp),%rsi
    130a:	lea    (%rsi,%rdx,4),%rdx
    130e:	mov    %rdx,-0x20(%rsp)
    1313:	mov    -0x38(%rsp),%r12
    1318:	lea    (%r12,%rcx,4),%rdx
    131c:	mov    %rdx,-0x28(%rsp)
    1321:	mov    %rcx,%r10
    1324:	and    $0xfffffffffffffff8,%r10
    1328:	lea    -0x1(%rcx),%r11
    132c:	lea    0x10(%rsi),%rdx
    1330:	mov    %rdx,-0x30(%rsp)
    1335:	lea    0x10(%r12),%r14
    133a:	xor    %r8d,%r8d
    133d:	jmp    1357 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xd7>
    133f:	nop
    1340:	mov    -0x10(%rsp),%r8
    1345:	inc    %r8
    1348:	add    %rax,%r14
    134b:	add    %rax,%r12
    134e:	cmp    %rcx,%r8
    1351:	je     1528 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2a8>
    1357:	test   %rax,%rax
    135a:	sets   %sil
    135e:	mov    %rax,%rdx
    1361:	imul   %r8,%rdx
    1365:	mov    -0x38(%rsp),%rbx
    136a:	lea    (%rbx,%rdx,1),%rdi
    136e:	add    -0x28(%rsp),%rdx
    1373:	mov    %r8,-0x10(%rsp)
    1378:	imul   %rcx,%r8
    137c:	mov    -0x18(%rsp),%r9
    1381:	lea    (%r9,%r8,4),%r13
    1385:	lea    (%rbx,%r8,4),%r8
    1389:	mov    %r8,-0x8(%rsp)
    138e:	cmp    -0x20(%rsp),%rdi
    1393:	setb   %dil
    1397:	mov    -0x40(%rsp),%r8
    139c:	cmp    %rdx,%r8
    139f:	setb   %dl
    13a2:	and    %dil,%dl
    13a5:	or     %sil,%dl
    13a8:	mov    %r8,%rsi
    13ab:	mov    -0x30(%rsp),%rbx
    13b0:	xor    %edi,%edi
    13b2:	jmp    13d2 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x152>
    13b4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    13c0:	inc    %rdi
    13c3:	add    %rax,%rbx
    13c6:	add    %rax,%rsi
    13c9:	cmp    %rcx,%rdi
    13cc:	je     1340 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    13d2:	cmp    $0x8,%rcx
    13d6:	setb   %r9b
    13da:	mov    0x0(%r13,%rdi,4),%r8d
    13df:	or     %dl,%r9b
    13e2:	je     1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    13e4:	xor    %r9d,%r9d
    13e7:	jmp    14ba <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x23a>
    13ec:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13fb:	nopl   0x0(%rax,%rax,1)
    1400:	movd   %r8d,%xmm0
    1405:	pshufd $0x0,%xmm0,%xmm0
    140a:	pshufd $0xf5,%xmm0,%xmm1
    140f:	xor    %r15d,%r15d
    1412:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1421:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1430:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    143f:	nop
    1440:	movdqu -0x10(%rbx,%r15,4),%xmm2
    1447:	movdqu (%rbx,%r15,4),%xmm3
    144d:	pshufd $0xf5,%xmm2,%xmm4
    1452:	pmuludq %xmm0,%xmm2
    1456:	pshufd $0xe8,%xmm2,%xmm2
    145b:	pmuludq %xmm1,%xmm4
    145f:	pshufd $0xe8,%xmm4,%xmm4
    1464:	punpckldq %xmm4,%xmm2
    1468:	pshufd $0xf5,%xmm3,%xmm4
    146d:	pmuludq %xmm0,%xmm3
    1471:	pshufd $0xe8,%xmm3,%xmm3
    1476:	pmuludq %xmm1,%xmm4
    147a:	pshufd $0xe8,%xmm4,%xmm4
    147f:	punpckldq %xmm4,%xmm3
    1483:	movdqu -0x10(%r14,%r15,4),%xmm4
    148a:	paddd  %xmm2,%xmm4
    148e:	movdqu (%r14,%r15,4),%xmm2
    1494:	paddd  %xmm3,%xmm2
    1498:	movdqu %xmm4,-0x10(%r14,%r15,4)
    149f:	movdqu %xmm2,(%r14,%r15,4)
    14a5:	add    $0x8,%r15
    14a9:	cmp    %r15,%r10
    14ac:	jne    1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    14ae:	mov    %r10,%r9
    14b1:	cmp    %rcx,%r10
    14b4:	je     13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    14ba:	mov    %r9,%r15
    14bd:	test   $0x1,%cl
    14c0:	je     14f2 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x272>
    14c2:	mov    %rdi,%r15
    14c5:	imul   %rcx,%r15
    14c9:	mov    -0x40(%rsp),%rbp
    14ce:	lea    0x0(,%r15,4),%r15
    14d6:	add    %rbp,%r15
    14d9:	mov    (%r15,%r9,4),%r15d
    14dd:	imul   %r8d,%r15d
    14e1:	mov    -0x8(%rsp),%rbp
    14e6:	add    %r15d,0x0(%rbp,%r9,4)
    14eb:	mov    %r9,%r15
    14ee:	or     $0x1,%r15
    14f2:	cmp    %r11,%r9
    14f5:	je     13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    14fb:	nopl   0x0(%rax,%rax,1)
    1500:	mov    (%rsi,%r15,4),%r9d
    1504:	imul   %r8d,%r9d
    1508:	add    %r9d,(%r12,%r15,4)
    150c:	mov    0x4(%rsi,%r15,4),%r9d
    1511:	imul   %r8d,%r9d
    1515:	add    %r9d,0x4(%r12,%r15,4)
    151a:	add    $0x2,%r15
    151e:	cmp    %r15,%rcx
    1521:	jne    1500 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    1523:	jmp    13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    1528:	pop    %rbx
    1529:	pop    %r12
    152b:	pop    %r13
    152d:	pop    %r14
    152f:	pop    %r15
    1531:	pop    %rbp
    1532:	ret
    1533:	ud2
    1535:	data16 cs nopw 0x0(%rax,%rax,1)
