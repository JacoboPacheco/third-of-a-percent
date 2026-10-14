0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1334 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rsi),%rdx
    1257:	cmp    $0x1,%rcx
    125b:	mov    %rcx,%rdi
    125e:	adc    $0x0,%rdi
    1262:	cmp    $0x8,%rcx
    1266:	jb     127a <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3a>
    1268:	lea    (%rdx,%rdi,8),%rsi
    126c:	cmp    %rsi,%rax
    126f:	jae    12d1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x91>
    1271:	lea    (%rax,%rdi,4),%rsi
    1275:	cmp    %rsi,%rdx
    1278:	jae    12d1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x91>
    127a:	xor    %esi,%esi
    127c:	mov    %rsi,%r8
    127f:	or     $0x1,%r8
    1283:	test   $0x1,%dil
    1287:	je     1299 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x59>
    1289:	mov    0x4(%rdx,%rsi,8),%r9d
    128e:	add    (%rdx,%rsi,8),%r9d
    1292:	mov    %r9d,(%rax,%rsi,4)
    1296:	mov    %r8,%rsi
    1299:	cmp    %r8,%rdi
    129c:	je     1334 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12a2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	mov    0x4(%rdx,%rsi,8),%edi
    12b4:	add    (%rdx,%rsi,8),%edi
    12b7:	mov    %edi,(%rax,%rsi,4)
    12ba:	mov    0xc(%rdx,%rsi,8),%edi
    12be:	add    0x8(%rdx,%rsi,8),%edi
    12c2:	mov    %edi,0x4(%rax,%rsi,4)
    12c6:	add    $0x2,%rsi
    12ca:	cmp    %rsi,%rcx
    12cd:	jne    12b0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    12cf:	jmp    1334 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12d1:	mov    %rdi,%rsi
    12d4:	and    $0xfffffffffffffff8,%rsi
    12d8:	xor    %r8d,%r8d
    12db:	nopl   0x0(%rax,%rax,1)
    12e0:	movups (%rdx,%r8,8),%xmm0
    12e5:	movups 0x10(%rdx,%r8,8),%xmm1
    12eb:	movups 0x20(%rdx,%r8,8),%xmm2
    12f1:	movups 0x30(%rdx,%r8,8),%xmm3
    12f7:	movaps %xmm0,%xmm4
    12fa:	shufps $0x88,%xmm1,%xmm4
    12fe:	movaps %xmm2,%xmm5
    1301:	shufps $0x88,%xmm3,%xmm5
    1305:	shufps $0xdd,%xmm1,%xmm0
    1309:	paddd  %xmm4,%xmm0
    130d:	shufps $0xdd,%xmm3,%xmm2
    1311:	paddd  %xmm5,%xmm2
    1315:	movdqu %xmm0,(%rax,%r8,4)
    131b:	movdqu %xmm2,0x10(%rax,%r8,4)
    1322:	add    $0x8,%r8
    1326:	cmp    %r8,%rsi
    1329:	jne    12e0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    132b:	cmp    %rsi,%rdi
    132e:	jne    127c <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x3c>
    1334:	ret
    1335:	data16 cs nopw 0x0(%rax,%rax,1)
