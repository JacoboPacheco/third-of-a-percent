0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1314 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rsi),%rdx
    1237:	cmp    $0x1,%rcx
    123b:	mov    %rcx,%rdi
    123e:	adc    $0x0,%rdi
    1242:	cmp    $0x8,%rcx
    1246:	jb     125a <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3a>
    1248:	lea    (%rdx,%rdi,8),%rsi
    124c:	cmp    %rsi,%rax
    124f:	jae    12b1 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x91>
    1251:	lea    (%rax,%rdi,4),%rsi
    1255:	cmp    %rsi,%rdx
    1258:	jae    12b1 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x91>
    125a:	xor    %esi,%esi
    125c:	mov    %rsi,%r8
    125f:	or     $0x1,%r8
    1263:	test   $0x1,%dil
    1267:	je     1279 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x59>
    1269:	mov    0x4(%rdx,%rsi,8),%r9d
    126e:	add    (%rdx,%rsi,8),%r9d
    1272:	mov    %r9d,(%rax,%rsi,4)
    1276:	mov    %r8,%rsi
    1279:	cmp    %r8,%rdi
    127c:	je     1314 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1282:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	mov    0x4(%rdx,%rsi,8),%edi
    1294:	add    (%rdx,%rsi,8),%edi
    1297:	mov    %edi,(%rax,%rsi,4)
    129a:	mov    0xc(%rdx,%rsi,8),%edi
    129e:	add    0x8(%rdx,%rsi,8),%edi
    12a2:	mov    %edi,0x4(%rax,%rsi,4)
    12a6:	add    $0x2,%rsi
    12aa:	cmp    %rsi,%rcx
    12ad:	jne    1290 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    12af:	jmp    1314 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12b1:	mov    %rdi,%rsi
    12b4:	and    $0xfffffffffffffff8,%rsi
    12b8:	xor    %r8d,%r8d
    12bb:	nopl   0x0(%rax,%rax,1)
    12c0:	movups (%rdx,%r8,8),%xmm0
    12c5:	movups 0x10(%rdx,%r8,8),%xmm1
    12cb:	movups 0x20(%rdx,%r8,8),%xmm2
    12d1:	movups 0x30(%rdx,%r8,8),%xmm3
    12d7:	movaps %xmm0,%xmm4
    12da:	shufps $0x88,%xmm1,%xmm4
    12de:	movaps %xmm2,%xmm5
    12e1:	shufps $0x88,%xmm3,%xmm5
    12e5:	shufps $0xdd,%xmm1,%xmm0
    12e9:	paddd  %xmm4,%xmm0
    12ed:	shufps $0xdd,%xmm3,%xmm2
    12f1:	paddd  %xmm5,%xmm2
    12f5:	movdqu %xmm0,(%rax,%r8,4)
    12fb:	movdqu %xmm2,0x10(%rax,%r8,4)
    1302:	add    $0x8,%r8
    1306:	cmp    %r8,%rsi
    1309:	jne    12c0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    130b:	cmp    %rsi,%rdi
    130e:	jne    125c <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3c>
    1314:	ret
    1315:	data16 cs nopw 0x0(%rax,%rax,1)
