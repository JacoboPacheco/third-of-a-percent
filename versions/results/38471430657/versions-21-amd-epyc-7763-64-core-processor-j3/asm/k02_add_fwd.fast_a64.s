0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%r8
    1243:	mov    0x8(%rsi),%rax
    1247:	sub    %r8,%rax
    124a:	je     139e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x15e>
    1250:	sar    $0x2,%rax
    1254:	mov    (%rdx),%rsi
    1257:	mov    0x8(%rdx),%rcx
    125b:	sub    %rsi,%rcx
    125e:	sar    $0x2,%rcx
    1262:	mov    (%rdi),%r9
    1265:	mov    0x8(%rdi),%rdx
    1269:	sub    %r9,%rdx
    126c:	sar    $0x2,%rdx
    1270:	lea    -0x1(%rax),%rdi
    1274:	cmp    %rdx,%rdi
    1277:	cmovae %rdx,%rdi
    127b:	cmp    %rcx,%rdi
    127e:	cmovae %rcx,%rdi
    1282:	inc    %rdi
    1285:	cmp    $0x8,%rdi
    1289:	jbe    12ac <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x6c>
    128b:	mov    %r9,%r10
    128e:	sub    %r8,%r10
    1291:	cmp    $0x20,%r10
    1295:	setb   %r10b
    1299:	mov    %r9,%r11
    129c:	sub    %rsi,%r11
    129f:	cmp    $0x20,%r11
    12a3:	setb   %r11b
    12a7:	or     %r10b,%r11b
    12aa:	je     12b3 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x73>
    12ac:	xor    %edi,%edi
    12ae:	jmp    1338 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xf8>
    12b3:	mov    %edi,%r10d
    12b6:	and    $0x7,%r10d
    12ba:	mov    $0x8,%r11d
    12c0:	cmovne %r10,%r11
    12c4:	sub    %r11,%rdi
    12c7:	xor    %r10d,%r10d
    12ca:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12d9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e8:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f7:	nopw   0x0(%rax,%rax,1)
    1300:	movdqu (%r8,%r10,4),%xmm0
    1306:	movdqu 0x10(%r8,%r10,4),%xmm1
    130d:	movdqu (%rsi,%r10,4),%xmm2
    1313:	paddd  %xmm0,%xmm2
    1317:	movdqu 0x10(%rsi,%r10,4),%xmm0
    131e:	paddd  %xmm1,%xmm0
    1322:	movdqu %xmm2,(%r9,%r10,4)
    1328:	movdqu %xmm0,0x10(%r9,%r10,4)
    132f:	add    $0x8,%r10
    1333:	cmp    %r10,%rdi
    1336:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1338:	sub    %rdi,%rdx
    133b:	sub    %rdi,%rcx
    133e:	sub    %rdi,%rax
    1341:	lea    (%r8,%rdi,4),%r8
    1345:	lea    (%rsi,%rdi,4),%rsi
    1349:	lea    (%r9,%rdi,4),%rdi
    134d:	xor    %r9d,%r9d
    1350:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    135f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137d:	nopl   (%rax)
    1380:	cmp    %r9,%rcx
    1383:	je     139f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x15f>
    1385:	cmp    %r9,%rdx
    1388:	je     139f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x15f>
    138a:	mov    (%rsi,%r9,4),%r10d
    138e:	add    (%r8,%r9,4),%r10d
    1392:	mov    %r10d,(%rdi,%r9,4)
    1396:	inc    %r9
    1399:	cmp    %r9,%rax
    139c:	jne    1380 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>
    139e:	ret
    139f:	ud2
    13a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
