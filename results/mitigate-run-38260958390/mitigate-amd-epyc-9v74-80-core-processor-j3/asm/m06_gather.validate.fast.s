0000000000001240 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%rax
    1243:	mov    0x8(%rdx),%r9
    1247:	mov    %r9,%r8
    124a:	sub    %rax,%r8
    124d:	mov    (%rdi),%rcx
    1250:	mov    0x8(%rdi),%rdx
    1254:	sub    %rcx,%rdx
    1257:	cmp    %r8,%rdx
    125a:	jb     1435 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1f5>
    1260:	cmp    %rax,%r9
    1263:	je     1434 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1f4>
    1269:	sar    $0x2,%r8
    126d:	cmp    $0x1,%r8
    1271:	mov    %r8,%rdx
    1274:	adc    $0x0,%rdx
    1278:	cmp    $0x8,%r8
    127c:	jae    1288 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x48>
    127e:	xor    %r10d,%r10d
    1281:	xor    %edi,%edi
    1283:	jmp    137b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x13b>
    1288:	mov    %rdx,%rdi
    128b:	and    $0xfffffffffffffff8,%rdi
    128f:	pxor   %xmm1,%xmm1
    1293:	xor    %r10d,%r10d
    1296:	movdqa 0xd72(%rip),%xmm0        # 2010 <_IO_stdin_used+0x10>
    129e:	pxor   %xmm2,%xmm2
    12a2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	movdqu (%rax,%r10,4),%xmm3
    12b6:	movdqu 0x10(%rax,%r10,4),%xmm4
    12bd:	movdqa %xmm1,%xmm5
    12c1:	pxor   %xmm0,%xmm5
    12c5:	movdqa %xmm3,%xmm6
    12c9:	pxor   %xmm0,%xmm6
    12cd:	pcmpgtd %xmm5,%xmm6
    12d1:	pand   %xmm6,%xmm3
    12d5:	pandn  %xmm1,%xmm6
    12d9:	movdqa %xmm6,%xmm1
    12dd:	por    %xmm3,%xmm1
    12e1:	movdqa %xmm2,%xmm3
    12e5:	pxor   %xmm0,%xmm3
    12e9:	movdqa %xmm4,%xmm5
    12ed:	pxor   %xmm0,%xmm5
    12f1:	pcmpgtd %xmm3,%xmm5
    12f5:	pand   %xmm5,%xmm4
    12f9:	pandn  %xmm2,%xmm5
    12fd:	movdqa %xmm5,%xmm2
    1301:	por    %xmm4,%xmm2
    1305:	add    $0x8,%r10
    1309:	cmp    %r10,%rdi
    130c:	jne    12b0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x70>
    130e:	movdqa %xmm2,%xmm3
    1312:	pxor   %xmm0,%xmm3
    1316:	movdqa %xmm1,%xmm4
    131a:	pxor   %xmm0,%xmm4
    131e:	pcmpgtd %xmm3,%xmm4
    1322:	pand   %xmm4,%xmm1
    1326:	pandn  %xmm2,%xmm4
    132a:	por    %xmm1,%xmm4
    132e:	pshufd $0xee,%xmm4,%xmm1
    1333:	movdqa %xmm4,%xmm2
    1337:	pxor   %xmm0,%xmm2
    133b:	movdqa %xmm1,%xmm3
    133f:	pxor   %xmm0,%xmm3
    1343:	pcmpgtd %xmm3,%xmm2
    1347:	pand   %xmm2,%xmm4
    134b:	pandn  %xmm1,%xmm2
    134f:	por    %xmm4,%xmm2
    1353:	pshufd $0x55,%xmm2,%xmm1
    1358:	movdqa %xmm2,%xmm3
    135c:	pxor   %xmm0,%xmm3
    1360:	pxor   %xmm1,%xmm0
    1364:	pcmpgtd %xmm0,%xmm3
    1368:	pand   %xmm3,%xmm2
    136c:	pandn  %xmm1,%xmm3
    1370:	por    %xmm2,%xmm3
    1374:	movd   %xmm3,%r10d
    1379:	jmp    1389 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x149>
    137b:	mov    (%rax,%rdi,4),%r11d
    137f:	cmp    %r10d,%r11d
    1382:	cmova  %r11d,%r10d
    1386:	inc    %rdi
    1389:	cmp    %rdi,%rdx
    138c:	jne    137b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x13b>
    138e:	cmp    %rax,%r9
    1391:	je     1434 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1f4>
    1397:	mov    (%rsi),%rdi
    139a:	mov    %r10d,%r9d
    139d:	mov    0x8(%rsi),%rsi
    13a1:	sub    %rdi,%rsi
    13a4:	sar    $0x2,%rsi
    13a8:	cmp    %r9,%rsi
    13ab:	jbe    1435 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1f5>
    13b1:	mov    %edx,%esi
    13b3:	and    $0x3,%esi
    13b6:	cmp    $0x4,%r8
    13ba:	jae    13c1 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    13bc:	xor    %r8d,%r8d
    13bf:	jmp    140f <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1cf>
    13c1:	and    $0xfffffffffffffffc,%rdx
    13c5:	xor    %r8d,%r8d
    13c8:	nopl   0x0(%rax,%rax,1)
    13d0:	mov    (%rax,%r8,4),%r9d
    13d4:	mov    (%rdi,%r9,4),%r9d
    13d8:	mov    %r9d,(%rcx,%r8,4)
    13dc:	mov    0x4(%rax,%r8,4),%r9d
    13e1:	mov    (%rdi,%r9,4),%r9d
    13e5:	mov    %r9d,0x4(%rcx,%r8,4)
    13ea:	mov    0x8(%rax,%r8,4),%r9d
    13ef:	mov    (%rdi,%r9,4),%r9d
    13f3:	mov    %r9d,0x8(%rcx,%r8,4)
    13f8:	mov    0xc(%rax,%r8,4),%r9d
    13fd:	mov    (%rdi,%r9,4),%r9d
    1401:	mov    %r9d,0xc(%rcx,%r8,4)
    1406:	add    $0x4,%r8
    140a:	cmp    %r8,%rdx
    140d:	jne    13d0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x190>
    140f:	test   %rsi,%rsi
    1412:	je     1434 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1f4>
    1414:	lea    (%rcx,%r8,4),%rcx
    1418:	lea    (%rax,%r8,4),%rax
    141c:	xor    %edx,%edx
    141e:	xchg   %ax,%ax
    1420:	mov    (%rax,%rdx,4),%r8d
    1424:	mov    (%rdi,%r8,4),%r8d
    1428:	mov    %r8d,(%rcx,%rdx,4)
    142c:	inc    %rdx
    142f:	cmp    %rdx,%rsi
    1432:	jne    1420 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1e0>
    1434:	ret
    1435:	ud2
    1437:	nopw   0x0(%rax,%rax,1)
