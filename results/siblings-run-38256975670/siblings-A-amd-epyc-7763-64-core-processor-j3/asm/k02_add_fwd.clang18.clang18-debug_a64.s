0000000000001280 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	push   %rax
    1281:	mov    (%rsi),%r8
    1284:	mov    0x8(%rsi),%rax
    1288:	sub    %r8,%rax
    128b:	je     139e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11e>
    1291:	sar    $0x2,%rax
    1295:	mov    (%rdx),%rsi
    1298:	mov    0x8(%rdx),%rcx
    129c:	sub    %rsi,%rcx
    129f:	sar    $0x2,%rcx
    12a3:	mov    (%rdi),%r9
    12a6:	mov    0x8(%rdi),%rdx
    12aa:	sub    %r9,%rdx
    12ad:	sar    $0x2,%rdx
    12b1:	cmp    $0x1,%rax
    12b5:	adc    $0x0,%rax
    12b9:	lea    -0x1(%rax),%r10
    12bd:	cmp    %rdx,%r10
    12c0:	cmovae %rdx,%r10
    12c4:	cmp    %rcx,%r10
    12c7:	cmovae %rcx,%r10
    12cb:	cmp    $0x7,%r10
    12cf:	ja     12d8 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x58>
    12d1:	xor    %edi,%edi
    12d3:	jmp    135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12d8:	mov    %r9,%r11
    12db:	sub    %r8,%r11
    12de:	xor    %edi,%edi
    12e0:	cmp    $0x10,%r11
    12e4:	jb     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12ea:	mov    %r9,%r11
    12ed:	sub    %rsi,%r11
    12f0:	cmp    $0x10,%r11
    12f4:	jb     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12f6:	inc    %r10
    12f9:	mov    %r10d,%edi
    12fc:	and    $0x3,%edi
    12ff:	mov    $0x4,%r11d
    1305:	cmovne %rdi,%r11
    1309:	mov    %r10,%rdi
    130c:	sub    %r11,%rdi
    130f:	xor    %r10d,%r10d
    1312:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1321:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1330:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133f:	nop
    1340:	movdqu (%r8,%r10,4),%xmm0
    1346:	movdqu (%rsi,%r10,4),%xmm1
    134c:	paddd  %xmm0,%xmm1
    1350:	movdqu %xmm1,(%r9,%r10,4)
    1356:	add    $0x4,%r10
    135a:	cmp    %r10,%rdi
    135d:	jne    1340 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    135f:	sub    %rdi,%rdx
    1362:	sub    %rdi,%rcx
    1365:	sub    %rdi,%rax
    1368:	lea    (%r8,%rdi,4),%r8
    136c:	lea    (%rsi,%rdi,4),%rsi
    1370:	lea    (%r9,%rdi,4),%rdi
    1374:	xor    %r9d,%r9d
    1377:	nopw   0x0(%rax,%rax,1)
    1380:	cmp    %r9,%rcx
    1383:	je     13a0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x120>
    1385:	cmp    %r9,%rdx
    1388:	je     13b5 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x135>
    138a:	mov    (%rsi,%r9,4),%r10d
    138e:	add    (%r8,%r9,4),%r10d
    1392:	mov    %r10d,(%rdi,%r9,4)
    1396:	inc    %r9
    1399:	cmp    %r9,%rax
    139c:	jne    1380 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    139e:	pop    %rax
    139f:	ret
    13a0:	lea    0xc89(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    13a7:	lea    0xc85(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    13ae:	xor    %eax,%eax
    13b0:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    13b5:	lea    0xc74(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    13bc:	lea    0xce1(%rip),%rsi        # 20a4 <_IO_stdin_used+0xa4>
    13c3:	xor    %eax,%eax
    13c5:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    13ca:	mov    %rax,%rdi
    13cd:	call   1780 <__clang_call_terminate>
    13d2:	mov    %rax,%rdi
    13d5:	call   1780 <__clang_call_terminate>
    13da:	nopw   0x0(%rax,%rax,1)
