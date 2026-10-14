0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rcx
    1243:	mov    0x8(%rdi),%rdi
    1247:	mov    %rdi,%rax
    124a:	sub    %rcx,%rax
    124d:	sar    $0x2,%rax
    1251:	mov    (%rsi),%rdx
    1254:	mov    0x8(%rsi),%rsi
    1258:	sub    %rdx,%rsi
    125b:	sar    $0x2,%rsi
    125f:	shr    $1,%rsi
    1262:	cmp    %rax,%rsi
    1265:	jb     1365 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x125>
    126b:	cmp    %rcx,%rdi
    126e:	je     1364 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x124>
    1274:	cmp    $0x1,%rax
    1278:	mov    %rax,%rsi
    127b:	adc    $0x0,%rsi
    127f:	cmp    $0x8,%rax
    1283:	jb     1297 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x57>
    1285:	lea    (%rdx,%rsi,8),%rdi
    1289:	cmp    %rdi,%rcx
    128c:	jae    1301 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc1>
    128e:	lea    (%rcx,%rsi,4),%rdi
    1292:	cmp    %rdi,%rdx
    1295:	jae    1301 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc1>
    1297:	xor    %edi,%edi
    1299:	xor    %r8d,%r8d
    129c:	mov    %r8,%r9
    129f:	or     $0x1,%r9
    12a3:	test   $0x1,%sil
    12a7:	je     12bd <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7d>
    12a9:	mov    0x4(%rdx,%rdi,4),%r10d
    12ae:	add    (%rdx,%rdi,4),%r10d
    12b2:	mov    %r10d,(%rcx,%r8,4)
    12b6:	add    $0x2,%rdi
    12ba:	mov    %r9,%r8
    12bd:	cmp    %r9,%rsi
    12c0:	je     1364 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x124>
    12c6:	lea    (%rdx,%rdi,4),%rdx
    12ca:	add    $0xc,%rdx
    12ce:	lea    (%rcx,%r8,4),%rcx
    12d2:	add    $0x4,%rcx
    12d6:	sub    %r8,%rax
    12d9:	xor    %esi,%esi
    12db:	nopl   0x0(%rax,%rax,1)
    12e0:	mov    -0x8(%rdx,%rsi,8),%edi
    12e4:	add    -0xc(%rdx,%rsi,8),%edi
    12e8:	mov    %edi,-0x4(%rcx,%rsi,4)
    12ec:	mov    (%rdx,%rsi,8),%edi
    12ef:	add    -0x4(%rdx,%rsi,8),%edi
    12f3:	mov    %edi,(%rcx,%rsi,4)
    12f6:	add    $0x2,%rsi
    12fa:	cmp    %rsi,%rax
    12fd:	jne    12e0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12ff:	jmp    1364 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x124>
    1301:	mov    %rsi,%r8
    1304:	and    $0xfffffffffffffff8,%r8
    1308:	lea    (%r8,%r8,1),%rdi
    130c:	xor    %r9d,%r9d
    130f:	nop
    1310:	movups (%rdx,%r9,8),%xmm0
    1315:	movups 0x10(%rdx,%r9,8),%xmm1
    131b:	movups 0x20(%rdx,%r9,8),%xmm2
    1321:	movups 0x30(%rdx,%r9,8),%xmm3
    1327:	movaps %xmm0,%xmm4
    132a:	shufps $0x88,%xmm1,%xmm4
    132e:	movaps %xmm2,%xmm5
    1331:	shufps $0x88,%xmm3,%xmm5
    1335:	shufps $0xdd,%xmm1,%xmm0
    1339:	paddd  %xmm4,%xmm0
    133d:	shufps $0xdd,%xmm3,%xmm2
    1341:	paddd  %xmm5,%xmm2
    1345:	movdqu %xmm0,(%rcx,%r9,4)
    134b:	movdqu %xmm2,0x10(%rcx,%r9,4)
    1352:	add    $0x8,%r9
    1356:	cmp    %r9,%r8
    1359:	jne    1310 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd0>
    135b:	cmp    %r8,%rsi
    135e:	jne    129c <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5c>
    1364:	ret
    1365:	ud2
    1367:	nopw   0x0(%rax,%rax,1)
