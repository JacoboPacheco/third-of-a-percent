0000000000001240 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	test   %rcx,%rcx
    124d:	je     1515 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2d5>
    1253:	mov    %rcx,%rbp
    1256:	mov    (%rdi),%r8
    1259:	mov    0x8(%rdi),%rcx
    125d:	sub    %r8,%rcx
    1260:	sar    $0x2,%rcx
    1264:	mov    (%rsi),%rax
    1267:	mov    0x8(%rsi),%rsi
    126b:	mov    %rax,-0x30(%rsp)
    1270:	sub    %rax,%rsi
    1273:	sar    $0x2,%rsi
    1277:	lea    0x0(,%rbp,4),%rax
    127f:	mov    %rax,-0x70(%rsp)
    1284:	lea    -0x1(%rbp),%r10
    1288:	lea    0x4(%r8),%rax
    128c:	mov    %rax,-0x38(%rsp)
    1291:	lea    0x10(%r8),%rbx
    1295:	xor    %eax,%eax
    1297:	mov    %r8,%r12
    129a:	mov    %rsi,-0x58(%rsp)
    129f:	mov    %rdx,-0x40(%rsp)
    12a4:	mov    %r8,-0x48(%rsp)
    12a9:	mov    %rcx,-0x50(%rsp)
    12ae:	mov    %rax,-0x68(%rsp)
    12b3:	imul   %rbp,%rax
    12b7:	sub    %rax,%rcx
    12ba:	jb     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    12c0:	cmp    $0xffffffffffffffff,%rbp
    12c4:	je     12f0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xb0>
    12c6:	cmp    %rbp,%rcx
    12c9:	jb     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    12cf:	sub    %rax,%rsi
    12d2:	jb     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    12d8:	mov    %rbp,%rcx
    12db:	mov    %rbp,%r15
    12de:	cmp    %rbp,%rsi
    12e1:	jae    12fc <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xbc>
    12e3:	jmp    1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    12e8:	nopl   0x0(%rax,%rax,1)
    12f0:	mov    %rsi,%r15
    12f3:	sub    %rax,%r15
    12f6:	jb     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    12fc:	mov    -0x70(%rsp),%rsi
    1301:	imul   -0x68(%rsp),%rsi
    1307:	lea    (%r8,%rsi,1),%rdi
    130b:	mov    %rdi,-0x10(%rsp)
    1310:	add    -0x38(%rsp),%rsi
    1315:	mov    %rsi,-0x20(%rsp)
    131a:	mov    -0x30(%rsp),%rsi
    131f:	lea    (%rsi,%rax,4),%r9
    1323:	mov    (%rdx),%rax
    1326:	mov    0x8(%rdx),%rdx
    132a:	sub    %rax,%rdx
    132d:	sar    $0x2,%rdx
    1331:	mov    %rdx,-0x8(%rsp)
    1336:	lea    0x4(%rax),%rdx
    133a:	mov    %rdx,-0x18(%rsp)
    133f:	lea    0x10(%rax),%rsi
    1343:	mov    %rax,-0x28(%rsp)
    1348:	xor    %r8d,%r8d
    134b:	mov    %r9,-0x60(%rsp)
    1350:	cmp    %r15,%r8
    1353:	je     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    1359:	mov    %r8,%r11
    135c:	imul   %rbp,%r11
    1360:	mov    -0x8(%rsp),%rdx
    1365:	sub    %r11,%rdx
    1368:	jb     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    136e:	mov    (%r9,%r8,4),%r14d
    1372:	cmp    $0xffffffffffffffff,%rbp
    1376:	je     1384 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x144>
    1378:	cmp    %rbp,%rdx
    137b:	mov    %rbp,%rdx
    137e:	jb     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    1384:	cmp    %rcx,%rdx
    1387:	mov    %rcx,%r13
    138a:	cmovb  %rdx,%r13
    138e:	cmp    %r10,%r13
    1391:	cmovae %r10,%r13
    1395:	inc    %r13
    1398:	cmp    $0x8,%r13
    139c:	ja     13b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x170>
    139e:	xor    %r13d,%r13d
    13a1:	jmp    14b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x270>
    13a6:	cs nopw 0x0(%rax,%rax,1)
    13b0:	mov    %r15,%r9
    13b3:	mov    -0x70(%rsp),%r15
    13b8:	imul   %r8,%r15
    13bc:	mov    -0x18(%rsp),%rdi
    13c1:	add    %r15,%rdi
    13c4:	cmp    %rcx,%rdx
    13c7:	mov    %rcx,%r11
    13ca:	cmovb  %rdx,%r11
    13ce:	cmp    %r10,%r11
    13d1:	cmovae %r10,%r11
    13d5:	lea    (%rdi,%r11,4),%rdi
    13d9:	cmp    %rdi,-0x10(%rsp)
    13de:	jae    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    13e0:	add    -0x28(%rsp),%r15
    13e5:	mov    -0x20(%rsp),%rdi
    13ea:	lea    (%rdi,%r11,4),%rdi
    13ee:	cmp    %rdi,%r15
    13f1:	jae    1400 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    13f3:	xor    %r13d,%r13d
    13f6:	jmp    149e <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x25e>
    13fb:	nopl   0x0(%rax,%rax,1)
    1400:	mov    %r13d,%edi
    1403:	and    $0x7,%edi
    1406:	mov    $0x8,%r11d
    140c:	cmove  %r11,%rdi
    1410:	sub    %rdi,%r13
    1413:	movd   %r14d,%xmm0
    1418:	pshufd $0x0,%xmm0,%xmm0
    141d:	pshufd $0xf5,%xmm0,%xmm1
    1422:	xor    %r15d,%r15d
    1425:	data16 cs nopw 0x0(%rax,%rax,1)
    1430:	movdqu -0x10(%rsi,%r15,4),%xmm2
    1437:	movdqu (%rsi,%r15,4),%xmm3
    143d:	pshufd $0xf5,%xmm2,%xmm4
    1442:	pmuludq %xmm0,%xmm2
    1446:	pshufd $0xe8,%xmm2,%xmm2
    144b:	pmuludq %xmm1,%xmm4
    144f:	pshufd $0xe8,%xmm4,%xmm4
    1454:	punpckldq %xmm4,%xmm2
    1458:	pshufd $0xf5,%xmm3,%xmm4
    145d:	pmuludq %xmm0,%xmm3
    1461:	pshufd $0xe8,%xmm3,%xmm3
    1466:	pmuludq %xmm1,%xmm4
    146a:	pshufd $0xe8,%xmm4,%xmm4
    146f:	punpckldq %xmm4,%xmm3
    1473:	movdqu -0x10(%rbx,%r15,4),%xmm4
    147a:	paddd  %xmm2,%xmm4
    147e:	movdqu (%rbx,%r15,4),%xmm2
    1484:	paddd  %xmm3,%xmm2
    1488:	movdqu %xmm4,-0x10(%rbx,%r15,4)
    148f:	movdqu %xmm2,(%rbx,%r15,4)
    1495:	add    $0x8,%r15
    1499:	cmp    %r15,%r13
    149c:	jne    1430 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1f0>
    149e:	mov    %r9,%r15
    14a1:	mov    -0x60(%rsp),%r9
    14a6:	cs nopw 0x0(%rax,%rax,1)
    14b0:	cmp    %r13,%rdx
    14b3:	je     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    14b5:	cmp    %r13,%rcx
    14b8:	je     1520 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2e0>
    14ba:	mov    (%rax,%r13,4),%edi
    14be:	imul   %r14d,%edi
    14c2:	add    %edi,(%r12,%r13,4)
    14c6:	inc    %r13
    14c9:	cmp    %r13,%rbp
    14cc:	jne    14b0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x270>
    14ce:	inc    %r8
    14d1:	mov    -0x70(%rsp),%rdx
    14d6:	add    %rdx,%rsi
    14d9:	add    %rdx,%rax
    14dc:	cmp    %rbp,%r8
    14df:	jne    1350 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x110>
    14e5:	mov    -0x68(%rsp),%rax
    14ea:	inc    %rax
    14ed:	mov    -0x70(%rsp),%rcx
    14f2:	add    %rcx,%rbx
    14f5:	add    %rcx,%r12
    14f8:	cmp    %rbp,%rax
    14fb:	mov    -0x40(%rsp),%rdx
    1500:	mov    -0x48(%rsp),%r8
    1505:	mov    -0x50(%rsp),%rcx
    150a:	mov    -0x58(%rsp),%rsi
    150f:	jne    12ae <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x6e>
    1515:	pop    %rbx
    1516:	pop    %r12
    1518:	pop    %r13
    151a:	pop    %r14
    151c:	pop    %r15
    151e:	pop    %rbp
    151f:	ret
    1520:	ud2
    1522:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
