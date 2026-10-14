0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%r8
    1227:	mov    %r8,%rdi
    122a:	sub    %rax,%rdi
    122d:	je     12bf <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9f>
    1233:	mov    %rdi,%rcx
    1236:	sar    $0x2,%rcx
    123a:	mov    (%rsi),%rdx
    123d:	cmp    $0x1c,%rcx
    1241:	jb     127e <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    1243:	lea    0x4(%rdx),%rsi
    1247:	lea    -0x1(%rcx),%r9
    124b:	shr    $0x3d,%r9
    124f:	setne  %r9b
    1253:	lea    (%rsi,%rcx,8),%r10
    1257:	add    $0xfffffffffffffff8,%r10
    125b:	cmp    %rsi,%r10
    125e:	setb   %sil
    1262:	or     %r9b,%sil
    1265:	jne    127e <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    1267:	lea    (%rdx,%rdi,2),%rsi
    126b:	cmp    %rsi,%rax
    126e:	setb   %sil
    1272:	cmp    %r8,%rdx
    1275:	setb   %r8b
    1279:	test   %r8b,%sil
    127c:	je     12c0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    127e:	xor    %esi,%esi
    1280:	mov    %rsi,%r8
    1283:	or     $0x1,%r8
    1287:	test   $0x4,%dil
    128b:	je     129a <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7a>
    128d:	mov    0x4(%rdx,%rsi,8),%edi
    1291:	add    (%rdx,%rsi,8),%edi
    1294:	mov    %edi,(%rax,%rsi,4)
    1297:	mov    %r8,%rsi
    129a:	cmp    %r8,%rcx
    129d:	je     12bf <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9f>
    129f:	nop
    12a0:	mov    0x4(%rdx,%rsi,8),%edi
    12a4:	add    (%rdx,%rsi,8),%edi
    12a7:	mov    %edi,(%rax,%rsi,4)
    12aa:	mov    0xc(%rdx,%rsi,8),%edi
    12ae:	add    0x8(%rdx,%rsi,8),%edi
    12b2:	mov    %edi,0x4(%rax,%rsi,4)
    12b6:	add    $0x2,%rsi
    12ba:	cmp    %rsi,%rcx
    12bd:	jne    12a0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12bf:	ret
    12c0:	movabs $0x3ffffffffffffff8,%rsi
    12ca:	and    %rcx,%rsi
    12cd:	lea    (%rcx,%rcx,1),%r9
    12d1:	movabs $0x7ffffffffffffff0,%r8
    12db:	and    %r9,%r8
    12de:	xor    %r9d,%r9d
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	movups (%rdx,%r9,4),%xmm0
    12f5:	movups 0x10(%rdx,%r9,4),%xmm1
    12fb:	movups 0x20(%rdx,%r9,4),%xmm2
    1301:	movups 0x30(%rdx,%r9,4),%xmm3
    1307:	movaps %xmm0,%xmm4
    130a:	shufps $0x88,%xmm1,%xmm4
    130e:	shufps $0xdd,%xmm1,%xmm0
    1312:	paddd  %xmm4,%xmm0
    1316:	movaps %xmm2,%xmm1
    1319:	shufps $0x88,%xmm3,%xmm1
    131d:	shufps $0xdd,%xmm3,%xmm2
    1321:	paddd  %xmm1,%xmm2
    1325:	movdqu %xmm0,(%rax,%r9,2)
    132b:	movdqu %xmm2,0x10(%rax,%r9,2)
    1332:	add    $0x10,%r9
    1336:	cmp    %r9,%r8
    1339:	jne    12f0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd0>
    133b:	cmp    %rsi,%rcx
    133e:	je     12bf <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9f>
    1344:	jmp    1280 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    1349:	nopl   0x0(%rax)
