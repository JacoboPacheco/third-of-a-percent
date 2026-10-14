0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	mov    %rdx,%r8
    128d:	mov    %rcx,%rax
    1290:	mul    %rcx
    1293:	jo     13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    1299:	mov    (%rsi),%rdx
    129c:	mov    0x8(%rsi),%rsi
    12a0:	sub    %rdx,%rsi
    12a3:	sar    $0x2,%rsi
    12a7:	cmp    %rax,%rsi
    12aa:	jb     13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    12b0:	mov    (%r8),%r12
    12b3:	mov    0x8(%r8),%r8
    12b7:	sub    %r12,%r8
    12ba:	sar    $0x2,%r8
    12be:	cmp    %rax,%r8
    12c1:	jb     13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    12c7:	mov    (%rdi),%r10
    12ca:	mov    0x8(%rdi),%rdi
    12ce:	sub    %r10,%rdi
    12d1:	sar    $0x2,%rdi
    12d5:	cmp    %rax,%rdi
    12d8:	jb     13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    12de:	test   %rcx,%rcx
    12e1:	je     13cf <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x14f>
    12e7:	lea    0x0(,%rcx,4),%rax
    12ef:	xor    %r11d,%r11d
    12f2:	xor    %r14d,%r14d
    12f5:	mov    %r12,-0x10(%rsp)
    12fa:	mov    %r14,-0x8(%rsp)
    12ff:	imul   %rcx,%r14
    1303:	xor    %r15d,%r15d
    1306:	xor    %r13d,%r13d
    1309:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1318:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1327:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1336:	cs nopw 0x0(%rax,%rax,1)
    1340:	lea    (%r14,%r13,1),%r9
    1344:	cmp    %r9,%rsi
    1347:	jbe    13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    134d:	mov    (%rdx,%r9,4),%ebp
    1351:	xor    %r9d,%r9d
    1354:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1363:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1372:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	lea    (%r15,%r9,1),%rbx
    1384:	cmp    %rbx,%r8
    1387:	jbe    13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    1389:	lea    (%r11,%r9,1),%rbx
    138d:	cmp    %rbx,%rdi
    1390:	jbe    13da <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x15a>
    1392:	mov    (%r12,%r9,4),%ebx
    1396:	imul   %ebp,%ebx
    1399:	add    %ebx,(%r10,%r9,4)
    139d:	inc    %r9
    13a0:	cmp    %r9,%rcx
    13a3:	jne    1380 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x100>
    13a5:	inc    %r13
    13a8:	add    %rax,%r12
    13ab:	add    %rcx,%r15
    13ae:	cmp    %rcx,%r13
    13b1:	jne    1340 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    13b3:	mov    -0x8(%rsp),%r14
    13b8:	inc    %r14
    13bb:	add    %rax,%r10
    13be:	add    %rcx,%r11
    13c1:	cmp    %rcx,%r14
    13c4:	mov    -0x10(%rsp),%r12
    13c9:	jne    12fa <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x7a>
    13cf:	pop    %rbx
    13d0:	pop    %r12
    13d2:	pop    %r13
    13d4:	pop    %r14
    13d6:	pop    %r15
    13d8:	pop    %rbp
    13d9:	ret
    13da:	ud2
    13dc:	nopl   0x0(%rax)
