0000000000001280 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1280:	push   %rbp
    1281:	push   %r15
    1283:	push   %r14
    1285:	push   %r13
    1287:	push   %r12
    1289:	push   %rbx
    128a:	sub    $0x28,%rsp
    128e:	test   %rcx,%rcx
    1291:	je     1394 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x114>
    1297:	mov    (%rsi),%rax
    129a:	mov    0x8(%rsi),%rsi
    129e:	mov    %rax,0x20(%rsp)
    12a3:	sub    %rax,%rsi
    12a6:	sar    $0x2,%rsi
    12aa:	lea    0x0(,%rcx,4),%rax
    12b2:	mov    %rax,0x8(%rsp)
    12b7:	xor    %r9d,%r9d
    12ba:	xor    %r10d,%r10d
    12bd:	xor    %ebx,%ebx
    12bf:	mov    %rdx,0x10(%rsp)
    12c4:	mov    %rbx,0x18(%rsp)
    12c9:	imul   %rcx,%rbx
    12cd:	mov    (%rdx),%r14
    12d0:	mov    0x8(%rdx),%r15
    12d4:	sub    %r14,%r15
    12d7:	sar    $0x2,%r15
    12db:	xor    %r12d,%r12d
    12de:	xor    %r13d,%r13d
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	lea    (%rbx,%r13,1),%rax
    1304:	cmp    %rax,%rsi
    1307:	jbe    13cd <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x14d>
    130d:	mov    0x20(%rsp),%rdx
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
    1347:	jbe    13a3 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x123>
    1349:	lea    (%r9,%rax,1),%r8
    134d:	cmp    %r8,%rdx
    1350:	jbe    13b8 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x138>
    1352:	mov    (%r14,%rax,4),%r8d
    1356:	imul   %ebp,%r8d
    135a:	add    %r8d,(%r11,%rax,4)
    135e:	inc    %rax
    1361:	cmp    %rax,%rcx
    1364:	jne    1340 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xc0>
    1366:	inc    %r13
    1369:	add    0x8(%rsp),%r14
    136e:	add    %rcx,%r12
    1371:	cmp    %rcx,%r13
    1374:	jne    1300 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x80>
    1376:	mov    0x18(%rsp),%rbx
    137b:	inc    %rbx
    137e:	add    0x8(%rsp),%r10
    1383:	add    %rcx,%r9
    1386:	cmp    %rcx,%rbx
    1389:	mov    0x10(%rsp),%rdx
    138e:	jne    12c4 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x44>
    1394:	add    $0x28,%rsp
    1398:	pop    %rbx
    1399:	pop    %r12
    139b:	pop    %r13
    139d:	pop    %r14
    139f:	pop    %r15
    13a1:	pop    %rbp
    13a2:	ret
    13a3:	lea    0xc96(%rip),%rdi        # 2040 <_IO_stdin_used+0x40>
    13aa:	lea    0xc92(%rip),%rsi        # 2043 <_IO_stdin_used+0x43>
    13b1:	xor    %eax,%eax
    13b3:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    13b8:	lea    0xc81(%rip),%rdi        # 2040 <_IO_stdin_used+0x40>
    13bf:	lea    0xcee(%rip),%rsi        # 20b4 <_IO_stdin_used+0xb4>
    13c6:	xor    %eax,%eax
    13c8:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    13cd:	lea    0xc6c(%rip),%rdi        # 2040 <_IO_stdin_used+0x40>
    13d4:	lea    0xc68(%rip),%rsi        # 2043 <_IO_stdin_used+0x43>
    13db:	xor    %eax,%eax
    13dd:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    13e2:	mov    %rax,%rdi
    13e5:	call   1940 <__clang_call_terminate>
    13ea:	mov    %rax,%rdi
    13ed:	call   1940 <__clang_call_terminate>
    13f2:	mov    %rax,%rdi
    13f5:	call   1940 <__clang_call_terminate>
    13fa:	nopw   0x0(%rax,%rax,1)
