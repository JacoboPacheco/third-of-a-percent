0000000000001220 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1220:	push   %rbp
    1221:	push   %r15
    1223:	push   %r14
    1225:	push   %r13
    1227:	push   %r12
    1229:	push   %rbx
    122a:	mov    %rdi,-0x8(%rsp)
    122f:	test   %rcx,%rcx
    1232:	je     14cf <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2af>
    1238:	mov    (%rsi),%rax
    123b:	mov    0x8(%rsi),%rsi
    123f:	mov    %rax,-0x18(%rsp)
    1244:	sub    %rax,%rsi
    1247:	sar    $0x2,%rsi
    124b:	mov    %rsi,-0x10(%rsp)
    1250:	lea    0x0(,%rcx,4),%r10
    1258:	lea    -0x1(%rcx),%rax
    125c:	mov    %rax,-0x78(%rsp)
    1261:	xor    %ebx,%ebx
    1263:	xor    %eax,%eax
    1265:	mov    %rax,-0x80(%rsp)
    126a:	xor    %eax,%eax
    126c:	mov    %rdx,-0x50(%rsp)
    1271:	mov    %r10,-0x68(%rsp)
    1276:	mov    %rax,%r14
    1279:	imul   %rcx,%r14
    127d:	mov    %r10,%rsi
    1280:	mov    %rax,-0x48(%rsp)
    1285:	imul   %rax,%rsi
    1289:	mov    %rsi,-0x30(%rsp)
    128e:	mov    (%rdx),%rbp
    1291:	mov    0x8(%rdx),%r11
    1295:	sub    %rbp,%r11
    1298:	sar    $0x2,%r11
    129c:	lea    0x4(%rbp),%rax
    12a0:	mov    %rax,-0x38(%rsp)
    12a5:	mov    %rbp,-0x40(%rsp)
    12aa:	xor    %eax,%eax
    12ac:	mov    %rax,-0x70(%rsp)
    12b1:	xor    %r15d,%r15d
    12b4:	xor    %r12d,%r12d
    12b7:	mov    -0x80(%rsp),%rdx
    12bc:	mov    %r14,-0x60(%rsp)
    12c1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12d0:	cmp    %r15,%r11
    12d3:	mov    %r15,%rsi
    12d6:	cmova  %r11,%rsi
    12da:	mov    %r12,%rax
    12dd:	imul   %rcx,%rax
    12e1:	mov    %r11,%r8
    12e4:	sub    %rax,%r8
    12e7:	mov    $0x0,%edi
    12ec:	cmovae %r8,%rdi
    12f0:	lea    (%r12,%r14,1),%r9
    12f4:	cmp    %r9,-0x10(%rsp)
    12f9:	jbe    14dd <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2bd>
    12ff:	mov    %r12,-0x58(%rsp)
    1304:	mov    %r11,%r10
    1307:	sub    %rax,%r10
    130a:	mov    $0x0,%eax
    130f:	cmovb  %rax,%r10
    1313:	mov    -0x8(%rsp),%rax
    1318:	mov    (%rax),%r13
    131b:	mov    0x8(%rax),%rax
    131f:	sub    %r13,%rax
    1322:	sar    $0x2,%rax
    1326:	cmp    %r14,%rax
    1329:	mov    %r14,%r12
    132c:	cmova  %rax,%r12
    1330:	sub    %r14,%r12
    1333:	mov    -0x78(%rsp),%r8
    1338:	cmp    %r8,%r12
    133b:	cmovb  %r12,%r8
    133f:	cmp    %r10,%r8
    1342:	cmovae %r10,%r8
    1346:	mov    -0x18(%rsp),%r10
    134b:	mov    (%r10,%r9,4),%r14d
    134f:	inc    %r8
    1352:	mov    $0x0,%r9d
    1358:	cmp    $0x8,%r8
    135c:	jbe    144f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x22f>
    1362:	mov    -0x68(%rsp),%r9
    1367:	imul   -0x58(%rsp),%r9
    136d:	mov    -0x38(%rsp),%rdx
    1372:	add    %r9,%rdx
    1375:	mov    %rdx,-0x20(%rsp)
    137a:	mov    -0x30(%rsp),%rdx
    137f:	add    %r13,%rdx
    1382:	mov    %rdx,-0x28(%rsp)
    1387:	mov    -0x60(%rsp),%rdx
    138c:	cmp    %rdx,%rax
    138f:	mov    %rdx,%r10
    1392:	cmova  %rax,%r10
    1396:	sub    %rdx,%r10
    1399:	mov    -0x78(%rsp),%rdx
    139e:	cmp    %rdx,%r10
    13a1:	cmovae %rdx,%r10
    13a5:	mov    -0x28(%rsp),%rdx
    13aa:	cmp    %rdi,%r10
    13ad:	cmovae %rdi,%r10
    13b1:	mov    -0x20(%rsp),%rdi
    13b6:	lea    (%rdi,%r10,4),%rdi
    13ba:	cmp    %rdi,%rdx
    13bd:	jae    13e0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    13bf:	add    -0x40(%rsp),%r9
    13c4:	lea    (%rdx,%r10,4),%rdi
    13c8:	add    $0x4,%rdi
    13cc:	cmp    %rdi,%r9
    13cf:	jae    13e0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x1c0>
    13d1:	xor    %r9d,%r9d
    13d4:	mov    -0x80(%rsp),%rdx
    13d9:	jmp    144f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x22f>
    13db:	nopl   0x0(%rax,%rax,1)
    13e0:	add    -0x70(%rsp),%rsi
    13e5:	mov    %r8d,%edi
    13e8:	and    $0x7,%edi
    13eb:	mov    $0x8,%edx
    13f0:	cmove  %rdx,%rdi
    13f4:	sub    %rdi,%r8
    13f7:	vmovd  %r14d,%xmm0
    13fc:	cmp    %rsi,%r12
    13ff:	cmovb  %r12,%rsi
    1403:	vpbroadcastd %xmm0,%ymm0
    1408:	mov    -0x78(%rsp),%rdx
    140d:	cmp    %rdx,%rsi
    1410:	cmovae %rdx,%rsi
    1414:	sub    %rdi,%rsi
    1417:	inc    %rsi
    141a:	mov    -0x80(%rsp),%rdx
    141f:	lea    (%rdx,%r13,1),%rdi
    1423:	xor    %r9d,%r9d
    1426:	cs nopw 0x0(%rax,%rax,1)
    1430:	vpmulld 0x0(%rbp,%r9,4),%ymm0,%ymm1
    1437:	vpaddd (%rdi,%r9,4),%ymm1,%ymm1
    143d:	vmovdqu %ymm1,(%rdi,%r9,4)
    1443:	add    $0x8,%r9
    1447:	cmp    %r9,%rsi
    144a:	jne    1430 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x210>
    144c:	mov    %r8,%r9
    144f:	add    %rdx,%r13
    1452:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1460:	lea    (%r15,%r9,1),%rsi
    1464:	cmp    %rsi,%r11
    1467:	jbe    14dd <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2bd>
    1469:	lea    (%rbx,%r9,1),%rsi
    146d:	cmp    %rsi,%rax
    1470:	jbe    14dd <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2bd>
    1472:	mov    0x0(%rbp,%r9,4),%esi
    1477:	imul   %r14d,%esi
    147b:	add    %esi,0x0(%r13,%r9,4)
    1480:	inc    %r9
    1483:	cmp    %r9,%rcx
    1486:	jne    1460 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x240>
    1488:	mov    -0x58(%rsp),%r12
    148d:	inc    %r12
    1490:	add    %rcx,%r15
    1493:	sub    %rcx,-0x70(%rsp)
    1498:	mov    -0x68(%rsp),%r10
    149d:	add    %r10,%rbp
    14a0:	cmp    %rcx,%r12
    14a3:	mov    -0x60(%rsp),%r14
    14a8:	jne    12d0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xb0>
    14ae:	mov    -0x48(%rsp),%rax
    14b3:	inc    %rax
    14b6:	add    %r10,%rdx
    14b9:	mov    %rdx,-0x80(%rsp)
    14be:	add    %rcx,%rbx
    14c1:	cmp    %rcx,%rax
    14c4:	mov    -0x50(%rsp),%rdx
    14c9:	jne    1276 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x56>
    14cf:	pop    %rbx
    14d0:	pop    %r12
    14d2:	pop    %r13
    14d4:	pop    %r14
    14d6:	pop    %r15
    14d8:	pop    %rbp
    14d9:	vzeroupper
    14dc:	ret
    14dd:	ud2
    14df:	nop
