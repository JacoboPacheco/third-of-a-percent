0000000000001280 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	test   %rcx,%rcx
    128d:	je     1394 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x114>
    1293:	mov    (%rsi),%rax
    1296:	mov    0x8(%rsi),%rsi
    129a:	mov    %rax,-0x8(%rsp)
    129f:	sub    %rax,%rsi
    12a2:	sar    $0x2,%rsi
    12a6:	lea    0x0(,%rcx,4),%rax
    12ae:	mov    %rax,-0x20(%rsp)
    12b3:	xor    %r9d,%r9d
    12b6:	xor    %r10d,%r10d
    12b9:	xor    %ebx,%ebx
    12bb:	mov    %rdx,-0x18(%rsp)
    12c0:	mov    %rbx,-0x10(%rsp)
    12c5:	imul   %rcx,%rbx
    12c9:	mov    (%rdx),%r14
    12cc:	mov    0x8(%rdx),%r15
    12d0:	sub    %r14,%r15
    12d3:	sar    $0x2,%r15
    12d7:	xor    %r12d,%r12d
    12da:	xor    %r13d,%r13d
    12dd:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ec:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fb:	nopl   0x0(%rax,%rax,1)
    1300:	lea    (%rbx,%r13,1),%rax
    1304:	cmp    %rax,%rsi
    1307:	jbe    139f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x11f>
    130d:	mov    -0x8(%rsp),%rdx
    1312:	mov    (%rdx,%rax,4),%ebp
    1315:	mov    (%rdi),%r11
    1318:	mov    0x8(%rdi),%rdx
    131c:	sub    %r11,%rdx
    131f:	sar    $0x2,%rdx
    1323:	add    %r10,%r11
    1326:	xor    %eax,%eax
    1328:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1337:	nopw   0x0(%rax,%rax,1)
    1340:	lea    (%r12,%rax,1),%r8
    1344:	cmp    %r8,%r15
    1347:	jbe    139f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x11f>
    1349:	lea    (%r9,%rax,1),%r8
    134d:	cmp    %r8,%rdx
    1350:	jbe    139f <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x11f>
    1352:	mov    (%r14,%rax,4),%r8d
    1356:	imul   %ebp,%r8d
    135a:	add    %r8d,(%r11,%rax,4)
    135e:	inc    %rax
    1361:	cmp    %rax,%rcx
    1364:	jne    1340 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    1366:	inc    %r13
    1369:	add    -0x20(%rsp),%r14
    136e:	add    %rcx,%r12
    1371:	cmp    %rcx,%r13
    1374:	jne    1300 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1376:	mov    -0x10(%rsp),%rbx
    137b:	inc    %rbx
    137e:	add    -0x20(%rsp),%r10
    1383:	add    %rcx,%r9
    1386:	cmp    %rcx,%rbx
    1389:	mov    -0x18(%rsp),%rdx
    138e:	jne    12c0 <_Z15kern_m08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>
    1394:	pop    %rbx
    1395:	pop    %r12
    1397:	pop    %r13
    1399:	pop    %r14
    139b:	pop    %r15
    139d:	pop    %rbp
    139e:	ret
    139f:	ud2
    13a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
