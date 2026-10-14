0000000000001240 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	test   %rcx,%rcx
    1243:	je     14b2 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x272>
    1249:	push   %rbp
    124a:	push   %r15
    124c:	push   %r14
    124e:	push   %r13
    1250:	push   %r12
    1252:	push   %rbx
    1253:	mov    (%rsi),%rax
    1256:	mov    %rax,-0x18(%rsp)
    125b:	mov    (%rdx),%rdx
    125e:	mov    (%rdi),%r12
    1261:	lea    0x0(,%rcx,4),%rdi
    1269:	mov    %rcx,%rax
    126c:	imul   %rcx,%rax
    1270:	lea    (%rdx,%rax,4),%rax
    1274:	mov    %rax,-0x28(%rsp)
    1279:	lea    (%r12,%rcx,4),%rax
    127d:	mov    %rax,-0x30(%rsp)
    1282:	mov    %rcx,%r10
    1285:	and    $0xfffffffffffffff8,%r10
    1289:	lea    -0x1(%rcx),%r11
    128d:	mov    %rdx,-0x40(%rsp)
    1292:	lea    0x10(%rdx),%rax
    1296:	mov    %rax,-0x38(%rsp)
    129b:	lea    0x10(%r12),%r14
    12a0:	xor    %r8d,%r8d
    12a3:	mov    %r12,-0x20(%rsp)
    12a8:	jmp    12d7 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x97>
    12aa:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b9:	nopl   0x0(%rax)
    12c0:	mov    -0x10(%rsp),%r8
    12c5:	inc    %r8
    12c8:	add    %rdi,%r14
    12cb:	add    %rdi,%r12
    12ce:	cmp    %rcx,%r8
    12d1:	je     14a8 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x268>
    12d7:	test   %rdi,%rdi
    12da:	sets   %dl
    12dd:	mov    %rdi,%rax
    12e0:	imul   %r8,%rax
    12e4:	mov    -0x20(%rsp),%rbx
    12e9:	lea    (%rbx,%rax,1),%rsi
    12ed:	add    -0x30(%rsp),%rax
    12f2:	mov    %r8,-0x10(%rsp)
    12f7:	imul   %rcx,%r8
    12fb:	mov    -0x18(%rsp),%r9
    1300:	lea    (%r9,%r8,4),%r13
    1304:	lea    (%rbx,%r8,4),%r8
    1308:	mov    %r8,-0x8(%rsp)
    130d:	cmp    -0x28(%rsp),%rsi
    1312:	setb   %sil
    1316:	mov    -0x40(%rsp),%r8
    131b:	cmp    %rax,%r8
    131e:	setb   %al
    1321:	and    %sil,%al
    1324:	or     %dl,%al
    1326:	mov    %r8,%rdx
    1329:	mov    -0x38(%rsp),%rbx
    132e:	xor    %r9d,%r9d
    1331:	jmp    1352 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x112>
    1333:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	inc    %r9
    1343:	add    %rdi,%rbx
    1346:	add    %rdi,%rdx
    1349:	cmp    %rcx,%r9
    134c:	je     12c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1352:	cmp    $0x8,%rcx
    1356:	setb   %r8b
    135a:	mov    0x0(%r13,%r9,4),%esi
    135f:	or     %al,%r8b
    1362:	je     1380 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    1364:	xor    %r8d,%r8d
    1367:	jmp    143a <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1fa>
    136c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137b:	nopl   0x0(%rax,%rax,1)
    1380:	movd   %esi,%xmm0
    1384:	pshufd $0x0,%xmm0,%xmm0
    1389:	pshufd $0xf5,%xmm0,%xmm1
    138e:	xor    %r15d,%r15d
    1391:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13a0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13af:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13be:	xchg   %ax,%ax
    13c0:	movdqu -0x10(%rbx,%r15,4),%xmm2
    13c7:	movdqu (%rbx,%r15,4),%xmm3
    13cd:	pshufd $0xf5,%xmm2,%xmm4
    13d2:	pmuludq %xmm0,%xmm2
    13d6:	pshufd $0xe8,%xmm2,%xmm2
    13db:	pmuludq %xmm1,%xmm4
    13df:	pshufd $0xe8,%xmm4,%xmm4
    13e4:	punpckldq %xmm4,%xmm2
    13e8:	pshufd $0xf5,%xmm3,%xmm4
    13ed:	pmuludq %xmm0,%xmm3
    13f1:	pshufd $0xe8,%xmm3,%xmm3
    13f6:	pmuludq %xmm1,%xmm4
    13fa:	pshufd $0xe8,%xmm4,%xmm4
    13ff:	punpckldq %xmm4,%xmm3
    1403:	movdqu -0x10(%r14,%r15,4),%xmm4
    140a:	paddd  %xmm2,%xmm4
    140e:	movdqu (%r14,%r15,4),%xmm2
    1414:	paddd  %xmm3,%xmm2
    1418:	movdqu %xmm4,-0x10(%r14,%r15,4)
    141f:	movdqu %xmm2,(%r14,%r15,4)
    1425:	add    $0x8,%r15
    1429:	cmp    %r15,%r10
    142c:	jne    13c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    142e:	mov    %r10,%r8
    1431:	cmp    %rcx,%r10
    1434:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    143a:	mov    %r8,%r15
    143d:	test   $0x1,%cl
    1440:	je     1472 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x232>
    1442:	mov    %r9,%r15
    1445:	imul   %rcx,%r15
    1449:	mov    -0x40(%rsp),%rbp
    144e:	lea    0x0(,%r15,4),%r15
    1456:	add    %rbp,%r15
    1459:	mov    (%r15,%r8,4),%r15d
    145d:	imul   %esi,%r15d
    1461:	mov    -0x8(%rsp),%rbp
    1466:	add    %r15d,0x0(%rbp,%r8,4)
    146b:	mov    %r8,%r15
    146e:	or     $0x1,%r15
    1472:	cmp    %r11,%r8
    1475:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    147b:	nopl   0x0(%rax,%rax,1)
    1480:	mov    (%rdx,%r15,4),%r8d
    1484:	imul   %esi,%r8d
    1488:	add    %r8d,(%r12,%r15,4)
    148c:	mov    0x4(%rdx,%r15,4),%r8d
    1491:	imul   %esi,%r8d
    1495:	add    %r8d,0x4(%r12,%r15,4)
    149a:	add    $0x2,%r15
    149e:	cmp    %r15,%rcx
    14a1:	jne    1480 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    14a3:	jmp    1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    14a8:	pop    %rbx
    14a9:	pop    %r12
    14ab:	pop    %r13
    14ad:	pop    %r14
    14af:	pop    %r15
    14b1:	pop    %rbp
    14b2:	ret
    14b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
