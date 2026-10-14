0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rdi
    1247:	mov    %rdi,%r8
    124a:	sub    %rax,%r8
    124d:	mov    %r8,%rcx
    1250:	sar    $0x2,%rcx
    1254:	js     133d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfd>
    125a:	mov    (%rsi),%rdx
    125d:	mov    0x8(%rsi),%r9
    1261:	sub    %rdx,%r9
    1264:	sar    $0x2,%r9
    1268:	mov    %r8,%rsi
    126b:	shr    $1,%rsi
    126e:	cmp    %rsi,%r9
    1271:	jb     133d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfd>
    1277:	cmp    %rax,%rdi
    127a:	je     133c <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfc>
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
    12c3:	jmp    1309 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc9>
    12c5:	inc    %rdi
    12c8:	mov    %edi,%r8d
    12cb:	and    $0x3,%r8d
    12cf:	mov    $0x4,%r9d
    12d5:	cmovne %r8,%r9
    12d9:	sub    %r9,%rdi
    12dc:	xor    %r8d,%r8d
    12df:	nop
    12e0:	movups (%rdx,%r8,8),%xmm0
    12e5:	movups 0x10(%rdx,%r8,8),%xmm1
    12eb:	movaps %xmm0,%xmm2
    12ee:	shufps $0x88,%xmm1,%xmm2
    12f2:	shufps $0xdd,%xmm1,%xmm0
    12f6:	paddd  %xmm2,%xmm0
    12fa:	movdqu %xmm0,(%rax,%r8,4)
    1300:	add    $0x4,%r8
    1304:	cmp    %r8,%rdi
    1307:	jne    12e0 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    1309:	sub    %rdi,%rcx
    130c:	lea    0x1(,%rdi,2),%rdi
    1314:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1320:	cmp    %rdi,%rsi
    1323:	jbe    133d <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfd>
    1325:	mov    (%rdx,%rdi,4),%r8d
    1329:	add    -0x4(%rdx,%rdi,4),%r8d
    132e:	mov    %r8d,-0x2(%rax,%rdi,2)
    1333:	add    $0x2,%rdi
    1337:	dec    %rcx
    133a:	jne    1320 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe0>
    133c:	ret
    133d:	ud2
    133f:	nop
