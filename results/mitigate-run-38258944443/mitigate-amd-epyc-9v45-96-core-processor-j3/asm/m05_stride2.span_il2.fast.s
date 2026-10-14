0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rdi
    1247:	mov    %rdi,%r8
    124a:	sub    %rax,%r8
    124d:	mov    %r8,%rcx
    1250:	sar    $0x2,%rcx
    1254:	js     135d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11d>
    125a:	mov    (%rsi),%rdx
    125d:	mov    0x8(%rsi),%r9
    1261:	sub    %rdx,%r9
    1264:	sar    $0x2,%r9
    1268:	mov    %r8,%rsi
    126b:	shr    $1,%rsi
    126e:	cmp    %rsi,%r9
    1271:	jb     135d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11d>
    1277:	cmp    %rax,%rdi
    127a:	je     135c <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11c>
    1280:	cmp    $0x1,%rcx
    1284:	adc    $0x0,%rcx
    1288:	shr    $0x2,%r8
    128c:	lea    -0x1(%rcx),%r9
    1290:	cmp    %r9,%r8
    1293:	mov    %r9,%rdi
    1296:	cmovb  %r8,%rdi
    129a:	cmp    $0xf,%rdi
    129e:	jbe    12c1 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x81>
    12a0:	cmp    %r9,%r8
    12a3:	cmovb  %r8,%r9
    12a7:	lea    (%rdx,%r9,8),%r8
    12ab:	add    $0x8,%r8
    12af:	cmp    %r8,%rax
    12b2:	jae    12c5 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12b4:	lea    (%rax,%r9,4),%r8
    12b8:	add    $0x4,%r8
    12bc:	cmp    %r8,%rdx
    12bf:	jae    12c5 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12c1:	xor    %edi,%edi
    12c3:	jmp    132b <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xeb>
    12c5:	inc    %rdi
    12c8:	mov    %edi,%r8d
    12cb:	and    $0x7,%r8d
    12cf:	mov    $0x8,%r9d
    12d5:	cmovne %r8,%r9
    12d9:	sub    %r9,%rdi
    12dc:	xor    %r8d,%r8d
    12df:	nop
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
    1326:	cmp    %r8,%rdi
    1329:	jne    12e0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    132b:	sub    %rdi,%rcx
    132e:	lea    0x1(,%rdi,2),%rdi
    1336:	cs nopw 0x0(%rax,%rax,1)
    1340:	cmp    %rdi,%rsi
    1343:	jbe    135d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x11d>
    1345:	mov    (%rdx,%rdi,4),%r8d
    1349:	add    -0x4(%rdx,%rdi,4),%r8d
    134e:	mov    %r8d,-0x2(%rax,%rdi,2)
    1353:	add    $0x2,%rdi
    1357:	dec    %rcx
    135a:	jne    1340 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    135c:	ret
    135d:	ud2
    135f:	nop
