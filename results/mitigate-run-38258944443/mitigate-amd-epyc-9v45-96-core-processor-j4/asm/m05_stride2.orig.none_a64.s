0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rax
    1283:	mov    0x8(%rdi),%rcx
    1287:	sub    %rax,%rcx
    128a:	je     1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    1290:	sar    $0x2,%rcx
    1294:	mov    (%rsi),%rdx
    1297:	cmp    $0x1,%rcx
    129b:	mov    %rcx,%rdi
    129e:	adc    $0x0,%rdi
    12a2:	cmp    $0x8,%rcx
    12a6:	jb     12ba <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3a>
    12a8:	lea    (%rdx,%rdi,8),%rsi
    12ac:	cmp    %rsi,%rax
    12af:	jae    1321 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    12b1:	lea    (%rax,%rdi,4),%rsi
    12b5:	cmp    %rsi,%rdx
    12b8:	jae    1321 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    12ba:	xor    %esi,%esi
    12bc:	mov    %rsi,%r8
    12bf:	or     $0x1,%r8
    12c3:	test   $0x1,%dil
    12c7:	je     12d9 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x59>
    12c9:	mov    0x4(%rdx,%rsi,8),%r9d
    12ce:	add    (%rdx,%rsi,8),%r9d
    12d2:	mov    %r9d,(%rax,%rsi,4)
    12d6:	mov    %r8,%rsi
    12d9:	cmp    %r8,%rdi
    12dc:	je     1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12e2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	mov    0x4(%rdx,%rsi,8),%edi
    1304:	add    (%rdx,%rsi,8),%edi
    1307:	mov    %edi,(%rax,%rsi,4)
    130a:	mov    0xc(%rdx,%rsi,8),%edi
    130e:	add    0x8(%rdx,%rsi,8),%edi
    1312:	mov    %edi,0x4(%rax,%rsi,4)
    1316:	add    $0x2,%rsi
    131a:	cmp    %rsi,%rcx
    131d:	jne    1300 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    131f:	jmp    1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    1321:	mov    %rdi,%rsi
    1324:	and    $0xfffffffffffffff8,%rsi
    1328:	xor    %r8d,%r8d
    132b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133a:	nopw   0x0(%rax,%rax,1)
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
    1386:	cmp    %r8,%rsi
    1389:	jne    1340 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    138b:	cmp    %rsi,%rdi
    138e:	jne    12bc <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3c>
    1394:	ret
    1395:	data16 cs nopw 0x0(%rax,%rax,1)
