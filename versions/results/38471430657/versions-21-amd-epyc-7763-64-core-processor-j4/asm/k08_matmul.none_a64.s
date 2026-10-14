0000000000001240 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	test   %rcx,%rcx
    1243:	je     14b2 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x272>
    1249:	push   %rbp
    124a:	push   %r15
    124c:	push   %r14
    124e:	push   %r13
    1250:	push   %r12
    1252:	push   %rbx
    1253:	mov    %rcx,%r14
    1256:	mov    (%rsi),%rax
    1259:	mov    %rax,-0x18(%rsp)
    125e:	mov    (%rdx),%rax
    1261:	mov    (%rdi),%r15
    1264:	lea    0x0(,%rcx,4),%rdi
    126c:	imul   %r14,%rcx
    1270:	lea    (%rax,%rcx,4),%rcx
    1274:	mov    %rcx,-0x28(%rsp)
    1279:	lea    (%r15,%r14,4),%rcx
    127d:	mov    %rcx,-0x30(%rsp)
    1282:	mov    %r14,%rcx
    1285:	and    $0xfffffffffffffff8,%rcx
    1289:	lea    0x10(%r15),%r11
    128d:	mov    %rax,-0x40(%rsp)
    1292:	add    $0x10,%rax
    1296:	mov    %rax,-0x38(%rsp)
    129b:	xor    %r9d,%r9d
    129e:	mov    %r15,-0x20(%rsp)
    12a3:	jmp    12d7 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x97>
    12a5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    -0x10(%rsp),%r9
    12c5:	inc    %r9
    12c8:	add    %rdi,%r11
    12cb:	add    %rdi,%r15
    12ce:	cmp    %r14,%r9
    12d1:	je     14a8 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x268>
    12d7:	test   %rdi,%rdi
    12da:	sets   %dl
    12dd:	mov    %rdi,%rsi
    12e0:	imul   %r9,%rsi
    12e4:	mov    -0x20(%rsp),%r10
    12e9:	lea    (%r10,%rsi,1),%r8
    12ed:	add    -0x30(%rsp),%rsi
    12f2:	mov    %r9,-0x10(%rsp)
    12f7:	imul   %r14,%r9
    12fb:	mov    -0x18(%rsp),%rax
    1300:	lea    (%rax,%r9,4),%r12
    1304:	lea    (%r10,%r9,4),%rax
    1308:	mov    %rax,-0x8(%rsp)
    130d:	cmp    -0x28(%rsp),%r8
    1312:	setb   %r8b
    1316:	mov    -0x40(%rsp),%rax
    131b:	cmp    %rsi,%rax
    131e:	setb   %bpl
    1322:	and    %r8b,%bpl
    1325:	or     %dl,%bpl
    1328:	mov    %rax,%rdx
    132b:	mov    -0x38(%rsp),%rbx
    1330:	xor    %eax,%eax
    1332:	jmp    1352 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x112>
    1334:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	inc    %rax
    1343:	add    %rdi,%rbx
    1346:	add    %rdi,%rdx
    1349:	cmp    %r14,%rax
    134c:	je     12c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1352:	cmp    $0x8,%r14
    1356:	setb   %sil
    135a:	mov    (%r12,%rax,4),%r8d
    135e:	or     %bpl,%sil
    1361:	test   $0x1,%sil
    1365:	je     1380 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x140>
    1367:	xor    %r10d,%r10d
    136a:	jmp    143a <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1fa>
    136f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137e:	xchg   %ax,%ax
    1380:	movd   %r8d,%xmm0
    1385:	pshufd $0x0,%xmm0,%xmm0
    138a:	pshufd $0xf5,%xmm0,%xmm1
    138f:	xor    %r10d,%r10d
    1392:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13b0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13bf:	nop
    13c0:	movdqu -0x10(%rbx,%r10,4),%xmm2
    13c7:	movdqu (%rbx,%r10,4),%xmm3
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
    1403:	movdqu -0x10(%r11,%r10,4),%xmm4
    140a:	paddd  %xmm2,%xmm4
    140e:	movdqu (%r11,%r10,4),%xmm2
    1414:	paddd  %xmm3,%xmm2
    1418:	movdqu %xmm4,-0x10(%r11,%r10,4)
    141f:	movdqu %xmm2,(%r11,%r10,4)
    1425:	add    $0x8,%r10
    1429:	cmp    %r10,%rcx
    142c:	jne    13c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    142e:	mov    %rcx,%r10
    1431:	cmp    %rcx,%r14
    1434:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    143a:	mov    %r10,%rsi
    143d:	or     $0x1,%rsi
    1441:	test   $0x1,%r14b
    1445:	je     1473 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x233>
    1447:	mov    %rax,%r9
    144a:	imul   %r14,%r9
    144e:	mov    -0x40(%rsp),%r13
    1453:	lea    0x0(,%r9,4),%r9
    145b:	add    %r13,%r9
    145e:	mov    (%r9,%r10,4),%r9d
    1462:	imul   %r8d,%r9d
    1466:	mov    -0x8(%rsp),%r13
    146b:	add    %r9d,0x0(%r13,%r10,4)
    1470:	mov    %rsi,%r10
    1473:	cmp    %rsi,%r14
    1476:	je     1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    147c:	nopl   0x0(%rax)
    1480:	mov    (%rdx,%r10,4),%esi
    1484:	imul   %r8d,%esi
    1488:	add    %esi,(%r15,%r10,4)
    148c:	mov    0x4(%rdx,%r10,4),%esi
    1491:	imul   %r8d,%esi
    1495:	add    %esi,0x4(%r15,%r10,4)
    149a:	add    $0x2,%r10
    149e:	cmp    %r10,%r14
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
