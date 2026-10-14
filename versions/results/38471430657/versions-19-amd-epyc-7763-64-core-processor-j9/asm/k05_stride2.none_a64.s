0000000000001240 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1354 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rsi),%rdx
    1257:	cmp    $0x1,%rcx
    125b:	mov    %rcx,%rdi
    125e:	adc    $0x0,%rdi
    1262:	cmp    $0x7,%rcx
    1266:	jbe    1283 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x43>
    1268:	lea    (%rax,%rdi,4),%rsi
    126c:	lea    (%rdx,%rdi,8),%r8
    1270:	cmp    %r8,%rax
    1273:	setb   %r8b
    1277:	cmp    %rsi,%rdx
    127a:	setb   %sil
    127e:	test   %sil,%r8b
    1281:	je     12e1 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa1>
    1283:	xor    %esi,%esi
    1285:	mov    %rsi,%r8
    1288:	or     $0x1,%r8
    128c:	test   $0x1,%dil
    1290:	je     12a2 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x62>
    1292:	mov    0x4(%rdx,%rsi,8),%r9d
    1297:	add    (%rdx,%rsi,8),%r9d
    129b:	mov    %r9d,(%rax,%rsi,4)
    129f:	mov    %r8,%rsi
    12a2:	cmp    %r8,%rdi
    12a5:	je     1354 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12ab:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ba:	nopw   0x0(%rax,%rax,1)
    12c0:	mov    0x4(%rdx,%rsi,8),%edi
    12c4:	add    (%rdx,%rsi,8),%edi
    12c7:	mov    %edi,(%rax,%rsi,4)
    12ca:	mov    0xc(%rdx,%rsi,8),%edi
    12ce:	add    0x8(%rdx,%rsi,8),%edi
    12d2:	mov    %edi,0x4(%rax,%rsi,4)
    12d6:	add    $0x2,%rsi
    12da:	cmp    %rsi,%rcx
    12dd:	jne    12c0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12df:	jmp    1354 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12e1:	mov    %rdi,%rsi
    12e4:	and    $0xfffffffffffffff8,%rsi
    12e8:	xor    %r8d,%r8d
    12eb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fa:	nopw   0x0(%rax,%rax,1)
    1300:	movups (%rdx,%r8,8),%xmm0
    1305:	movups 0x10(%rdx,%r8,8),%xmm1
    130b:	movups 0x20(%rdx,%r8,8),%xmm2
    1311:	movups 0x30(%rdx,%r8,8),%xmm3
    1317:	movaps %xmm0,%xmm4
    131a:	shufps $0x88,%xmm1,%xmm4
    131e:	movaps %xmm2,%xmm5
    1321:	shufps $0x88,%xmm3,%xmm5
    1325:	shufps $0xdd,%xmm1,%xmm0
    1329:	paddd  %xmm4,%xmm0
    132d:	shufps $0xdd,%xmm3,%xmm2
    1331:	paddd  %xmm5,%xmm2
    1335:	movdqu %xmm0,(%rax,%r8,4)
    133b:	movdqu %xmm2,0x10(%rax,%r8,4)
    1342:	add    $0x8,%r8
    1346:	cmp    %r8,%rsi
    1349:	jne    1300 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    134b:	cmp    %rsi,%rcx
    134e:	jne    1285 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x45>
    1354:	ret
    1355:	data16 cs nopw 0x0(%rax,%rax,1)
