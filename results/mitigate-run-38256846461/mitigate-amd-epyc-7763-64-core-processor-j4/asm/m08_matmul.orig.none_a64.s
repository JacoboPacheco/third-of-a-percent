0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	test   %rcx,%rcx
    1283:	je     14f2 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x272>
    1289:	push   %rbp
    128a:	push   %r15
    128c:	push   %r14
    128e:	push   %r13
    1290:	push   %r12
    1292:	push   %rbx
    1293:	mov    (%rsi),%rax
    1296:	mov    %rax,-0x18(%rsp)
    129b:	mov    (%rdx),%rdx
    129e:	mov    (%rdi),%r12
    12a1:	lea    0x0(,%rcx,4),%rdi
    12a9:	mov    %rcx,%rax
    12ac:	imul   %rcx,%rax
    12b0:	lea    (%rdx,%rax,4),%rax
    12b4:	mov    %rax,-0x28(%rsp)
    12b9:	lea    (%r12,%rcx,4),%rax
    12bd:	mov    %rax,-0x30(%rsp)
    12c2:	mov    %rcx,%r10
    12c5:	and    $0xfffffffffffffff8,%r10
    12c9:	lea    -0x1(%rcx),%r11
    12cd:	mov    %rdx,-0x40(%rsp)
    12d2:	lea    0x10(%rdx),%rax
    12d6:	mov    %rax,-0x38(%rsp)
    12db:	lea    0x10(%r12),%r14
    12e0:	xor    %r8d,%r8d
    12e3:	mov    %r12,-0x20(%rsp)
    12e8:	jmp    1317 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x97>
    12ea:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f9:	nopl   0x0(%rax)
    1300:	mov    -0x10(%rsp),%r8
    1305:	inc    %r8
    1308:	add    %rdi,%r14
    130b:	add    %rdi,%r12
    130e:	cmp    %rcx,%r8
    1311:	je     14e8 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x268>
    1317:	test   %rdi,%rdi
    131a:	sets   %dl
    131d:	mov    %rdi,%rax
    1320:	imul   %r8,%rax
    1324:	mov    -0x20(%rsp),%rbx
    1329:	lea    (%rbx,%rax,1),%rsi
    132d:	add    -0x30(%rsp),%rax
    1332:	mov    %r8,-0x10(%rsp)
    1337:	imul   %rcx,%r8
    133b:	mov    -0x18(%rsp),%r9
    1340:	lea    (%r9,%r8,4),%r13
    1344:	lea    (%rbx,%r8,4),%r8
    1348:	mov    %r8,-0x8(%rsp)
    134d:	cmp    -0x28(%rsp),%rsi
    1352:	setb   %sil
    1356:	mov    -0x40(%rsp),%r8
    135b:	cmp    %rax,%r8
    135e:	setb   %al
    1361:	and    %sil,%al
    1364:	or     %dl,%al
    1366:	mov    %r8,%rdx
    1369:	mov    -0x38(%rsp),%rbx
    136e:	xor    %r9d,%r9d
    1371:	jmp    1392 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x112>
    1373:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	inc    %r9
    1383:	add    %rdi,%rbx
    1386:	add    %rdi,%rdx
    1389:	cmp    %rcx,%r9
    138c:	je     1300 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1392:	cmp    $0x8,%rcx
    1396:	setb   %r8b
    139a:	mov    0x0(%r13,%r9,4),%esi
    139f:	or     %al,%r8b
    13a2:	je     13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    13a4:	xor    %r8d,%r8d
    13a7:	jmp    147a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1fa>
    13ac:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13bb:	nopl   0x0(%rax,%rax,1)
    13c0:	movd   %esi,%xmm0
    13c4:	pshufd $0x0,%xmm0,%xmm0
    13c9:	pshufd $0xf5,%xmm0,%xmm1
    13ce:	xor    %r15d,%r15d
    13d1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13e0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13ef:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13fe:	xchg   %ax,%ax
    1400:	movdqu -0x10(%rbx,%r15,4),%xmm2
    1407:	movdqu (%rbx,%r15,4),%xmm3
    140d:	pshufd $0xf5,%xmm2,%xmm4
    1412:	pmuludq %xmm0,%xmm2
    1416:	pshufd $0xe8,%xmm2,%xmm2
    141b:	pmuludq %xmm1,%xmm4
    141f:	pshufd $0xe8,%xmm4,%xmm4
    1424:	punpckldq %xmm4,%xmm2
    1428:	pshufd $0xf5,%xmm3,%xmm4
    142d:	pmuludq %xmm0,%xmm3
    1431:	pshufd $0xe8,%xmm3,%xmm3
    1436:	pmuludq %xmm1,%xmm4
    143a:	pshufd $0xe8,%xmm4,%xmm4
    143f:	punpckldq %xmm4,%xmm3
    1443:	movdqu -0x10(%r14,%r15,4),%xmm4
    144a:	paddd  %xmm2,%xmm4
    144e:	movdqu (%r14,%r15,4),%xmm2
    1454:	paddd  %xmm3,%xmm2
    1458:	movdqu %xmm4,-0x10(%r14,%r15,4)
    145f:	movdqu %xmm2,(%r14,%r15,4)
    1465:	add    $0x8,%r15
    1469:	cmp    %r15,%r10
    146c:	jne    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    146e:	mov    %r10,%r8
    1471:	cmp    %rcx,%r10
    1474:	je     1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    147a:	mov    %r8,%r15
    147d:	test   $0x1,%cl
    1480:	je     14b2 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x232>
    1482:	mov    %r9,%r15
    1485:	imul   %rcx,%r15
    1489:	mov    -0x40(%rsp),%rbp
    148e:	lea    0x0(,%r15,4),%r15
    1496:	add    %rbp,%r15
    1499:	mov    (%r15,%r8,4),%r15d
    149d:	imul   %esi,%r15d
    14a1:	mov    -0x8(%rsp),%rbp
    14a6:	add    %r15d,0x0(%rbp,%r8,4)
    14ab:	mov    %r8,%r15
    14ae:	or     $0x1,%r15
    14b2:	cmp    %r11,%r8
    14b5:	je     1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    14bb:	nopl   0x0(%rax,%rax,1)
    14c0:	mov    (%rdx,%r15,4),%r8d
    14c4:	imul   %esi,%r8d
    14c8:	add    %r8d,(%r12,%r15,4)
    14cc:	mov    0x4(%rdx,%r15,4),%r8d
    14d1:	imul   %esi,%r8d
    14d5:	add    %r8d,0x4(%r12,%r15,4)
    14da:	add    $0x2,%r15
    14de:	cmp    %r15,%rcx
    14e1:	jne    14c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    14e3:	jmp    1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    14e8:	pop    %rbx
    14e9:	pop    %r12
    14eb:	pop    %r13
    14ed:	pop    %r14
    14ef:	pop    %r15
    14f1:	pop    %rbp
    14f2:	ret
    14f3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
