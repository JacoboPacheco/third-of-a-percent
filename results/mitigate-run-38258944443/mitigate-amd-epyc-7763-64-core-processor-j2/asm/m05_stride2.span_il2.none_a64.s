0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rax
    1283:	mov    0x8(%rdi),%rdx
    1287:	mov    %rdx,%rcx
    128a:	sub    %rax,%rcx
    128d:	sar    $0x2,%rcx
    1291:	js     1395 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x115>
    1297:	cmp    %rax,%rdx
    129a:	je     1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12a0:	mov    (%rsi),%rdx
    12a3:	cmp    $0x1,%rcx
    12a7:	mov    %rcx,%rdi
    12aa:	adc    $0x0,%rdi
    12ae:	cmp    $0x8,%rcx
    12b2:	jb     12c6 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x46>
    12b4:	lea    (%rdx,%rdi,8),%rsi
    12b8:	cmp    %rsi,%rax
    12bb:	jae    1321 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    12bd:	lea    (%rax,%rdi,4),%rsi
    12c1:	cmp    %rsi,%rdx
    12c4:	jae    1321 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    12c6:	xor    %esi,%esi
    12c8:	mov    %rsi,%r8
    12cb:	or     $0x1,%r8
    12cf:	test   $0x1,%dil
    12d3:	je     12e5 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x65>
    12d5:	mov    0x4(%rdx,%rsi,8),%r9d
    12da:	add    (%rdx,%rsi,8),%r9d
    12de:	mov    %r9d,(%rax,%rsi,4)
    12e2:	mov    %r8,%rsi
    12e5:	cmp    %r8,%rdi
    12e8:	je     1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12ee:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fd:	nopl   (%rax)
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
    1321:	movabs $0x7ffffffffffffff8,%rsi
    132b:	and    %rdi,%rsi
    132e:	xor    %r8d,%r8d
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
    1386:	cmp    %r8,%rsi
    1389:	jne    1340 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    138b:	cmp    %rsi,%rdi
    138e:	jne    12c8 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>
    1394:	ret
    1395:	ud2
    1397:	nopw   0x0(%rax,%rax,1)
