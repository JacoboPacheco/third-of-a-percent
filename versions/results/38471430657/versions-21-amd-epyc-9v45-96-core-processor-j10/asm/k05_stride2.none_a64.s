0000000000001240 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%r8
    1247:	mov    %r8,%rdi
    124a:	sub    %rax,%rdi
    124d:	je     12df <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9f>
    1253:	mov    %rdi,%rcx
    1256:	sar    $0x2,%rcx
    125a:	mov    (%rsi),%rdx
    125d:	cmp    $0x1c,%rcx
    1261:	jb     129e <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    1263:	lea    0x4(%rdx),%rsi
    1267:	lea    -0x1(%rcx),%r9
    126b:	shr    $0x3d,%r9
    126f:	setne  %r9b
    1273:	lea    (%rsi,%rcx,8),%r10
    1277:	add    $0xfffffffffffffff8,%r10
    127b:	cmp    %rsi,%r10
    127e:	setb   %sil
    1282:	or     %r9b,%sil
    1285:	jne    129e <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    1287:	lea    (%rdx,%rdi,2),%rsi
    128b:	cmp    %rsi,%rax
    128e:	setb   %sil
    1292:	cmp    %r8,%rdx
    1295:	setb   %r8b
    1299:	test   %r8b,%sil
    129c:	je     12e0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    129e:	xor    %esi,%esi
    12a0:	mov    %rsi,%r8
    12a3:	or     $0x1,%r8
    12a7:	test   $0x4,%dil
    12ab:	je     12ba <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7a>
    12ad:	mov    0x4(%rdx,%rsi,8),%edi
    12b1:	add    (%rdx,%rsi,8),%edi
    12b4:	mov    %edi,(%rax,%rsi,4)
    12b7:	mov    %r8,%rsi
    12ba:	cmp    %r8,%rcx
    12bd:	je     12df <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9f>
    12bf:	nop
    12c0:	mov    0x4(%rdx,%rsi,8),%edi
    12c4:	add    (%rdx,%rsi,8),%edi
    12c7:	mov    %edi,(%rax,%rsi,4)
    12ca:	mov    0xc(%rdx,%rsi,8),%edi
    12ce:	add    0x8(%rdx,%rsi,8),%edi
    12d2:	mov    %edi,0x4(%rax,%rsi,4)
    12d6:	add    $0x2,%rsi
    12da:	cmp    %rsi,%rcx
    12dd:	jne    12c0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12df:	ret
    12e0:	movabs $0x3ffffffffffffff8,%rsi
    12ea:	and    %rcx,%rsi
    12ed:	lea    (%rcx,%rcx,1),%r9
    12f1:	movabs $0x7ffffffffffffff0,%r8
    12fb:	and    %r9,%r8
    12fe:	xor    %r9d,%r9d
    1301:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1310:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    131f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    132e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133d:	nopl   (%rax)
    1340:	movups (%rdx,%r9,4),%xmm0
    1345:	movups 0x10(%rdx,%r9,4),%xmm1
    134b:	movups 0x20(%rdx,%r9,4),%xmm2
    1351:	movups 0x30(%rdx,%r9,4),%xmm3
    1357:	movaps %xmm0,%xmm4
    135a:	shufps $0x88,%xmm1,%xmm4
    135e:	shufps $0xdd,%xmm1,%xmm0
    1362:	paddd  %xmm4,%xmm0
    1366:	movaps %xmm2,%xmm1
    1369:	shufps $0x88,%xmm3,%xmm1
    136d:	shufps $0xdd,%xmm3,%xmm2
    1371:	paddd  %xmm1,%xmm2
    1375:	movdqu %xmm0,(%rax,%r9,2)
    137b:	movdqu %xmm2,0x10(%rax,%r9,2)
    1382:	add    $0x10,%r9
    1386:	cmp    %r9,%r8
    1389:	jne    1340 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    138b:	cmp    %rsi,%rcx
    138e:	je     12df <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9f>
    1394:	jmp    12a0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    1399:	nopl   0x0(%rax)
