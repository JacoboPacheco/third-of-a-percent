0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	mov    %rdx,%r8
    124d:	mov    %rcx,%rax
    1250:	mul    %rcx
    1253:	jo     14d4 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>
    1259:	mov    (%rsi),%r9
    125c:	mov    0x8(%rsi),%rdx
    1260:	mov    %r9,-0x18(%rsp)
    1265:	sub    %r9,%rdx
    1268:	sar    $0x2,%rdx
    126c:	cmp    %rax,%rdx
    126f:	jb     14d4 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>
    1275:	mov    (%r8),%rsi
    1278:	mov    0x8(%r8),%rdx
    127c:	mov    %rsi,-0x48(%rsp)
    1281:	sub    %rsi,%rdx
    1284:	sar    $0x2,%rdx
    1288:	cmp    %rax,%rdx
    128b:	jb     14d4 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>
    1291:	mov    (%rdi),%rsi
    1294:	mov    0x8(%rdi),%rdx
    1298:	mov    %rsi,-0x40(%rsp)
    129d:	sub    %rsi,%rdx
    12a0:	sar    $0x2,%rdx
    12a4:	cmp    %rax,%rdx
    12a7:	jb     14d4 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x294>
    12ad:	test   %rcx,%rcx
    12b0:	je     14c9 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x289>
    12b6:	lea    0x0(,%rcx,4),%rax
    12be:	mov    %rcx,%rdx
    12c1:	imul   %rcx,%rdx
    12c5:	mov    -0x48(%rsp),%rsi
    12ca:	lea    (%rsi,%rdx,4),%rdx
    12ce:	mov    %rdx,-0x20(%rsp)
    12d3:	mov    -0x40(%rsp),%r13
    12d8:	lea    0x0(,%rcx,4),%rdx
    12e0:	add    %r13,%rdx
    12e3:	mov    %rdx,-0x28(%rsp)
    12e8:	mov    %rcx,%r10
    12eb:	and    $0xfffffffffffffff8,%r10
    12ef:	lea    -0x1(%rcx),%r11
    12f3:	lea    0x10(%rsi),%rdx
    12f7:	mov    %rdx,-0x30(%rsp)
    12fc:	lea    0x10(%r13),%r14
    1300:	lea    0x4(%rsi),%rdx
    1304:	mov    %rdx,-0x38(%rsp)
    1309:	xor    %edx,%edx
    130b:	jmp    1327 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xe7>
    130d:	nopl   (%rax)
    1310:	mov    -0x10(%rsp),%rdx
    1315:	inc    %rdx
    1318:	add    %rax,%r14
    131b:	add    %rax,%r13
    131e:	cmp    %rcx,%rdx
    1321:	je     14c9 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x289>
    1327:	test   %rax,%rax
    132a:	sets   %sil
    132e:	mov    %rax,%rdi
    1331:	imul   %rdx,%rdi
    1335:	mov    -0x40(%rsp),%r9
    133a:	lea    (%r9,%rdi,1),%r8
    133e:	add    -0x28(%rsp),%rdi
    1343:	mov    %rdx,-0x10(%rsp)
    1348:	imul   %rcx,%rdx
    134c:	lea    (%r9,%rdx,4),%r9
    1350:	mov    %r9,-0x8(%rsp)
    1355:	mov    -0x18(%rsp),%r9
    135a:	lea    (%r9,%rdx,4),%rdx
    135e:	cmp    -0x20(%rsp),%r8
    1363:	setb   %r8b
    1367:	cmp    %rdi,-0x48(%rsp)
    136c:	setb   %dil
    1370:	and    %r8b,%dil
    1373:	or     %sil,%dil
    1376:	mov    -0x38(%rsp),%r15
    137b:	mov    -0x30(%rsp),%rbx
    1380:	xor    %r9d,%r9d
    1383:	jmp    13a2 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x162>
    1385:	data16 cs nopw 0x0(%rax,%rax,1)
    1390:	inc    %r9
    1393:	add    %rax,%rbx
    1396:	add    %rax,%r15
    1399:	cmp    %rcx,%r9
    139c:	je     1310 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xd0>
    13a2:	cmp    $0x8,%rcx
    13a6:	setb   %sil
    13aa:	mov    (%rdx,%r9,4),%r8d
    13ae:	or     %dil,%sil
    13b1:	je     13c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x180>
    13b3:	xor    %esi,%esi
    13b5:	jmp    145a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x21a>
    13ba:	nopw   0x0(%rax,%rax,1)
    13c0:	movd   %r8d,%xmm0
    13c5:	pshufd $0x0,%xmm0,%xmm0
    13ca:	pshufd $0xf5,%xmm0,%xmm1
    13cf:	xor    %r12d,%r12d
    13d2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13e0:	movdqu -0x10(%rbx,%r12,4),%xmm2
    13e7:	movdqu (%rbx,%r12,4),%xmm3
    13ed:	pshufd $0xf5,%xmm2,%xmm4
    13f2:	pmuludq %xmm0,%xmm2
    13f6:	pshufd $0xe8,%xmm2,%xmm2
    13fb:	pmuludq %xmm1,%xmm4
    13ff:	pshufd $0xe8,%xmm4,%xmm4
    1404:	punpckldq %xmm4,%xmm2
    1408:	pshufd $0xf5,%xmm3,%xmm4
    140d:	pmuludq %xmm0,%xmm3
    1411:	pshufd $0xe8,%xmm3,%xmm3
    1416:	pmuludq %xmm1,%xmm4
    141a:	pshufd $0xe8,%xmm4,%xmm4
    141f:	punpckldq %xmm4,%xmm3
    1423:	movdqu -0x10(%r14,%r12,4),%xmm4
    142a:	paddd  %xmm2,%xmm4
    142e:	movdqu (%r14,%r12,4),%xmm2
    1434:	paddd  %xmm3,%xmm2
    1438:	movdqu %xmm4,-0x10(%r14,%r12,4)
    143f:	movdqu %xmm2,(%r14,%r12,4)
    1445:	add    $0x8,%r12
    1449:	cmp    %r12,%r10
    144c:	jne    13e0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1a0>
    144e:	mov    %r10,%rsi
    1451:	cmp    %rcx,%r10
    1454:	je     1390 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x150>
    145a:	mov    %rsi,%r12
    145d:	test   $0x1,%cl
    1460:	je     1492 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x252>
    1462:	mov    %r9,%r12
    1465:	imul   %rcx,%r12
    1469:	mov    -0x48(%rsp),%rbp
    146e:	lea    0x0(,%r12,4),%r12
    1476:	add    %rbp,%r12
    1479:	mov    (%r12,%rsi,4),%r12d
    147d:	imul   %r8d,%r12d
    1481:	mov    -0x8(%rsp),%rbp
    1486:	add    %r12d,0x0(%rbp,%rsi,4)
    148b:	mov    %rsi,%r12
    148e:	or     $0x1,%r12
    1492:	cmp    %r11,%rsi
    1495:	je     1390 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x150>
    149b:	nopl   0x0(%rax,%rax,1)
    14a0:	mov    -0x4(%r15,%r12,4),%esi
    14a5:	imul   %r8d,%esi
    14a9:	add    %esi,0x0(%r13,%r12,4)
    14ae:	mov    (%r15,%r12,4),%esi
    14b2:	imul   %r8d,%esi
    14b6:	add    %esi,0x4(%r13,%r12,4)
    14bb:	add    $0x2,%r12
    14bf:	cmp    %r12,%rcx
    14c2:	jne    14a0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x260>
    14c4:	jmp    1390 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x150>
    14c9:	pop    %rbx
    14ca:	pop    %r12
    14cc:	pop    %r13
    14ce:	pop    %r14
    14d0:	pop    %r15
    14d2:	pop    %rbp
    14d3:	ret
    14d4:	ud2
    14d6:	cs nopw 0x0(%rax,%rax,1)
