0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rax
    1283:	mov    0x8(%rdi),%rdi
    1287:	mov    %rdi,%r8
    128a:	sub    %rax,%r8
    128d:	mov    %r8,%rcx
    1290:	sar    $0x2,%rcx
    1294:	js     13dd <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x15d>
    129a:	mov    (%rsi),%rdx
    129d:	mov    0x8(%rsi),%r9
    12a1:	sub    %rdx,%r9
    12a4:	sar    $0x2,%r9
    12a8:	mov    %r8,%rsi
    12ab:	shr    $1,%rsi
    12ae:	cmp    %rsi,%r9
    12b1:	jb     13dd <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x15d>
    12b7:	cmp    %rax,%rdi
    12ba:	je     13dc <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x15c>
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
    12f2:	jae    1308 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x88>
    12f4:	lea    (%rax,%r9,4),%r8
    12f8:	add    $0x4,%r8
    12fc:	cmp    %r8,%rdx
    12ff:	jae    1308 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x88>
    1301:	xor    %edi,%edi
    1303:	jmp    138b <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x10b>
    1308:	inc    %rdi
    130b:	mov    %edi,%r8d
    130e:	and    $0x7,%r8d
    1312:	mov    $0x8,%r9d
    1318:	cmovne %r8,%r9
    131c:	sub    %r9,%rdi
    131f:	xor    %r8d,%r8d
    1322:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1331:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	movups (%rdx,%r8,8),%xmm0
    1345:	movups 0x10(%rdx,%r8,8),%xmm1
    134b:	movups 0x20(%rdx,%r8,8),%xmm2
    1351:	movups 0x30(%rdx,%r8,8),%xmm3
    1357:	movaps %xmm0,%xmm4
    135a:	shufps $0x88,%xmm1,%xmm4
    135e:	movaps %xmm2,%xmm5
    1361:	shufps $0x88,%xmm3,%xmm5
    1365:	shufps $0xdd,%xmm1,%xmm0
    1369:	paddd  %xmm4,%xmm0
    136d:	shufps $0xdd,%xmm3,%xmm2
    1371:	paddd  %xmm5,%xmm2
    1375:	movdqu %xmm0,(%rax,%r8,4)
    137b:	movdqu %xmm2,0x10(%rax,%r8,4)
    1382:	add    $0x8,%r8
    1386:	cmp    %r8,%rdi
    1389:	jne    1340 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    138b:	sub    %rdi,%rcx
    138e:	lea    0x1(,%rdi,2),%rdi
    1396:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13a5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    13b4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    13c0:	cmp    %rdi,%rsi
    13c3:	jbe    13dd <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x15d>
    13c5:	mov    (%rdx,%rdi,4),%r8d
    13c9:	add    -0x4(%rdx,%rdi,4),%r8d
    13ce:	mov    %r8d,-0x2(%rax,%rdi,2)
    13d3:	add    $0x2,%rdi
    13d7:	dec    %rcx
    13da:	jne    13c0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13dc:	ret
    13dd:	ud2
    13df:	nop
