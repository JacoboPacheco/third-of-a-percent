0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%r8
    1243:	mov    0x8(%rsi),%rax
    1247:	sub    %r8,%rax
    124a:	je     132e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1250:	sar    $0x2,%rax
    1254:	mov    (%rdx),%rsi
    1257:	mov    0x8(%rdx),%rcx
    125b:	sub    %rsi,%rcx
    125e:	sar    $0x2,%rcx
    1262:	mov    (%rdi),%r9
    1265:	mov    0x8(%rdi),%rdx
    1269:	sub    %r9,%rdx
    126c:	sar    $0x2,%rdx
    1270:	cmp    $0x1,%rax
    1274:	adc    $0x0,%rax
    1278:	lea    -0x1(%rax),%r10
    127c:	cmp    %rdx,%r10
    127f:	cmovae %rdx,%r10
    1283:	cmp    %rcx,%r10
    1286:	cmovae %rcx,%r10
    128a:	cmp    $0x7,%r10
    128e:	ja     1294 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    1290:	xor    %edi,%edi
    1292:	jmp    12ef <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1294:	mov    %r9,%r11
    1297:	sub    %r8,%r11
    129a:	xor    %edi,%edi
    129c:	cmp    $0x10,%r11
    12a0:	jb     12ef <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12a2:	mov    %r9,%r11
    12a5:	sub    %rsi,%r11
    12a8:	cmp    $0x10,%r11
    12ac:	jb     12ef <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12ae:	inc    %r10
    12b1:	mov    %r10d,%edi
    12b4:	and    $0x3,%edi
    12b7:	mov    $0x4,%r11d
    12bd:	cmovne %rdi,%r11
    12c1:	mov    %r10,%rdi
    12c4:	sub    %r11,%rdi
    12c7:	xor    %r10d,%r10d
    12ca:	nopw   0x0(%rax,%rax,1)
    12d0:	movdqu (%r8,%r10,4),%xmm0
    12d6:	movdqu (%rsi,%r10,4),%xmm1
    12dc:	paddd  %xmm0,%xmm1
    12e0:	movdqu %xmm1,(%r9,%r10,4)
    12e6:	add    $0x4,%r10
    12ea:	cmp    %r10,%rdi
    12ed:	jne    12d0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12ef:	sub    %rdi,%rdx
    12f2:	sub    %rdi,%rcx
    12f5:	sub    %rdi,%rax
    12f8:	lea    (%r8,%rdi,4),%r8
    12fc:	lea    (%rsi,%rdi,4),%rsi
    1300:	lea    (%r9,%rdi,4),%rdi
    1304:	xor    %r9d,%r9d
    1307:	nopw   0x0(%rax,%rax,1)
    1310:	cmp    %r9,%rcx
    1313:	je     132f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    1315:	cmp    %r9,%rdx
    1318:	je     132f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    131a:	mov    (%rsi,%r9,4),%r10d
    131e:	add    (%r8,%r9,4),%r10d
    1322:	mov    %r10d,(%rdi,%r9,4)
    1326:	inc    %r9
    1329:	cmp    %r9,%rax
    132c:	jne    1310 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    132e:	ret
    132f:	ud2
    1331:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
