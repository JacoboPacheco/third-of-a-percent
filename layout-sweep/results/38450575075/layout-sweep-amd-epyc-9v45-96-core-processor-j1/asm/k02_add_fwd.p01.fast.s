0000000000001230 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1230:	mov    (%rsi),%r8
    1233:	mov    0x8(%rsi),%rax
    1237:	sub    %r8,%rax
    123a:	je     131e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1240:	sar    $0x2,%rax
    1244:	mov    (%rdx),%rsi
    1247:	mov    0x8(%rdx),%rcx
    124b:	sub    %rsi,%rcx
    124e:	sar    $0x2,%rcx
    1252:	mov    (%rdi),%r9
    1255:	mov    0x8(%rdi),%rdx
    1259:	sub    %r9,%rdx
    125c:	sar    $0x2,%rdx
    1260:	cmp    $0x1,%rax
    1264:	adc    $0x0,%rax
    1268:	lea    -0x1(%rax),%r10
    126c:	cmp    %rdx,%r10
    126f:	cmovae %rdx,%r10
    1273:	cmp    %rcx,%r10
    1276:	cmovae %rcx,%r10
    127a:	cmp    $0x7,%r10
    127e:	ja     1284 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    1280:	xor    %edi,%edi
    1282:	jmp    12df <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1284:	mov    %r9,%r11
    1287:	sub    %r8,%r11
    128a:	xor    %edi,%edi
    128c:	cmp    $0x10,%r11
    1290:	jb     12df <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1292:	mov    %r9,%r11
    1295:	sub    %rsi,%r11
    1298:	cmp    $0x10,%r11
    129c:	jb     12df <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    129e:	inc    %r10
    12a1:	mov    %r10d,%edi
    12a4:	and    $0x3,%edi
    12a7:	mov    $0x4,%r11d
    12ad:	cmovne %rdi,%r11
    12b1:	mov    %r10,%rdi
    12b4:	sub    %r11,%rdi
    12b7:	xor    %r10d,%r10d
    12ba:	nopw   0x0(%rax,%rax,1)
    12c0:	movdqu (%r8,%r10,4),%xmm0
    12c6:	movdqu (%rsi,%r10,4),%xmm1
    12cc:	paddd  %xmm0,%xmm1
    12d0:	movdqu %xmm1,(%r9,%r10,4)
    12d6:	add    $0x4,%r10
    12da:	cmp    %r10,%rdi
    12dd:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12df:	sub    %rdi,%rdx
    12e2:	sub    %rdi,%rcx
    12e5:	sub    %rdi,%rax
    12e8:	lea    (%r8,%rdi,4),%r8
    12ec:	lea    (%rsi,%rdi,4),%rsi
    12f0:	lea    (%r9,%rdi,4),%rdi
    12f4:	xor    %r9d,%r9d
    12f7:	nopw   0x0(%rax,%rax,1)
    1300:	cmp    %r9,%rcx
    1303:	je     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    1305:	cmp    %r9,%rdx
    1308:	je     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    130a:	mov    (%rsi,%r9,4),%r10d
    130e:	add    (%r8,%r9,4),%r10d
    1312:	mov    %r10d,(%rdi,%r9,4)
    1316:	inc    %r9
    1319:	cmp    %r9,%rax
    131c:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    131e:	ret
    131f:	ud2
    1321:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
