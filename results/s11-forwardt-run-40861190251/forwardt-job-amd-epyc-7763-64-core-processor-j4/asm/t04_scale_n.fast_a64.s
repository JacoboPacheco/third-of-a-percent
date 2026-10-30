0000000000001240 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
    1240:	test   %rdx,%rdx
    1243:	je     131d <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xdd>
    1249:	mov    (%rsi),%rax
    124c:	mov    0x8(%rsi),%rcx
    1250:	sub    %rax,%rcx
    1253:	sar    $0x2,%rcx
    1257:	mov    (%rdi),%rsi
    125a:	mov    0x8(%rdi),%rdi
    125e:	sub    %rsi,%rdi
    1261:	sar    $0x2,%rdi
    1265:	lea    -0x1(%rdx),%r8
    1269:	cmp    %r8,%rdi
    126c:	cmovb  %rdi,%r8
    1270:	cmp    %rcx,%r8
    1273:	cmovae %rcx,%r8
    1277:	inc    %r8
    127a:	xor    %r9d,%r9d
    127d:	cmp    $0x5,%r8
    1281:	jb     1300 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc0>
    1287:	mov    %rsi,%r10
    128a:	sub    %rax,%r10
    128d:	cmp    $0xf,%r10
    1291:	jbe    1300 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc0>
    1293:	mov    %r8d,%r9d
    1296:	and    $0x3,%r9d
    129a:	mov    $0x4,%r10d
    12a0:	cmovne %r9,%r10
    12a4:	sub    %r10,%r8
    12a7:	xor    %r9d,%r9d
    12aa:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b9:	nopl   0x0(%rax)
    12c0:	movdqu (%rax,%r9,4),%xmm0
    12c6:	paddd  %xmm0,%xmm0
    12ca:	movdqu %xmm0,(%rsi,%r9,4)
    12d0:	add    $0x4,%r9
    12d4:	cmp    %r9,%r8
    12d7:	jne    12c0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>
    12d9:	mov    %r8,%r9
    12dc:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12eb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fa:	nopw   0x0(%rax,%rax,1)
    1300:	cmp    %r9,%rcx
    1303:	je     131e <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xde>
    1305:	cmp    %r9,%rdi
    1308:	je     131e <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xde>
    130a:	mov    (%rax,%r9,4),%r8d
    130e:	add    %r8d,%r8d
    1311:	mov    %r8d,(%rsi,%r9,4)
    1315:	inc    %r9
    1318:	cmp    %r9,%rdx
    131b:	jne    1300 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc0>
    131d:	ret
    131e:	ud2
