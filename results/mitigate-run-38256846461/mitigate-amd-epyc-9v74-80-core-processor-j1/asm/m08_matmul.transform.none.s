0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	test   %rcx,%rcx
    1243:	je     1496 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x256>
    1249:	push   %rbp
    124a:	push   %r15
    124c:	push   %r14
    124e:	push   %r13
    1250:	push   %r12
    1252:	push   %rbx
    1253:	mov    (%rdi),%r8
    1256:	mov    0x8(%rdi),%rax
    125a:	sub    %r8,%rax
    125d:	sar    $0x2,%rax
    1261:	mov    %rax,-0x38(%rsp)
    1266:	mov    (%rsi),%rax
    1269:	mov    %rax,-0x40(%rsp)
    126e:	mov    (%rdx),%rdx
    1271:	lea    0x0(,%rcx,4),%r9
    1279:	lea    -0x1(%rcx),%rax
    127d:	imul   %rcx,%rax
    1281:	lea    (%rdx,%rax,4),%rax
    1285:	add    $0x4,%rax
    1289:	mov    %rax,-0x48(%rsp)
    128e:	lea    0x4(%r8),%rax
    1292:	mov    %rax,-0x50(%rsp)
    1297:	mov    %rdx,-0x60(%rsp)
    129c:	lea    0x10(%rdx),%rax
    12a0:	mov    %rax,-0x58(%rsp)
    12a5:	mov    %r8,-0x30(%rsp)
    12aa:	lea    0x10(%r8),%r14
    12ae:	xor    %eax,%eax
    12b0:	jmp    12d4 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x94>
    12b2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    -0x28(%rsp),%rax
    12c5:	inc    %rax
    12c8:	add    %r9,%r14
    12cb:	cmp    %rcx,%rax
    12ce:	je     148c <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x24c>
    12d4:	test   %r9,%r9
    12d7:	sets   %dil
    12db:	mov    %r9,%r8
    12de:	imul   %rax,%r8
    12e2:	mov    -0x30(%rsp),%rdx
    12e7:	lea    (%rdx,%r8,1),%r10
    12eb:	add    -0x50(%rsp),%r8
    12f0:	mov    %rax,-0x28(%rsp)
    12f5:	imul   %rcx,%rax
    12f9:	mov    -0x38(%rsp),%r12
    12fe:	sub    %rax,%r12
    1301:	cmp    $0xffffffffffffffff,%rcx
    1305:	cmovne %rcx,%r12
    1309:	lea    (%rdx,%rax,4),%rbx
    130d:	mov    -0x40(%rsp),%rdx
    1312:	lea    (%rdx,%rax,4),%rbp
    1316:	lea    (%rbx,%r12,4),%rax
    131a:	movabs $0x3fffffffffffffff,%rdx
    1324:	lea    (%r12,%rdx,1),%rsi
    1328:	and    %rdx,%rsi
    132b:	lea    (%r8,%rsi,4),%r8
    132f:	mov    -0x48(%rsp),%rdx
    1334:	lea    (%rdx,%rsi,4),%r11
    1338:	lea    0x1(%rsi),%rdx
    133c:	cmp    %r11,%r10
    133f:	setb   %r10b
    1343:	cmp    %r8,-0x60(%rsp)
    1348:	setb   %r11b
    134c:	and    %r10b,%r11b
    134f:	or     %dil,%r11b
    1352:	mov    %rdx,-0x10(%rsp)
    1357:	mov    %rdx,%r10
    135a:	and    $0xfffffffffffffff8,%r10
    135e:	lea    0x0(,%r10,4),%rdx
    1366:	mov    %rdx,-0x18(%rsp)
    136b:	mov    %rbx,-0x8(%rsp)
    1370:	lea    (%rbx,%r10,4),%rdx
    1374:	mov    %rdx,-0x20(%rsp)
    1379:	mov    -0x58(%rsp),%r15
    137e:	xor    %edi,%edi
    1380:	jmp    139f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15f>
    1382:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1390:	inc    %rdi
    1393:	add    %r9,%r15
    1396:	cmp    %rcx,%rdi
    1399:	je     12c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    139f:	test   %r12,%r12
    13a2:	je     1390 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x150>
    13a4:	mov    0x0(%rbp,%rdi,4),%ebx
    13a8:	cmp    $0x7,%rsi
    13ac:	setb   %r13b
    13b0:	mov    %rdi,%r8
    13b3:	imul   %rcx,%r8
    13b7:	mov    -0x60(%rsp),%rdx
    13bc:	lea    (%rdx,%r8,4),%r8
    13c0:	or     %r11b,%r13b
    13c3:	je     13d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x190>
    13c5:	mov    -0x8(%rsp),%r13
    13ca:	jmp    1470 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x230>
    13cf:	nop
    13d0:	add    -0x18(%rsp),%r8
    13d5:	movd   %ebx,%xmm0
    13d9:	pshufd $0x0,%xmm0,%xmm0
    13de:	pshufd $0xf5,%xmm0,%xmm1
    13e3:	xor    %r13d,%r13d
    13e6:	cs nopw 0x0(%rax,%rax,1)
    13f0:	movdqu -0x10(%r14,%r13,4),%xmm2
    13f7:	movdqu (%r14,%r13,4),%xmm3
    13fd:	movdqu -0x10(%r15,%r13,4),%xmm4
    1404:	movdqu (%r15,%r13,4),%xmm5
    140a:	pshufd $0xf5,%xmm4,%xmm6
    140f:	pmuludq %xmm0,%xmm4
    1413:	pshufd $0xe8,%xmm4,%xmm4
    1418:	pmuludq %xmm1,%xmm6
    141c:	pshufd $0xe8,%xmm6,%xmm6
    1421:	punpckldq %xmm6,%xmm4
    1425:	paddd  %xmm2,%xmm4
    1429:	pshufd $0xf5,%xmm5,%xmm2
    142e:	pmuludq %xmm0,%xmm5
    1432:	pshufd $0xe8,%xmm5,%xmm5
    1437:	pmuludq %xmm1,%xmm2
    143b:	pshufd $0xe8,%xmm2,%xmm2
    1440:	punpckldq %xmm2,%xmm5
    1444:	paddd  %xmm3,%xmm5
    1448:	movdqu %xmm4,-0x10(%r14,%r13,4)
    144f:	movdqu %xmm5,(%r14,%r13,4)
    1455:	add    $0x8,%r13
    1459:	cmp    %r13,%r10
    145c:	jne    13f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1b0>
    145e:	mov    -0x20(%rsp),%r13
    1463:	cmp    %r10,-0x10(%rsp)
    1468:	je     1390 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x150>
    146e:	xchg   %ax,%ax
    1470:	mov    (%r8),%edx
    1473:	imul   %ebx,%edx
    1476:	add    %edx,0x0(%r13)
    147a:	add    $0x4,%r13
    147e:	add    $0x4,%r8
    1482:	cmp    %rax,%r13
    1485:	jne    1470 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x230>
    1487:	jmp    1390 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x150>
    148c:	pop    %rbx
    148d:	pop    %r12
    148f:	pop    %r13
    1491:	pop    %r14
    1493:	pop    %r15
    1495:	pop    %rbp
    1496:	ret
    1497:	nopw   0x0(%rax,%rax,1)
