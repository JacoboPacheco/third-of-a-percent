0000000000001280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	mov    (%rdx),%rax
    1283:	mov    0x8(%rdx),%r9
    1287:	mov    %r9,%r8
    128a:	sub    %rax,%r8
    128d:	mov    (%rdi),%rcx
    1290:	mov    0x8(%rdi),%rdx
    1294:	sub    %rcx,%rdx
    1297:	cmp    %r8,%rdx
    129a:	jb     14d5 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x255>
    12a0:	cmp    %rax,%r9
    12a3:	je     14d4 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x254>
    12a9:	sar    $0x2,%r8
    12ad:	cmp    $0x1,%r8
    12b1:	mov    %r8,%rdx
    12b4:	adc    $0x0,%rdx
    12b8:	cmp    $0x8,%r8
    12bc:	jae    12c8 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x48>
    12be:	xor    %r10d,%r10d
    12c1:	xor    %edi,%edi
    12c3:	jmp    13cb <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x14b>
    12c8:	mov    %rdx,%rdi
    12cb:	and    $0xfffffffffffffff8,%rdi
    12cf:	pxor   %xmm1,%xmm1
    12d3:	xor    %r10d,%r10d
    12d6:	movdqa 0xd32(%rip),%xmm0        # 2010 <_IO_stdin_used+0x10>
    12de:	pxor   %xmm2,%xmm2
    12e2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	movdqu (%rax,%r10,4),%xmm3
    1306:	movdqu 0x10(%rax,%r10,4),%xmm4
    130d:	movdqa %xmm1,%xmm5
    1311:	pxor   %xmm0,%xmm5
    1315:	movdqa %xmm3,%xmm6
    1319:	pxor   %xmm0,%xmm6
    131d:	pcmpgtd %xmm5,%xmm6
    1321:	pand   %xmm6,%xmm3
    1325:	pandn  %xmm1,%xmm6
    1329:	movdqa %xmm6,%xmm1
    132d:	por    %xmm3,%xmm1
    1331:	movdqa %xmm2,%xmm3
    1335:	pxor   %xmm0,%xmm3
    1339:	movdqa %xmm4,%xmm5
    133d:	pxor   %xmm0,%xmm5
    1341:	pcmpgtd %xmm3,%xmm5
    1345:	pand   %xmm5,%xmm4
    1349:	pandn  %xmm2,%xmm5
    134d:	movdqa %xmm5,%xmm2
    1351:	por    %xmm4,%xmm2
    1355:	add    $0x8,%r10
    1359:	cmp    %r10,%rdi
    135c:	jne    1300 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    135e:	movdqa %xmm2,%xmm3
    1362:	pxor   %xmm0,%xmm3
    1366:	movdqa %xmm1,%xmm4
    136a:	pxor   %xmm0,%xmm4
    136e:	pcmpgtd %xmm3,%xmm4
    1372:	pand   %xmm4,%xmm1
    1376:	pandn  %xmm2,%xmm4
    137a:	por    %xmm1,%xmm4
    137e:	pshufd $0xee,%xmm4,%xmm1
    1383:	movdqa %xmm4,%xmm2
    1387:	pxor   %xmm0,%xmm2
    138b:	movdqa %xmm1,%xmm3
    138f:	pxor   %xmm0,%xmm3
    1393:	pcmpgtd %xmm3,%xmm2
    1397:	pand   %xmm2,%xmm4
    139b:	pandn  %xmm1,%xmm2
    139f:	por    %xmm4,%xmm2
    13a3:	pshufd $0x55,%xmm2,%xmm1
    13a8:	movdqa %xmm2,%xmm3
    13ac:	pxor   %xmm0,%xmm3
    13b0:	pxor   %xmm1,%xmm0
    13b4:	pcmpgtd %xmm0,%xmm3
    13b8:	pand   %xmm3,%xmm2
    13bc:	pandn  %xmm1,%xmm3
    13c0:	por    %xmm2,%xmm3
    13c4:	movd   %xmm3,%r10d
    13c9:	jmp    13d9 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x159>
    13cb:	mov    (%rax,%rdi,4),%r11d
    13cf:	cmp    %r10d,%r11d
    13d2:	cmova  %r11d,%r10d
    13d6:	inc    %rdi
    13d9:	cmp    %rdi,%rdx
    13dc:	jne    13cb <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x14b>
    13de:	cmp    %rax,%r9
    13e1:	je     14d4 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x254>
    13e7:	mov    (%rsi),%rdi
    13ea:	mov    %r10d,%r9d
    13ed:	mov    0x8(%rsi),%rsi
    13f1:	sub    %rdi,%rsi
    13f4:	sar    $0x2,%rsi
    13f8:	cmp    %r9,%rsi
    13fb:	jbe    14d5 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x255>
    1401:	mov    %edx,%esi
    1403:	and    $0x3,%esi
    1406:	cmp    $0x4,%r8
    140a:	jae    1411 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x191>
    140c:	xor    %r8d,%r8d
    140f:	jmp    147f <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1ff>
    1411:	and    $0xfffffffffffffffc,%rdx
    1415:	xor    %r8d,%r8d
    1418:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1427:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1436:	cs nopw 0x0(%rax,%rax,1)
    1440:	mov    (%rax,%r8,4),%r9d
    1444:	mov    (%rdi,%r9,4),%r9d
    1448:	mov    %r9d,(%rcx,%r8,4)
    144c:	mov    0x4(%rax,%r8,4),%r9d
    1451:	mov    (%rdi,%r9,4),%r9d
    1455:	mov    %r9d,0x4(%rcx,%r8,4)
    145a:	mov    0x8(%rax,%r8,4),%r9d
    145f:	mov    (%rdi,%r9,4),%r9d
    1463:	mov    %r9d,0x8(%rcx,%r8,4)
    1468:	mov    0xc(%rax,%r8,4),%r9d
    146d:	mov    (%rdi,%r9,4),%r9d
    1471:	mov    %r9d,0xc(%rcx,%r8,4)
    1476:	add    $0x4,%r8
    147a:	cmp    %r8,%rdx
    147d:	jne    1440 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1c0>
    147f:	test   %rsi,%rsi
    1482:	je     14d4 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x254>
    1484:	lea    (%rcx,%r8,4),%rcx
    1488:	lea    (%rax,%r8,4),%rax
    148c:	xor    %edx,%edx
    148e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    149d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14ac:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    14bb:	nopl   0x0(%rax,%rax,1)
    14c0:	mov    (%rax,%rdx,4),%r8d
    14c4:	mov    (%rdi,%r8,4),%r8d
    14c8:	mov    %r8d,(%rcx,%rdx,4)
    14cc:	inc    %rdx
    14cf:	cmp    %rdx,%rsi
    14d2:	jne    14c0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x240>
    14d4:	ret
    14d5:	ud2
    14d7:	nopw   0x0(%rax,%rax,1)
