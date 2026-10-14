0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rdx
    1247:	mov    %rdx,%rcx
    124a:	sub    %rax,%rcx
    124d:	sar    $0x2,%rcx
    1251:	js     1345 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x105>
    1257:	cmp    %rax,%rdx
    125a:	je     1344 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
    1260:	mov    (%rsi),%rdx
    1263:	cmp    $0x1,%rcx
    1267:	mov    %rcx,%rdi
    126a:	adc    $0x0,%rdi
    126e:	cmp    $0x8,%rcx
    1272:	jb     1286 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x46>
    1274:	lea    (%rdx,%rdi,8),%rsi
    1278:	cmp    %rsi,%rax
    127b:	jae    12d1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x91>
    127d:	lea    (%rax,%rdi,4),%rsi
    1281:	cmp    %rsi,%rdx
    1284:	jae    12d1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x91>
    1286:	xor    %esi,%esi
    1288:	mov    %rsi,%r8
    128b:	or     $0x1,%r8
    128f:	test   $0x1,%dil
    1293:	je     12a5 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x65>
    1295:	mov    0x4(%rdx,%rsi,8),%r9d
    129a:	add    (%rdx,%rsi,8),%r9d
    129e:	mov    %r9d,(%rax,%rsi,4)
    12a2:	mov    %r8,%rsi
    12a5:	cmp    %r8,%rdi
    12a8:	je     1344 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
    12ae:	xchg   %ax,%ax
    12b0:	mov    0x4(%rdx,%rsi,8),%edi
    12b4:	add    (%rdx,%rsi,8),%edi
    12b7:	mov    %edi,(%rax,%rsi,4)
    12ba:	mov    0xc(%rdx,%rsi,8),%edi
    12be:	add    0x8(%rdx,%rsi,8),%edi
    12c2:	mov    %edi,0x4(%rax,%rsi,4)
    12c6:	add    $0x2,%rsi
    12ca:	cmp    %rsi,%rcx
    12cd:	jne    12b0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    12cf:	jmp    1344 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
    12d1:	movabs $0x7ffffffffffffff8,%rsi
    12db:	and    %rdi,%rsi
    12de:	xor    %r8d,%r8d
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	movups (%rdx,%r8,8),%xmm0
    12f5:	movups 0x10(%rdx,%r8,8),%xmm1
    12fb:	movups 0x20(%rdx,%r8,8),%xmm2
    1301:	movups 0x30(%rdx,%r8,8),%xmm3
    1307:	movaps %xmm0,%xmm4
    130a:	shufps $0x88,%xmm1,%xmm4
    130e:	movaps %xmm2,%xmm5
    1311:	shufps $0x88,%xmm3,%xmm5
    1315:	shufps $0xdd,%xmm1,%xmm0
    1319:	paddd  %xmm4,%xmm0
    131d:	shufps $0xdd,%xmm3,%xmm2
    1321:	paddd  %xmm5,%xmm2
    1325:	movdqu %xmm0,(%rax,%r8,4)
    132b:	movdqu %xmm2,0x10(%rax,%r8,4)
    1332:	add    $0x8,%r8
    1336:	cmp    %r8,%rsi
    1339:	jne    12f0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>
    133b:	cmp    %rsi,%rdi
    133e:	jne    1288 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>
    1344:	ret
    1345:	ud2
    1347:	nopw   0x0(%rax,%rax,1)
