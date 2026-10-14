0000000000001250 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1250:	push   %rbp
    1251:	push   %r15
    1253:	push   %r14
    1255:	push   %r13
    1257:	push   %r12
    1259:	push   %rbx
    125a:	sub    $0x28,%rsp
    125e:	test   %rcx,%rcx
    1261:	je     1344 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xf4>
    1267:	mov    (%rsi),%rax
    126a:	mov    0x8(%rsi),%rsi
    126e:	mov    %rax,0x20(%rsp)
    1273:	sub    %rax,%rsi
    1276:	sar    $0x2,%rsi
    127a:	lea    0x0(,%rcx,4),%rax
    1282:	mov    %rax,0x8(%rsp)
    1287:	xor    %r9d,%r9d
    128a:	xor    %r10d,%r10d
    128d:	xor    %ebx,%ebx
    128f:	mov    %rdx,0x10(%rsp)
    1294:	mov    %rbx,0x18(%rsp)
    1299:	imul   %rcx,%rbx
    129d:	mov    (%rdx),%r14
    12a0:	mov    0x8(%rdx),%r15
    12a4:	sub    %r14,%r15
    12a7:	sar    $0x2,%r15
    12ab:	xor    %r12d,%r12d
    12ae:	xor    %r13d,%r13d
    12b1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	lea    (%rbx,%r13,1),%rax
    12c4:	cmp    %rax,%rsi
    12c7:	jbe    137d <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x12d>
    12cd:	mov    0x20(%rsp),%rdx
    12d2:	mov    (%rdx,%rax,4),%ebp
    12d5:	mov    (%rdi),%r11
    12d8:	mov    0x8(%rdi),%rdx
    12dc:	sub    %r11,%rdx
    12df:	sar    $0x2,%rdx
    12e3:	add    %r10,%r11
    12e6:	xor    %eax,%eax
    12e8:	nopl   0x0(%rax,%rax,1)
    12f0:	lea    (%r12,%rax,1),%r8
    12f4:	cmp    %r8,%r15
    12f7:	jbe    1353 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x103>
    12f9:	lea    (%r9,%rax,1),%r8
    12fd:	cmp    %r8,%rdx
    1300:	jbe    1368 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x118>
    1302:	mov    (%r14,%rax,4),%r8d
    1306:	imul   %ebp,%r8d
    130a:	add    %r8d,(%r11,%rax,4)
    130e:	inc    %rax
    1311:	cmp    %rax,%rcx
    1314:	jne    12f0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xa0>
    1316:	inc    %r13
    1319:	add    0x8(%rsp),%r14
    131e:	add    %rcx,%r12
    1321:	cmp    %rcx,%r13
    1324:	jne    12c0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    1326:	mov    0x18(%rsp),%rbx
    132b:	inc    %rbx
    132e:	add    0x8(%rsp),%r10
    1333:	add    %rcx,%r9
    1336:	cmp    %rcx,%rbx
    1339:	mov    0x10(%rsp),%rdx
    133e:	jne    1294 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x44>
    1344:	add    $0x28,%rsp
    1348:	pop    %rbx
    1349:	pop    %r12
    134b:	pop    %r13
    134d:	pop    %r14
    134f:	pop    %r15
    1351:	pop    %rbp
    1352:	ret
    1353:	lea    0xce6(%rip),%rdi        # 2040 <_IO_stdin_used+0x40>
    135a:	lea    0xce2(%rip),%rsi        # 2043 <_IO_stdin_used+0x43>
    1361:	xor    %eax,%eax
    1363:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    1368:	lea    0xcd1(%rip),%rdi        # 2040 <_IO_stdin_used+0x40>
    136f:	lea    0xd3e(%rip),%rsi        # 20b4 <_IO_stdin_used+0xb4>
    1376:	xor    %eax,%eax
    1378:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    137d:	lea    0xcbc(%rip),%rdi        # 2040 <_IO_stdin_used+0x40>
    1384:	lea    0xcb8(%rip),%rsi        # 2043 <_IO_stdin_used+0x43>
    138b:	xor    %eax,%eax
    138d:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    1392:	mov    %rax,%rdi
    1395:	call   1870 <__clang_call_terminate>
    139a:	mov    %rax,%rdi
    139d:	call   1870 <__clang_call_terminate>
    13a2:	mov    %rax,%rdi
    13a5:	call   1870 <__clang_call_terminate>
    13aa:	nopw   0x0(%rax,%rax,1)
