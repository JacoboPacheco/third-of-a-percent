0000000000001250 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1250:	mov    (%rsi),%r8
    1253:	mov    0x8(%rsi),%rax
    1257:	sub    %r8,%rax
    125a:	je     133e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1260:	sar    $0x2,%rax
    1264:	mov    (%rdx),%rsi
    1267:	mov    0x8(%rdx),%rcx
    126b:	sub    %rsi,%rcx
    126e:	sar    $0x2,%rcx
    1272:	mov    (%rdi),%r9
    1275:	mov    0x8(%rdi),%rdx
    1279:	sub    %r9,%rdx
    127c:	sar    $0x2,%rdx
    1280:	cmp    $0x1,%rax
    1284:	adc    $0x0,%rax
    1288:	lea    -0x1(%rax),%r10
    128c:	cmp    %rdx,%r10
    128f:	cmovae %rdx,%r10
    1293:	cmp    %rcx,%r10
    1296:	cmovae %rcx,%r10
    129a:	cmp    $0x7,%r10
    129e:	ja     12a4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    12a0:	xor    %edi,%edi
    12a2:	jmp    12ff <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12a4:	mov    %r9,%r11
    12a7:	sub    %r8,%r11
    12aa:	xor    %edi,%edi
    12ac:	cmp    $0x10,%r11
    12b0:	jb     12ff <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12b2:	mov    %r9,%r11
    12b5:	sub    %rsi,%r11
    12b8:	cmp    $0x10,%r11
    12bc:	jb     12ff <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12be:	inc    %r10
    12c1:	mov    %r10d,%edi
    12c4:	and    $0x3,%edi
    12c7:	mov    $0x4,%r11d
    12cd:	cmovne %rdi,%r11
    12d1:	mov    %r10,%rdi
    12d4:	sub    %r11,%rdi
    12d7:	xor    %r10d,%r10d
    12da:	nopw   0x0(%rax,%rax,1)
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
    1323:	je     133f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    1325:	cmp    %r9,%rdx
    1328:	je     133f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    132a:	mov    (%rsi,%r9,4),%r10d
    132e:	add    (%r8,%r9,4),%r10d
    1332:	mov    %r10d,(%rdi,%r9,4)
    1336:	inc    %r9
    1339:	cmp    %r9,%rax
    133c:	jne    1320 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    133e:	ret
    133f:	ud2
    1341:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
