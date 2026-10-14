0000000000001280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rdi),%rax
    1283:	mov    0x8(%rdi),%rdi
    1287:	mov    %rdi,%rcx
    128a:	sub    %rax,%rcx
    128d:	sar    $0x2,%rcx
    1291:	mov    (%rsi),%rdx
    1294:	mov    0x8(%rsi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	shr    $1,%rsi
    12a2:	cmp    %rcx,%rsi
    12a5:	jb     1395 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x115>
    12ab:	cmp    %rax,%rdi
    12ae:	je     1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12b4:	cmp    $0x1,%rcx
    12b8:	mov    %rcx,%rdi
    12bb:	adc    $0x0,%rdi
    12bf:	cmp    $0x8,%rcx
    12c3:	jb     12d7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x57>
    12c5:	lea    (%rdx,%rdi,8),%rsi
    12c9:	cmp    %rsi,%rax
    12cc:	jae    1321 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    12ce:	lea    (%rax,%rdi,4),%rsi
    12d2:	cmp    %rsi,%rdx
    12d5:	jae    1321 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    12d7:	xor    %esi,%esi
    12d9:	mov    %rsi,%r8
    12dc:	or     $0x1,%r8
    12e0:	test   $0x1,%dil
    12e4:	je     12f6 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x76>
    12e6:	mov    0x4(%rdx,%rsi,8),%r9d
    12eb:	add    (%rdx,%rsi,8),%r9d
    12ef:	mov    %r9d,(%rax,%rsi,4)
    12f3:	mov    %r8,%rsi
    12f6:	cmp    %r8,%rdi
    12f9:	je     1394 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12ff:	nop
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
    138e:	jne    12d9 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x59>
    1394:	ret
    1395:	ud2
    1397:	nopw   0x0(%rax,%rax,1)
