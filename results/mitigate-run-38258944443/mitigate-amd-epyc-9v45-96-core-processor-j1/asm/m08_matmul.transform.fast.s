0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	mov    %rdx,-0x40(%rsp)
    124f:	test   %rcx,%rcx
    1252:	je     14fa <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2ba>
    1258:	mov    (%rdi),%rax
    125b:	mov    0x8(%rdi),%rdx
    125f:	sub    %rax,%rdx
    1262:	sar    $0x2,%rdx
    1266:	mov    %rdx,-0x48(%rsp)
    126b:	mov    (%rsi),%rdx
    126e:	mov    0x8(%rsi),%rsi
    1272:	mov    %rdx,-0x58(%rsp)
    1277:	sub    %rdx,%rsi
    127a:	sar    $0x2,%rsi
    127e:	mov    %rsi,-0x68(%rsp)
    1283:	lea    0x0(,%rcx,4),%rdx
    128b:	mov    %rdx,-0x70(%rsp)
    1290:	lea    -0x1(%rcx),%rdx
    1294:	imul   %rcx,%rdx
    1298:	shl    $0x2,%rdx
    129c:	mov    %rdx,-0x60(%rsp)
    12a1:	mov    %rax,-0x50(%rsp)
    12a6:	lea    0x10(%rax),%rbx
    12aa:	xor    %esi,%esi
    12ac:	jmp    12c6 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x86>
    12ae:	xchg   %ax,%ax
    12b0:	mov    -0x38(%rsp),%rsi
    12b5:	inc    %rsi
    12b8:	add    -0x70(%rsp),%rbx
    12bd:	cmp    %rcx,%rsi
    12c0:	je     14fa <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2ba>
    12c6:	mov    %rsi,%rax
    12c9:	imul   %rcx,%rax
    12cd:	mov    -0x48(%rsp),%r15
    12d2:	sub    %rax,%r15
    12d5:	jb     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    12db:	cmp    $0xffffffffffffffff,%rcx
    12df:	je     1310 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xd0>
    12e1:	cmp    %rcx,%r15
    12e4:	jb     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    12ea:	mov    -0x68(%rsp),%rdx
    12ef:	sub    %rax,%rdx
    12f2:	jb     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    12f8:	mov    %rcx,%r15
    12fb:	mov    %rcx,%r12
    12fe:	cmp    %rcx,%rdx
    1301:	jae    131e <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xde>
    1303:	jmp    1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    1308:	nopl   0x0(%rax,%rax,1)
    1310:	mov    -0x68(%rsp),%r12
    1315:	sub    %rax,%r12
    1318:	jb     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    131e:	mov    -0x70(%rsp),%rdi
    1323:	mov    %rdi,%rdx
    1326:	mov    %rsi,-0x38(%rsp)
    132b:	imul   %rsi,%rdx
    132f:	mov    -0x50(%rsp),%rsi
    1334:	add    %rsi,%rdx
    1337:	test   %rdi,%rdi
    133a:	sets   %r10b
    133e:	lea    (%rsi,%rax,4),%r14
    1342:	mov    -0x58(%rsp),%rsi
    1347:	lea    (%rsi,%rax,4),%rbp
    134b:	mov    -0x40(%rsp),%rax
    1350:	mov    (%rax),%r13
    1353:	mov    0x8(%rax),%r9
    1357:	sub    %r13,%r9
    135a:	sar    $0x2,%r9
    135e:	lea    (%r14,%r15,4),%rdi
    1362:	lea    (%rdx,%r15,4),%rax
    1366:	mov    -0x60(%rsp),%rsi
    136b:	add    %r13,%rsi
    136e:	lea    (%rsi,%r15,4),%r8
    1372:	movabs $0x3fffffffffffffff,%rsi
    137c:	lea    (%r15,%rsi,1),%r11
    1380:	and    %rsi,%r11
    1383:	mov    %r11,-0x10(%rsp)
    1388:	inc    %r11
    138b:	cmp    %r8,%rdx
    138e:	setb   %dl
    1391:	cmp    %rax,%r13
    1394:	setb   %r8b
    1398:	and    %dl,%r8b
    139b:	or     %r10b,%r8b
    139e:	mov    %r11,-0x20(%rsp)
    13a3:	and    $0xfffffffffffffff8,%r11
    13a7:	lea    0x0(,%r11,4),%rax
    13af:	mov    %rax,-0x28(%rsp)
    13b4:	mov    %r14,-0x18(%rsp)
    13b9:	lea    (%r14,%r11,4),%rax
    13bd:	mov    %rax,-0x30(%rsp)
    13c2:	mov    %r13,-0x8(%rsp)
    13c7:	lea    0x10(%r13),%r14
    13cb:	xor    %r13d,%r13d
    13ce:	jmp    13e1 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1a1>
    13d0:	inc    %r13
    13d3:	add    -0x70(%rsp),%r14
    13d8:	cmp    %rcx,%r13
    13db:	je     12b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    13e1:	cmp    %r12,%r13
    13e4:	je     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    13ea:	mov    %r13,%rax
    13ed:	imul   %rcx,%rax
    13f1:	mov    %r9,%r10
    13f4:	sub    %rax,%r10
    13f7:	jb     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    13fd:	mov    0x0(%rbp,%r13,4),%edx
    1402:	cmp    $0xffffffffffffffff,%rcx
    1406:	je     1411 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1d1>
    1408:	cmp    %rcx,%r10
    140b:	jb     1505 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c5>
    1411:	test   %r15,%r15
    1414:	je     13d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x190>
    1416:	cmpq   $0x7,-0x10(%rsp)
    141c:	setb   %r10b
    1420:	mov    -0x8(%rsp),%rsi
    1425:	lea    (%rsi,%rax,4),%rax
    1429:	or     %r8b,%r10b
    142c:	je     1440 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    142e:	mov    -0x18(%rsp),%r10
    1433:	jmp    14e0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2a0>
    1438:	nopl   0x0(%rax,%rax,1)
    1440:	add    -0x28(%rsp),%rax
    1445:	movd   %edx,%xmm0
    1449:	pshufd $0x0,%xmm0,%xmm0
    144e:	pshufd $0xf5,%xmm0,%xmm1
    1453:	xor    %r10d,%r10d
    1456:	cs nopw 0x0(%rax,%rax,1)
    1460:	movdqu -0x10(%rbx,%r10,4),%xmm2
    1467:	movdqu (%rbx,%r10,4),%xmm3
    146d:	movdqu -0x10(%r14,%r10,4),%xmm4
    1474:	movdqu (%r14,%r10,4),%xmm5
    147a:	pshufd $0xf5,%xmm4,%xmm6
    147f:	pmuludq %xmm0,%xmm4
    1483:	pshufd $0xe8,%xmm4,%xmm4
    1488:	pmuludq %xmm1,%xmm6
    148c:	pshufd $0xe8,%xmm6,%xmm6
    1491:	punpckldq %xmm6,%xmm4
    1495:	paddd  %xmm2,%xmm4
    1499:	pshufd $0xf5,%xmm5,%xmm2
    149e:	pmuludq %xmm0,%xmm5
    14a2:	pshufd $0xe8,%xmm5,%xmm5
    14a7:	pmuludq %xmm1,%xmm2
    14ab:	pshufd $0xe8,%xmm2,%xmm2
    14b0:	punpckldq %xmm2,%xmm5
    14b4:	paddd  %xmm3,%xmm5
    14b8:	movdqu %xmm4,-0x10(%rbx,%r10,4)
    14bf:	movdqu %xmm5,(%rbx,%r10,4)
    14c5:	add    $0x8,%r10
    14c9:	cmp    %r10,%r11
    14cc:	jne    1460 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x220>
    14ce:	mov    -0x30(%rsp),%r10
    14d3:	cmp    %r11,-0x20(%rsp)
    14d8:	je     13d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x190>
    14de:	xchg   %ax,%ax
    14e0:	mov    (%rax),%esi
    14e2:	imul   %edx,%esi
    14e5:	add    %esi,(%r10)
    14e8:	add    $0x4,%r10
    14ec:	add    $0x4,%rax
    14f0:	cmp    %rdi,%r10
    14f3:	jne    14e0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2a0>
    14f5:	jmp    13d0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x190>
    14fa:	pop    %rbx
    14fb:	pop    %r12
    14fd:	pop    %r13
    14ff:	pop    %r14
    1501:	pop    %r15
    1503:	pop    %rbp
    1504:	ret
    1505:	ud2
    1507:	nopw   0x0(%rax,%rax,1)
