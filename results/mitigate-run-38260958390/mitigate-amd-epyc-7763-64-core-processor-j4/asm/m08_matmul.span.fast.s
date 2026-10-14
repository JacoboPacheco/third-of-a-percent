0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	test   %rcx,%rcx
    124d:	je     14df <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x29f>
    1253:	mov    %rcx,%r13
    1256:	mov    (%rdi),%r8
    1259:	mov    0x8(%rdi),%rdi
    125d:	sub    %r8,%rdi
    1260:	sar    $0x2,%rdi
    1264:	mov    (%rsi),%r11
    1267:	mov    0x8(%rsi),%rbx
    126b:	sub    %r11,%rbx
    126e:	sar    $0x2,%rbx
    1272:	lea    0x0(,%rcx,4),%rax
    127a:	mov    %rax,-0x28(%rsp)
    127f:	lea    -0x1(%rcx),%r10
    1283:	lea    0x4(%r8),%r14
    1287:	xor    %esi,%esi
    1289:	mov    %r8,%r15
    128c:	mov    %rdx,-0x30(%rsp)
    1291:	mov    %r8,-0x38(%rsp)
    1296:	mov    %rdi,-0x40(%rsp)
    129b:	mov    %r11,-0x48(%rsp)
    12a0:	mov    %rbx,-0x50(%rsp)
    12a5:	mov    %r14,-0x58(%rsp)
    12aa:	mov    %rsi,%rax
    12ad:	imul   %r13,%rax
    12b1:	mov    %rdi,%rcx
    12b4:	sub    %rax,%rcx
    12b7:	jb     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    12bd:	cmp    $0xffffffffffffffff,%r13
    12c1:	mov    %rsi,-0x68(%rsp)
    12c6:	je     12f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xb0>
    12c8:	cmp    %r13,%rcx
    12cb:	jb     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    12d1:	mov    %rbx,%rsi
    12d4:	sub    %rax,%rsi
    12d7:	jb     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    12dd:	mov    %r13,%rcx
    12e0:	mov    %r13,%r9
    12e3:	cmp    %r13,%rsi
    12e6:	jae    12fc <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xbc>
    12e8:	jmp    14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    12ed:	nopl   (%rax)
    12f0:	mov    %rbx,%r9
    12f3:	sub    %rax,%r9
    12f6:	jb     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    12fc:	mov    -0x28(%rsp),%rsi
    1301:	mov    %rsi,%rdi
    1304:	imul   -0x68(%rsp),%rdi
    130a:	add    %rdi,%r8
    130d:	mov    %r8,-0x8(%rsp)
    1312:	add    %r14,%rdi
    1315:	mov    %rdi,-0x18(%rsp)
    131a:	lea    (%r11,%rax,4),%r8
    131e:	mov    (%rdx),%r14
    1321:	mov    0x8(%rdx),%rbx
    1325:	mov    %rsi,%rbp
    1328:	sub    %r14,%rbx
    132b:	sar    $0x2,%rbx
    132f:	lea    0x4(%r14),%rax
    1333:	mov    %rax,-0x10(%rsp)
    1338:	mov    %r14,-0x20(%rsp)
    133d:	xor    %esi,%esi
    133f:	mov    %rbx,-0x60(%rsp)
    1344:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1350:	cmp    %r9,%rsi
    1353:	je     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    1359:	mov    %rsi,%rdi
    135c:	imul   %r13,%rdi
    1360:	mov    %rbx,%rax
    1363:	sub    %rdi,%rax
    1366:	jb     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    136c:	mov    (%r8,%rsi,4),%r11d
    1370:	cmp    $0xffffffffffffffff,%r13
    1374:	je     1382 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x142>
    1376:	cmp    %r13,%rax
    1379:	mov    %r13,%rax
    137c:	jb     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    1382:	cmp    %rcx,%rax
    1385:	mov    %rcx,%r12
    1388:	cmovb  %rax,%r12
    138c:	cmp    %r10,%r12
    138f:	cmovae %r10,%r12
    1393:	inc    %r12
    1396:	cmp    $0x4,%r12
    139a:	ja     13b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x170>
    139c:	xor    %r12d,%r12d
    139f:	jmp    1480 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    13a4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    13b0:	mov    %r9,%rbx
    13b3:	mov    %r8,%r9
    13b6:	mov    %rbp,%rdx
    13b9:	mov    %rbp,%rdi
    13bc:	imul   %rsi,%rdi
    13c0:	mov    -0x10(%rsp),%r8
    13c5:	add    %rdi,%r8
    13c8:	cmp    %rcx,%rax
    13cb:	mov    %rcx,%rbp
    13ce:	cmovb  %rax,%rbp
    13d2:	cmp    %r10,%rbp
    13d5:	cmovae %r10,%rbp
    13d9:	lea    (%r8,%rbp,4),%r8
    13dd:	cmp    %r8,-0x8(%rsp)
    13e2:	jae    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    13e4:	add    -0x20(%rsp),%rdi
    13e9:	mov    -0x18(%rsp),%r8
    13ee:	lea    (%r8,%rbp,4),%r8
    13f2:	cmp    %r8,%rdi
    13f5:	jae    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    13f7:	xor    %r12d,%r12d
    13fa:	jmp    146a <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x22a>
    13fc:	nopl   0x0(%rax)
    1400:	mov    %r12d,%edi
    1403:	and    $0x3,%edi
    1406:	mov    $0x4,%r8d
    140c:	cmove  %r8,%rdi
    1410:	sub    %rdi,%r12
    1413:	movd   %r11d,%xmm0
    1418:	pshufd $0x0,%xmm0,%xmm0
    141d:	pshufd $0xf5,%xmm0,%xmm1
    1422:	xor    %edi,%edi
    1424:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1430:	movdqu (%r14,%rdi,4),%xmm2
    1436:	pshufd $0xf5,%xmm2,%xmm3
    143b:	pmuludq %xmm0,%xmm2
    143f:	pshufd $0xe8,%xmm2,%xmm2
    1444:	pmuludq %xmm1,%xmm3
    1448:	pshufd $0xe8,%xmm3,%xmm3
    144d:	punpckldq %xmm3,%xmm2
    1451:	movdqu (%r15,%rdi,4),%xmm3
    1457:	paddd  %xmm2,%xmm3
    145b:	movdqu %xmm3,(%r15,%rdi,4)
    1461:	add    $0x4,%rdi
    1465:	cmp    %rdi,%r12
    1468:	jne    1430 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1f0>
    146a:	mov    %r9,%r8
    146d:	mov    %rbx,%r9
    1470:	mov    -0x60(%rsp),%rbx
    1475:	mov    %rdx,%rbp
    1478:	nopl   0x0(%rax,%rax,1)
    1480:	cmp    %r12,%rax
    1483:	je     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    1485:	cmp    %r12,%rcx
    1488:	je     14ea <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2aa>
    148a:	mov    (%r14,%r12,4),%edi
    148e:	imul   %r11d,%edi
    1492:	add    %edi,(%r15,%r12,4)
    1496:	inc    %r12
    1499:	cmp    %r12,%r13
    149c:	jne    1480 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    149e:	inc    %rsi
    14a1:	add    %rbp,%r14
    14a4:	cmp    %r13,%rsi
    14a7:	jne    1350 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x110>
    14ad:	mov    -0x68(%rsp),%rsi
    14b2:	inc    %rsi
    14b5:	add    %rbp,%r15
    14b8:	cmp    %r13,%rsi
    14bb:	mov    -0x30(%rsp),%rdx
    14c0:	mov    -0x38(%rsp),%r8
    14c5:	mov    -0x40(%rsp),%rdi
    14ca:	mov    -0x48(%rsp),%r11
    14cf:	mov    -0x50(%rsp),%rbx
    14d4:	mov    -0x58(%rsp),%r14
    14d9:	jne    12aa <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x6a>
    14df:	pop    %rbx
    14e0:	pop    %r12
    14e2:	pop    %r13
    14e4:	pop    %r14
    14e6:	pop    %r15
    14e8:	pop    %rbp
    14e9:	ret
    14ea:	ud2
    14ec:	nopl   0x0(%rax)
