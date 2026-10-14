0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rcx
    1283:	mov    0x8(%rdi),%rdi
    1287:	mov    %rdi,%rax
    128a:	sub    %rcx,%rax
    128d:	sar    $0x2,%rax
    1291:	mov    (%rsi),%rdx
    1294:	mov    0x8(%rsi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	shr    $1,%rsi
    12a2:	cmp    %rax,%rsi
    12a5:	jb     13d5 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x155>
    12ab:	cmp    %rcx,%rdi
    12ae:	je     13d4 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x154>
    12b4:	cmp    $0x1,%rax
    12b8:	mov    %rax,%rsi
    12bb:	adc    $0x0,%rsi
    12bf:	cmp    $0x8,%rax
    12c3:	jb     12df <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5f>
    12c5:	lea    (%rdx,%rsi,8),%rdi
    12c9:	cmp    %rdi,%rcx
    12cc:	jae    1361 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe1>
    12d2:	lea    (%rcx,%rsi,4),%rdi
    12d6:	cmp    %rdi,%rdx
    12d9:	jae    1361 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe1>
    12df:	xor    %edi,%edi
    12e1:	xor    %r8d,%r8d
    12e4:	mov    %r8,%r9
    12e7:	or     $0x1,%r9
    12eb:	test   $0x1,%sil
    12ef:	je     1305 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12f1:	mov    0x4(%rdx,%rdi,4),%r10d
    12f6:	add    (%rdx,%rdi,4),%r10d
    12fa:	mov    %r10d,(%rcx,%r8,4)
    12fe:	add    $0x2,%rdi
    1302:	mov    %r9,%r8
    1305:	cmp    %r9,%rsi
    1308:	je     13d4 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x154>
    130e:	lea    (%rdx,%rdi,4),%rdx
    1312:	add    $0xc,%rdx
    1316:	lea    (%rcx,%r8,4),%rcx
    131a:	add    $0x4,%rcx
    131e:	sub    %r8,%rax
    1321:	xor    %esi,%esi
    1323:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1332:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	mov    -0x8(%rdx,%rsi,8),%edi
    1344:	add    -0xc(%rdx,%rsi,8),%edi
    1348:	mov    %edi,-0x4(%rcx,%rsi,4)
    134c:	mov    (%rdx,%rsi,8),%edi
    134f:	add    -0x4(%rdx,%rsi,8),%edi
    1353:	mov    %edi,(%rcx,%rsi,4)
    1356:	add    $0x2,%rsi
    135a:	cmp    %rsi,%rax
    135d:	jne    1340 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    135f:	jmp    13d4 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x154>
    1361:	mov    %rsi,%r8
    1364:	and    $0xfffffffffffffff8,%r8
    1368:	lea    (%r8,%r8,1),%rdi
    136c:	xor    %r9d,%r9d
    136f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137e:	xchg   %ax,%ax
    1380:	movups (%rdx,%r9,8),%xmm0
    1385:	movups 0x10(%rdx,%r9,8),%xmm1
    138b:	movups 0x20(%rdx,%r9,8),%xmm2
    1391:	movups 0x30(%rdx,%r9,8),%xmm3
    1397:	movaps %xmm0,%xmm4
    139a:	shufps $0x88,%xmm1,%xmm4
    139e:	movaps %xmm2,%xmm5
    13a1:	shufps $0x88,%xmm3,%xmm5
    13a5:	shufps $0xdd,%xmm1,%xmm0
    13a9:	paddd  %xmm4,%xmm0
    13ad:	shufps $0xdd,%xmm3,%xmm2
    13b1:	paddd  %xmm5,%xmm2
    13b5:	movdqu %xmm0,(%rcx,%r9,4)
    13bb:	movdqu %xmm2,0x10(%rcx,%r9,4)
    13c2:	add    $0x8,%r9
    13c6:	cmp    %r9,%r8
    13c9:	jne    1380 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    13cb:	cmp    %r8,%rsi
    13ce:	jne    12e4 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>
    13d4:	ret
    13d5:	ud2
    13d7:	nopw   0x0(%rax,%rax,1)
