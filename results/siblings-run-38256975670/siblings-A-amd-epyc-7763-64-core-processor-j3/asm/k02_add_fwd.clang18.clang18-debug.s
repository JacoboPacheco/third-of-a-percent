0000000000001250 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1250:	push   %rax
    1251:	mov    (%rsi),%r8
    1254:	mov    0x8(%rsi),%rax
    1258:	sub    %r8,%rax
    125b:	je     133e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1261:	sar    $0x2,%rax
    1265:	mov    (%rdx),%rsi
    1268:	mov    0x8(%rdx),%rcx
    126c:	sub    %rsi,%rcx
    126f:	sar    $0x2,%rcx
    1273:	mov    (%rdi),%r9
    1276:	mov    0x8(%rdi),%rdx
    127a:	sub    %r9,%rdx
    127d:	sar    $0x2,%rdx
    1281:	cmp    $0x1,%rax
    1285:	adc    $0x0,%rax
    1289:	lea    -0x1(%rax),%r10
    128d:	cmp    %rdx,%r10
    1290:	cmovae %rdx,%r10
    1294:	cmp    %rcx,%r10
    1297:	cmovae %rcx,%r10
    129b:	cmp    $0x7,%r10
    129f:	ja     12a5 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x55>
    12a1:	xor    %edi,%edi
    12a3:	jmp    12ff <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12a5:	mov    %r9,%r11
    12a8:	sub    %r8,%r11
    12ab:	xor    %edi,%edi
    12ad:	cmp    $0x10,%r11
    12b1:	jb     12ff <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12b3:	mov    %r9,%r11
    12b6:	sub    %rsi,%r11
    12b9:	cmp    $0x10,%r11
    12bd:	jb     12ff <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12bf:	inc    %r10
    12c2:	mov    %r10d,%edi
    12c5:	and    $0x3,%edi
    12c8:	mov    $0x4,%r11d
    12ce:	cmovne %rdi,%r11
    12d2:	mov    %r10,%rdi
    12d5:	sub    %r11,%rdi
    12d8:	xor    %r10d,%r10d
    12db:	nopl   0x0(%rax,%rax,1)
    12e0:	movdqu (%r8,%r10,4),%xmm0
    12e6:	movdqu (%rsi,%r10,4),%xmm1
    12ec:	paddd  %xmm0,%xmm1
    12f0:	movdqu %xmm1,(%r9,%r10,4)
    12f6:	add    $0x4,%r10
    12fa:	cmp    %r10,%rdi
    12fd:	jne    12e0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12ff:	sub    %rdi,%rdx
    1302:	sub    %rdi,%rcx
    1305:	sub    %rdi,%rax
    1308:	lea    (%r8,%rdi,4),%r8
    130c:	lea    (%rsi,%rdi,4),%rsi
    1310:	lea    (%r9,%rdi,4),%rdi
    1314:	xor    %r9d,%r9d
    1317:	nopw   0x0(%rax,%rax,1)
    1320:	cmp    %r9,%rcx
    1323:	je     1340 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xf0>
    1325:	cmp    %r9,%rdx
    1328:	je     1355 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x105>
    132a:	mov    (%rsi,%r9,4),%r10d
    132e:	add    (%r8,%r9,4),%r10d
    1332:	mov    %r10d,(%rdi,%r9,4)
    1336:	inc    %r9
    1339:	cmp    %r9,%rax
    133c:	jne    1320 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    133e:	pop    %rax
    133f:	ret
    1340:	lea    0xce9(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    1347:	lea    0xce5(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    134e:	xor    %eax,%eax
    1350:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    1355:	lea    0xcd4(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    135c:	lea    0xd41(%rip),%rsi        # 20a4 <_IO_stdin_used+0xa4>
    1363:	xor    %eax,%eax
    1365:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    136a:	mov    %rax,%rdi
    136d:	call   16f0 <__clang_call_terminate>
    1372:	mov    %rax,%rdi
    1375:	call   16f0 <__clang_call_terminate>
    137a:	nopw   0x0(%rax,%rax,1)
