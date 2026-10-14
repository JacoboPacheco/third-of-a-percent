0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	test   %rcx,%rcx
    1243:	je     1472 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x232>
    1249:	push   %rbp
    124a:	push   %r15
    124c:	push   %r14
    124e:	push   %r13
    1250:	push   %r12
    1252:	push   %rbx
    1253:	mov    (%rdi),%r12
    1256:	mov    (%rsi),%rax
    1259:	mov    %rax,-0x20(%rsp)
    125e:	mov    (%rdx),%rdx
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
    12a3:	mov    %r12,-0x18(%rsp)
    12a8:	jmp    12c7 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x87>
    12aa:	nopw   0x0(%rax,%rax,1)
    12b0:	mov    -0x10(%rsp),%r8
    12b5:	inc    %r8
    12b8:	add    %rdi,%r14
    12bb:	add    %rdi,%r12
    12be:	cmp    %rcx,%r8
    12c1:	je     1468 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x228>
    12c7:	test   %rdi,%rdi
    12ca:	sets   %al
    12cd:	mov    %rdi,%rdx
    12d0:	imul   %r8,%rdx
    12d4:	mov    -0x18(%rsp),%r9
    12d9:	lea    (%r9,%rdx,1),%rsi
    12dd:	add    -0x30(%rsp),%rdx
    12e2:	mov    %r8,-0x10(%rsp)
    12e7:	imul   %rcx,%r8
    12eb:	lea    (%r9,%r8,4),%r9
    12ef:	mov    %r9,-0x8(%rsp)
    12f4:	mov    -0x20(%rsp),%r9
    12f9:	lea    (%r9,%r8,4),%rbp
    12fd:	cmp    -0x28(%rsp),%rsi
    1302:	setb   %r8b
    1306:	mov    -0x40(%rsp),%r9
    130b:	cmp    %rdx,%r9
    130e:	setb   %sil
    1312:	and    %r8b,%sil
    1315:	or     %al,%sil
    1318:	mov    %r9,%rdx
    131b:	mov    -0x38(%rsp),%rbx
    1320:	xor    %r9d,%r9d
    1323:	jmp    1342 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x102>
    1325:	data16 cs nopw 0x0(%rax,%rax,1)
    1330:	inc    %r9
    1333:	add    %rdi,%rbx
    1336:	add    %rdi,%rdx
    1339:	cmp    %rcx,%r9
    133c:	je     12b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    1342:	cmp    $0x8,%rcx
    1346:	setb   %r8b
    134a:	mov    0x0(%rbp,%r9,4),%eax
    134f:	or     %sil,%r8b
    1352:	je     1360 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x120>
    1354:	xor    %r8d,%r8d
    1357:	jmp    13fa <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1ba>
    135c:	nopl   0x0(%rax)
    1360:	movd   %eax,%xmm0
    1364:	pshufd $0x0,%xmm0,%xmm0
    1369:	pshufd $0xf5,%xmm0,%xmm1
    136e:	xor    %r15d,%r15d
    1371:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	movdqu -0x10(%rbx,%r15,4),%xmm2
    1387:	movdqu (%rbx,%r15,4),%xmm3
    138d:	pshufd $0xf5,%xmm2,%xmm4
    1392:	pmuludq %xmm0,%xmm2
    1396:	pshufd $0xe8,%xmm2,%xmm2
    139b:	pmuludq %xmm1,%xmm4
    139f:	pshufd $0xe8,%xmm4,%xmm4
    13a4:	punpckldq %xmm4,%xmm2
    13a8:	pshufd $0xf5,%xmm3,%xmm4
    13ad:	pmuludq %xmm0,%xmm3
    13b1:	pshufd $0xe8,%xmm3,%xmm3
    13b6:	pmuludq %xmm1,%xmm4
    13ba:	pshufd $0xe8,%xmm4,%xmm4
    13bf:	punpckldq %xmm4,%xmm3
    13c3:	movdqu -0x10(%r14,%r15,4),%xmm4
    13ca:	paddd  %xmm2,%xmm4
    13ce:	movdqu (%r14,%r15,4),%xmm2
    13d4:	paddd  %xmm3,%xmm2
    13d8:	movdqu %xmm4,-0x10(%r14,%r15,4)
    13df:	movdqu %xmm2,(%r14,%r15,4)
    13e5:	add    $0x8,%r15
    13e9:	cmp    %r15,%r10
    13ec:	jne    1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    13ee:	mov    %r10,%r8
    13f1:	cmp    %rcx,%r10
    13f4:	je     1330 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    13fa:	mov    %r8,%r15
    13fd:	test   $0x1,%cl
    1400:	je     1432 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1f2>
    1402:	mov    %r9,%r15
    1405:	imul   %rcx,%r15
    1409:	mov    -0x40(%rsp),%r13
    140e:	lea    0x0(,%r15,4),%r15
    1416:	add    %r13,%r15
    1419:	mov    (%r15,%r8,4),%r15d
    141d:	imul   %eax,%r15d
    1421:	mov    -0x8(%rsp),%r13
    1426:	add    %r15d,0x0(%r13,%r8,4)
    142b:	mov    %r8,%r15
    142e:	or     $0x1,%r15
    1432:	cmp    %r11,%r8
    1435:	je     1330 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    143b:	nopl   0x0(%rax,%rax,1)
    1440:	mov    (%rdx,%r15,4),%r8d
    1444:	imul   %eax,%r8d
    1448:	add    %r8d,(%r12,%r15,4)
    144c:	mov    0x4(%rdx,%r15,4),%r8d
    1451:	imul   %eax,%r8d
    1455:	add    %r8d,0x4(%r12,%r15,4)
    145a:	add    $0x2,%r15
    145e:	cmp    %r15,%rcx
    1461:	jne    1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    1463:	jmp    1330 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf0>
    1468:	pop    %rbx
    1469:	pop    %r12
    146b:	pop    %r13
    146d:	pop    %r14
    146f:	pop    %r15
    1471:	pop    %rbp
    1472:	ret
    1473:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
