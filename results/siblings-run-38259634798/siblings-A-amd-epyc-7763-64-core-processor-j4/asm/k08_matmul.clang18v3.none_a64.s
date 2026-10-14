0000000000001240 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	test   %rcx,%rcx
    1243:	je     14ca <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x28a>
    1249:	push   %rbp
    124a:	push   %r15
    124c:	push   %r14
    124e:	push   %r13
    1250:	push   %r12
    1252:	push   %rbx
    1253:	mov    (%rsi),%rax
    1256:	mov    %rax,-0x10(%rsp)
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
    1285:	and    $0xffffffffffffffe0,%r10
    1289:	mov    %ecx,%eax
    128b:	and    $0x3,%eax
    128e:	mov    %rax,-0x40(%rsp)
    1293:	mov    %rdx,-0x18(%rsp)
    1298:	lea    0x60(%rdx),%rax
    129c:	mov    %rax,-0x38(%rsp)
    12a1:	lea    0x60(%r12),%r14
    12a6:	xor    %r8d,%r8d
    12a9:	mov    %r12,-0x20(%rsp)
    12ae:	jmp    12d7 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x97>
    12b0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bf:	nop
    12c0:	mov    -0x8(%rsp),%r8
    12c5:	inc    %r8
    12c8:	add    %rdi,%r14
    12cb:	add    %rdi,%r12
    12ce:	cmp    %rcx,%r8
    12d1:	je     14c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    12d7:	test   %rdi,%rdi
    12da:	sets   %al
    12dd:	mov    %rdi,%rdx
    12e0:	imul   %r8,%rdx
    12e4:	mov    -0x20(%rsp),%rsi
    12e9:	add    %rdx,%rsi
    12ec:	add    -0x30(%rsp),%rdx
    12f1:	mov    %r8,-0x8(%rsp)
    12f6:	imul   %rcx,%r8
    12fa:	mov    -0x10(%rsp),%r9
    12ff:	lea    (%r9,%r8,4),%r13
    1303:	cmp    -0x28(%rsp),%rsi
    1308:	setb   %sil
    130c:	mov    -0x18(%rsp),%r8
    1311:	cmp    %rdx,%r8
    1314:	setb   %bpl
    1318:	and    %sil,%bpl
    131b:	or     %al,%bpl
    131e:	mov    %r8,%rdx
    1321:	mov    -0x38(%rsp),%rbx
    1326:	xor    %r9d,%r9d
    1329:	jmp    1352 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x112>
    132b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133a:	nopw   0x0(%rax,%rax,1)
    1340:	inc    %r9
    1343:	add    %rdi,%rbx
    1346:	add    %rdi,%rdx
    1349:	cmp    %rcx,%r9
    134c:	je     12c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1352:	cmp    $0x20,%rcx
    1356:	setb   %al
    1359:	mov    0x0(%r13,%r9,4),%r8d
    135e:	or     %bpl,%al
    1361:	je     1380 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    1363:	xor    %eax,%eax
    1365:	jmp    1426 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1e6>
    136a:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1379:	nopl   0x0(%rax)
    1380:	vmovd  %r8d,%xmm0
    1385:	vpbroadcastd %xmm0,%ymm0
    138a:	xor    %eax,%eax
    138c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    139b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13aa:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13b9:	nopl   0x0(%rax)
    13c0:	vpmulld -0x60(%rbx,%rax,4),%ymm0,%ymm1
    13c7:	vpmulld -0x40(%rbx,%rax,4),%ymm0,%ymm2
    13ce:	vpmulld -0x20(%rbx,%rax,4),%ymm0,%ymm3
    13d5:	vpmulld (%rbx,%rax,4),%ymm0,%ymm4
    13db:	vpaddd -0x60(%r14,%rax,4),%ymm1,%ymm1
    13e2:	vpaddd -0x40(%r14,%rax,4),%ymm2,%ymm2
    13e9:	vpaddd -0x20(%r14,%rax,4),%ymm3,%ymm3
    13f0:	vpaddd (%r14,%rax,4),%ymm4,%ymm4
    13f6:	vmovdqu %ymm1,-0x60(%r14,%rax,4)
    13fd:	vmovdqu %ymm2,-0x40(%r14,%rax,4)
    1404:	vmovdqu %ymm3,-0x20(%r14,%rax,4)
    140b:	vmovdqu %ymm4,(%r14,%rax,4)
    1411:	add    $0x20,%rax
    1415:	cmp    %rax,%r10
    1418:	jne    13c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    141a:	mov    %r10,%rax
    141d:	cmp    %rcx,%r10
    1420:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    1426:	mov    %rax,%rsi
    1429:	cmpq   $0x0,-0x40(%rsp)
    142f:	je     1454 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x214>
    1431:	mov    -0x40(%rsp),%r11
    1436:	mov    %rax,%rsi
    1439:	nopl   0x0(%rax)
    1440:	mov    (%rdx,%rsi,4),%r15d
    1444:	imul   %r8d,%r15d
    1448:	add    %r15d,(%r12,%rsi,4)
    144c:	inc    %rsi
    144f:	dec    %r11
    1452:	jne    1440 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    1454:	sub    %rcx,%rax
    1457:	cmp    $0xfffffffffffffffc,%rax
    145b:	ja     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    1461:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1470:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    147f:	nop
    1480:	mov    (%rdx,%rsi,4),%eax
    1483:	imul   %r8d,%eax
    1487:	add    %eax,(%r12,%rsi,4)
    148b:	mov    0x4(%rdx,%rsi,4),%eax
    148f:	imul   %r8d,%eax
    1493:	add    %eax,0x4(%r12,%rsi,4)
    1498:	mov    0x8(%rdx,%rsi,4),%eax
    149c:	imul   %r8d,%eax
    14a0:	add    %eax,0x8(%r12,%rsi,4)
    14a5:	mov    0xc(%rdx,%rsi,4),%eax
    14a9:	imul   %r8d,%eax
    14ad:	add    %eax,0xc(%r12,%rsi,4)
    14b2:	add    $0x4,%rsi
    14b6:	cmp    %rsi,%rcx
    14b9:	jne    1480 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    14bb:	jmp    1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    14c0:	pop    %rbx
    14c1:	pop    %r12
    14c3:	pop    %r13
    14c5:	pop    %r14
    14c7:	pop    %r15
    14c9:	pop    %rbp
    14ca:	vzeroupper
    14cd:	ret
    14ce:	xchg   %ax,%ax
