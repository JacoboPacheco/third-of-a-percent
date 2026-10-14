0000000000001280 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	push   %rbx
    1281:	mov    (%rsi),%rax
    1284:	mov    0x8(%rsi),%rcx
    1288:	sub    %rax,%rcx
    128b:	sar    $0x2,%rcx
    128f:	cmp    $0x3,%rcx
    1293:	jb     13e5 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x165>
    1299:	mov    (%rdi),%rdx
    129c:	mov    0x8(%rdi),%rsi
    12a0:	sub    %rdx,%rsi
    12a3:	sar    $0x2,%rsi
    12a7:	cmp    $0x1,%rsi
    12ab:	adc    $0x0,%rsi
    12af:	lea    -0x1(%rsi),%r11
    12b3:	lea    -0x3(%rcx),%r10
    12b7:	cmp    %r10,%r11
    12ba:	mov    %r10,%r9
    12bd:	cmovb  %r11,%r9
    12c1:	mov    $0x1,%edi
    12c6:	mov    $0x2,%r8d
    12cc:	cmp    $0xb,%r9
    12d0:	jbe    1390 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    12d6:	lea    0x4(%rdx),%rbx
    12da:	cmp    %r10,%r11
    12dd:	cmovb  %r11,%r10
    12e1:	lea    (%rax,%r10,4),%r11
    12e5:	add    $0xc,%r11
    12e9:	cmp    %r11,%rbx
    12ec:	jae    12ff <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7f>
    12ee:	lea    (%rdx,%r10,4),%r10
    12f2:	add    $0x8,%r10
    12f6:	cmp    %r10,%rax
    12f9:	jb     1390 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    12ff:	inc    %r9
    1302:	mov    %r9d,%edi
    1305:	and    $0x7,%edi
    1308:	mov    $0x8,%r8d
    130e:	cmovne %rdi,%r8
    1312:	mov    %r9,%r10
    1315:	sub    %r8,%r10
    1318:	neg    %r8
    131b:	add    %r9,%r8
    131e:	add    $0x2,%r8
    1322:	lea    0x1(%r10),%rdi
    1326:	xor    %r9d,%r9d
    1329:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1338:	nopl   0x0(%rax,%rax,1)
    1340:	movdqu (%rax,%r9,4),%xmm0
    1346:	movdqu 0x4(%rax,%r9,4),%xmm1
    134d:	paddd  %xmm0,%xmm1
    1351:	movdqu 0x8(%rax,%r9,4),%xmm0
    1358:	paddd  %xmm1,%xmm0
    135c:	movdqu 0x10(%rax,%r9,4),%xmm1
    1363:	movdqu 0x14(%rax,%r9,4),%xmm2
    136a:	paddd  %xmm1,%xmm2
    136e:	movdqu 0x18(%rax,%r9,4),%xmm1
    1375:	paddd  %xmm2,%xmm1
    1379:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1380:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1387:	add    $0x8,%r9
    138b:	cmp    %r9,%r10
    138e:	jne    1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1390:	inc    %rsi
    1393:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13a2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13b1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13c0:	cmp    %r8,%rsi
    13c3:	je     13e7 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x167>
    13c5:	mov    %r8,%r9
    13c8:	mov    (%rax,%rdi,4),%r8d
    13cc:	add    -0x4(%rax,%rdi,4),%r8d
    13d1:	add    (%rax,%r9,4),%r8d
    13d5:	mov    %r8d,(%rdx,%rdi,4)
    13d9:	lea    0x1(%r9),%r8
    13dd:	mov    %r9,%rdi
    13e0:	cmp    %r8,%rcx
    13e3:	jne    13c0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13e5:	pop    %rbx
    13e6:	ret
    13e7:	lea    0xc42(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    13ee:	lea    0xc3e(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    13f5:	xor    %eax,%eax
    13f7:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    13fc:	mov    %rax,%rdi
    13ff:	call   1720 <__clang_call_terminate>
    1404:	data16 data16 cs nopw 0x0(%rax,%rax,1)
