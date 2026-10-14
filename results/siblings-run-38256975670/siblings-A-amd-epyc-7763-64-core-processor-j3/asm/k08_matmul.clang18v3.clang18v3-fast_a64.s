0000000000001240 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1240:	push   %rbp
    1241:	push   %r15
    1243:	push   %r14
    1245:	push   %r13
    1247:	push   %r12
    1249:	push   %rbx
    124a:	mov    %rdi,-0x8(%rsp)
    124f:	test   %rcx,%rcx
    1252:	je     156f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x32f>
    1258:	mov    (%rsi),%rax
    125b:	mov    0x8(%rsi),%rsi
    125f:	mov    %rax,-0x18(%rsp)
    1264:	sub    %rax,%rsi
    1267:	sar    $0x2,%rsi
    126b:	mov    %rsi,-0x10(%rsp)
    1270:	lea    0x0(,%rcx,4),%r10
    1278:	lea    -0x1(%rcx),%rax
    127c:	mov    %rax,-0x78(%rsp)
    1281:	xor    %ebx,%ebx
    1283:	xor    %eax,%eax
    1285:	mov    %rax,-0x80(%rsp)
    128a:	xor    %eax,%eax
    128c:	mov    %rdx,-0x50(%rsp)
    1291:	mov    %r10,-0x68(%rsp)
    1296:	mov    %rax,%r14
    1299:	imul   %rcx,%r14
    129d:	mov    %r10,%rsi
    12a0:	mov    %rax,-0x48(%rsp)
    12a5:	imul   %rax,%rsi
    12a9:	mov    %rsi,-0x30(%rsp)
    12ae:	mov    (%rdx),%rbp
    12b1:	mov    0x8(%rdx),%r11
    12b5:	sub    %rbp,%r11
    12b8:	sar    $0x2,%r11
    12bc:	lea    0x4(%rbp),%rax
    12c0:	mov    %rax,-0x38(%rsp)
    12c5:	mov    %rbp,-0x40(%rsp)
    12ca:	xor    %eax,%eax
    12cc:	mov    %rax,-0x70(%rsp)
    12d1:	xor    %r15d,%r15d
    12d4:	xor    %r12d,%r12d
    12d7:	mov    -0x80(%rsp),%rdx
    12dc:	mov    %r14,-0x60(%rsp)
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	cmp    %r15,%r11
    1303:	mov    %r15,%rsi
    1306:	cmova  %r11,%rsi
    130a:	mov    %r12,%rax
    130d:	imul   %rcx,%rax
    1311:	mov    %r11,%r8
    1314:	sub    %rax,%r8
    1317:	mov    $0x0,%edi
    131c:	cmovae %r8,%rdi
    1320:	lea    (%r12,%r14,1),%r9
    1324:	cmp    %r9,-0x10(%rsp)
    1329:	jbe    157d <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x33d>
    132f:	mov    %r12,-0x58(%rsp)
    1334:	mov    %r11,%r10
    1337:	sub    %rax,%r10
    133a:	mov    $0x0,%eax
    133f:	cmovb  %rax,%r10
    1343:	mov    -0x8(%rsp),%rax
    1348:	mov    (%rax),%r13
    134b:	mov    0x8(%rax),%rax
    134f:	sub    %r13,%rax
    1352:	sar    $0x2,%rax
    1356:	cmp    %r14,%rax
    1359:	mov    %r14,%r12
    135c:	cmova  %rax,%r12
    1360:	sub    %r14,%r12
    1363:	mov    -0x78(%rsp),%r8
    1368:	cmp    %r8,%r12
    136b:	cmovb  %r12,%r8
    136f:	cmp    %r10,%r8
    1372:	cmovae %r10,%r8
    1376:	mov    -0x18(%rsp),%r10
    137b:	mov    (%r10,%r9,4),%r14d
    137f:	inc    %r8
    1382:	mov    $0x0,%r9d
    1388:	cmp    $0x8,%r8
    138c:	jbe    14df <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x29f>
    1392:	mov    -0x68(%rsp),%r9
    1397:	imul   -0x58(%rsp),%r9
    139d:	mov    -0x38(%rsp),%rdx
    13a2:	add    %r9,%rdx
    13a5:	mov    %rdx,-0x20(%rsp)
    13aa:	mov    -0x30(%rsp),%rdx
    13af:	add    %r13,%rdx
    13b2:	mov    %rdx,-0x28(%rsp)
    13b7:	mov    -0x60(%rsp),%rdx
    13bc:	cmp    %rdx,%rax
    13bf:	mov    %rdx,%r10
    13c2:	cmova  %rax,%r10
    13c6:	sub    %rdx,%r10
    13c9:	mov    -0x78(%rsp),%rdx
    13ce:	cmp    %rdx,%r10
    13d1:	cmovae %rdx,%r10
    13d5:	mov    -0x28(%rsp),%rdx
    13da:	cmp    %rdi,%r10
    13dd:	cmovae %rdi,%r10
    13e1:	mov    -0x20(%rsp),%rdi
    13e6:	lea    (%rdi,%r10,4),%rdi
    13ea:	cmp    %rdi,%rdx
    13ed:	jae    1440 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    13ef:	add    -0x40(%rsp),%r9
    13f4:	lea    (%rdx,%r10,4),%rdi
    13f8:	add    $0x4,%rdi
    13fc:	cmp    %rdi,%r9
    13ff:	jae    1440 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x200>
    1401:	xor    %r9d,%r9d
    1404:	mov    -0x80(%rsp),%rdx
    1409:	jmp    14df <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x29f>
    140e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    141d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    142c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    143b:	nopl   0x0(%rax,%rax,1)
    1440:	add    -0x70(%rsp),%rsi
    1445:	mov    %r8d,%edi
    1448:	and    $0x7,%edi
    144b:	mov    $0x8,%edx
    1450:	cmove  %rdx,%rdi
    1454:	sub    %rdi,%r8
    1457:	vmovd  %r14d,%xmm0
    145c:	cmp    %rsi,%r12
    145f:	cmovb  %r12,%rsi
    1463:	vpbroadcastd %xmm0,%ymm0
    1468:	mov    -0x78(%rsp),%rdx
    146d:	cmp    %rdx,%rsi
    1470:	cmovae %rdx,%rsi
    1474:	sub    %rdi,%rsi
    1477:	inc    %rsi
    147a:	mov    -0x80(%rsp),%rdx
    147f:	lea    (%rdx,%r13,1),%rdi
    1483:	xor    %r9d,%r9d
    1486:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1495:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14a4:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14c0:	vpmulld 0x0(%rbp,%r9,4),%ymm0,%ymm1
    14c7:	vpaddd (%rdi,%r9,4),%ymm1,%ymm1
    14cd:	vmovdqu %ymm1,(%rdi,%r9,4)
    14d3:	add    $0x8,%r9
    14d7:	cmp    %r9,%rsi
    14da:	jne    14c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x280>
    14dc:	mov    %r8,%r9
    14df:	add    %rdx,%r13
    14e2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14f1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1500:	lea    (%r15,%r9,1),%rsi
    1504:	cmp    %rsi,%r11
    1507:	jbe    157d <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x33d>
    1509:	lea    (%rbx,%r9,1),%rsi
    150d:	cmp    %rsi,%rax
    1510:	jbe    157d <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x33d>
    1512:	mov    0x0(%rbp,%r9,4),%esi
    1517:	imul   %r14d,%esi
    151b:	add    %esi,0x0(%r13,%r9,4)
    1520:	inc    %r9
    1523:	cmp    %r9,%rcx
    1526:	jne    1500 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x2c0>
    1528:	mov    -0x58(%rsp),%r12
    152d:	inc    %r12
    1530:	add    %rcx,%r15
    1533:	sub    %rcx,-0x70(%rsp)
    1538:	mov    -0x68(%rsp),%r10
    153d:	add    %r10,%rbp
    1540:	cmp    %rcx,%r12
    1543:	mov    -0x60(%rsp),%r14
    1548:	jne    1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    154e:	mov    -0x48(%rsp),%rax
    1553:	inc    %rax
    1556:	add    %r10,%rdx
    1559:	mov    %rdx,-0x80(%rsp)
    155e:	add    %rcx,%rbx
    1561:	cmp    %rcx,%rax
    1564:	mov    -0x50(%rsp),%rdx
    1569:	jne    1296 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x56>
    156f:	pop    %rbx
    1570:	pop    %r12
    1572:	pop    %r13
    1574:	pop    %r14
    1576:	pop    %r15
    1578:	pop    %rbp
    1579:	vzeroupper
    157c:	ret
    157d:	ud2
    157f:	nop
