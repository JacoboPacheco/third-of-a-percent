0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rdi
    1247:	mov    %rdi,%rcx
    124a:	sub    %rax,%rcx
    124d:	sar    $0x2,%rcx
    1251:	mov    (%rsi),%rdx
    1254:	mov    0x8(%rsi),%rsi
    1258:	sub    %rdx,%rsi
    125b:	sar    $0x2,%rsi
    125f:	shr    $1,%rsi
    1262:	cmp    %rcx,%rsi
    1265:	jb     1345 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x105>
    126b:	cmp    %rax,%rdi
    126e:	je     1344 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
    1274:	cmp    $0x1,%rcx
    1278:	mov    %rcx,%rdi
    127b:	adc    $0x0,%rdi
    127f:	cmp    $0x8,%rcx
    1283:	jb     1297 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x57>
    1285:	lea    (%rdx,%rdi,8),%rsi
    1289:	cmp    %rsi,%rax
    128c:	jae    12e1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    128e:	lea    (%rax,%rdi,4),%rsi
    1292:	cmp    %rsi,%rdx
    1295:	jae    12e1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    1297:	xor    %esi,%esi
    1299:	mov    %rsi,%r8
    129c:	or     $0x1,%r8
    12a0:	test   $0x1,%dil
    12a4:	je     12b6 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x76>
    12a6:	mov    0x4(%rdx,%rsi,8),%r9d
    12ab:	add    (%rdx,%rsi,8),%r9d
    12af:	mov    %r9d,(%rax,%rsi,4)
    12b3:	mov    %r8,%rsi
    12b6:	cmp    %r8,%rdi
    12b9:	je     1344 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
    12bf:	nop
    12c0:	mov    0x4(%rdx,%rsi,8),%edi
    12c4:	add    (%rdx,%rsi,8),%edi
    12c7:	mov    %edi,(%rax,%rsi,4)
    12ca:	mov    0xc(%rdx,%rsi,8),%edi
    12ce:	add    0x8(%rdx,%rsi,8),%edi
    12d2:	mov    %edi,0x4(%rax,%rsi,4)
    12d6:	add    $0x2,%rsi
    12da:	cmp    %rsi,%rcx
    12dd:	jne    12c0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12df:	jmp    1344 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
    12e1:	mov    %rdi,%rsi
    12e4:	and    $0xfffffffffffffff8,%rsi
    12e8:	xor    %r8d,%r8d
    12eb:	nopl   0x0(%rax,%rax,1)
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
    133e:	jne    1299 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x59>
    1344:	ret
    1345:	ud2
    1347:	nopw   0x0(%rax,%rax,1)
