0000000000001250 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	push   %rbx
    1251:	mov    (%rsi),%rax
    1254:	mov    0x8(%rsi),%rcx
    1258:	sub    %rax,%rcx
    125b:	sar    $0x2,%rcx
    125f:	cmp    $0x3,%rcx
    1263:	jb     1385 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x135>
    1269:	mov    (%rdi),%rdx
    126c:	mov    0x8(%rdi),%rsi
    1270:	sub    %rdx,%rsi
    1273:	sar    $0x2,%rsi
    1277:	cmp    $0x1,%rsi
    127b:	adc    $0x0,%rsi
    127f:	lea    -0x1(%rsi),%r11
    1283:	lea    -0x3(%rcx),%r10
    1287:	cmp    %r10,%r11
    128a:	mov    %r10,%r9
    128d:	cmovb  %r11,%r9
    1291:	mov    $0x1,%edi
    1296:	mov    $0x2,%r8d
    129c:	cmp    $0xb,%r9
    12a0:	jbe    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    12a6:	lea    0x4(%rdx),%rbx
    12aa:	cmp    %r10,%r11
    12ad:	cmovb  %r11,%r10
    12b1:	lea    (%rax,%r10,4),%r11
    12b5:	add    $0xc,%r11
    12b9:	cmp    %r11,%rbx
    12bc:	jae    12cf <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7f>
    12be:	lea    (%rdx,%r10,4),%r10
    12c2:	add    $0x8,%r10
    12c6:	cmp    %r10,%rax
    12c9:	jb     1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    12cf:	inc    %r9
    12d2:	mov    %r9d,%edi
    12d5:	and    $0x7,%edi
    12d8:	mov    $0x8,%r8d
    12de:	cmovne %rdi,%r8
    12e2:	mov    %r9,%r10
    12e5:	sub    %r8,%r10
    12e8:	neg    %r8
    12eb:	add    %r9,%r8
    12ee:	add    $0x2,%r8
    12f2:	lea    0x1(%r10),%rdi
    12f6:	xor    %r9d,%r9d
    12f9:	nopl   0x0(%rax)
    1300:	movdqu (%rax,%r9,4),%xmm0
    1306:	movdqu 0x4(%rax,%r9,4),%xmm1
    130d:	paddd  %xmm0,%xmm1
    1311:	movdqu 0x8(%rax,%r9,4),%xmm0
    1318:	paddd  %xmm1,%xmm0
    131c:	movdqu 0x10(%rax,%r9,4),%xmm1
    1323:	movdqu 0x14(%rax,%r9,4),%xmm2
    132a:	paddd  %xmm1,%xmm2
    132e:	movdqu 0x18(%rax,%r9,4),%xmm1
    1335:	paddd  %xmm2,%xmm1
    1339:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1340:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1347:	add    $0x8,%r9
    134b:	cmp    %r9,%r10
    134e:	jne    1300 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>
    1350:	inc    %rsi
    1353:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1360:	cmp    %r8,%rsi
    1363:	je     1387 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1365:	mov    %r8,%r9
    1368:	mov    (%rax,%rdi,4),%r8d
    136c:	add    -0x4(%rax,%rdi,4),%r8d
    1371:	add    (%rax,%r9,4),%r8d
    1375:	mov    %r8d,(%rdx,%rdi,4)
    1379:	lea    0x1(%r9),%r8
    137d:	mov    %r9,%rdi
    1380:	cmp    %r8,%rcx
    1383:	jne    1360 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    1385:	pop    %rbx
    1386:	ret
    1387:	lea    0xca2(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    138e:	lea    0xc9e(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    1395:	xor    %eax,%eax
    1397:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    139c:	mov    %rax,%rdi
    139f:	call   1680 <__clang_call_terminate>
    13a4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
