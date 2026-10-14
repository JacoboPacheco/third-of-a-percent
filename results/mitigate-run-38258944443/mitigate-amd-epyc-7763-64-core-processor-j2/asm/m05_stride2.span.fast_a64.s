0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rax
    1283:	mov    0x8(%rdi),%rdi
    1287:	mov    %rdi,%r8
    128a:	sub    %rax,%r8
    128d:	mov    %r8,%rcx
    1290:	sar    $0x2,%rcx
    1294:	js     139d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11d>
    129a:	mov    (%rsi),%rdx
    129d:	mov    0x8(%rsi),%r9
    12a1:	sub    %rdx,%r9
    12a4:	sar    $0x2,%r9
    12a8:	mov    %r8,%rsi
    12ab:	shr    $1,%rsi
    12ae:	cmp    %rsi,%r9
    12b1:	jb     139d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11d>
    12b7:	cmp    %rax,%rdi
    12ba:	je     139c <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11c>
    12c0:	cmp    $0x1,%rcx
    12c4:	adc    $0x0,%rcx
    12c8:	shr    $0x2,%r8
    12cc:	lea    -0x1(%rcx),%r9
    12d0:	cmp    %r9,%r8
    12d3:	mov    %r9,%rdi
    12d6:	cmovb  %r8,%rdi
    12da:	cmp    $0xf,%rdi
    12de:	jbe    1301 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x81>
    12e0:	cmp    %r9,%r8
    12e3:	cmovb  %r8,%r9
    12e7:	lea    (%rdx,%r9,8),%r8
    12eb:	add    $0x8,%r8
    12ef:	cmp    %r8,%rax
    12f2:	jae    1305 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12f4:	lea    (%rax,%r9,4),%r8
    12f8:	add    $0x4,%r8
    12fc:	cmp    %r8,%rdx
    12ff:	jae    1305 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    1301:	xor    %edi,%edi
    1303:	jmp    1369 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe9>
    1305:	inc    %rdi
    1308:	mov    %edi,%r8d
    130b:	and    $0x3,%r8d
    130f:	mov    $0x4,%r9d
    1315:	cmovne %r8,%r9
    1319:	sub    %r9,%rdi
    131c:	xor    %r8d,%r8d
    131f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    132e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133d:	nopl   (%rax)
    1340:	movups (%rdx,%r8,8),%xmm0
    1345:	movups 0x10(%rdx,%r8,8),%xmm1
    134b:	movaps %xmm0,%xmm2
    134e:	shufps $0x88,%xmm1,%xmm2
    1352:	shufps $0xdd,%xmm1,%xmm0
    1356:	paddd  %xmm2,%xmm0
    135a:	movdqu %xmm0,(%rax,%r8,4)
    1360:	add    $0x4,%r8
    1364:	cmp    %r8,%rdi
    1367:	jne    1340 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1369:	sub    %rdi,%rcx
    136c:	lea    0x1(,%rdi,2),%rdi
    1374:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	cmp    %rdi,%rsi
    1383:	jbe    139d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11d>
    1385:	mov    (%rdx,%rdi,4),%r8d
    1389:	add    -0x4(%rdx,%rdi,4),%r8d
    138e:	mov    %r8d,-0x2(%rax,%rdi,2)
    1393:	add    $0x2,%rdi
    1397:	dec    %rcx
    139a:	jne    1380 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    139c:	ret
    139d:	ud2
    139f:	nop
