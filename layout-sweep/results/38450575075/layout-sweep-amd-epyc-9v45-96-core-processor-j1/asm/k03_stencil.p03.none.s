0000000000001250 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	mov    (%rsi),%rax
    1253:	mov    0x8(%rsi),%r10
    1257:	mov    %r10,%r9
    125a:	sub    %rax,%r9
    125d:	mov    %r9,%rcx
    1260:	sar    $0x2,%rcx
    1264:	cmp    $0x3,%rcx
    1268:	jb     1387 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    126e:	mov    (%rdi),%rdx
    1271:	lea    -0x2(%rcx),%r8
    1275:	mov    $0x1,%edi
    127a:	mov    $0x2,%esi
    127f:	cmp    $0x8,%r8
    1283:	jb     1309 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    1289:	lea    0x4(%rdx),%r11
    128d:	cmp    %r10,%r11
    1290:	jae    129e <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    1292:	add    %rdx,%r9
    1295:	add    $0xfffffffffffffffc,%r9
    1299:	cmp    %r9,%rax
    129c:	jb     1309 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    129e:	mov    %r8,%r9
    12a1:	and    $0xfffffffffffffff8,%r9
    12a5:	lea    0x2(%r9),%rsi
    12a9:	lea    0x1(%r9),%rdi
    12ad:	xor    %r10d,%r10d
    12b0:	movdqu (%rax,%r10,4),%xmm0
    12b6:	movdqu 0x4(%rax,%r10,4),%xmm1
    12bd:	paddd  %xmm0,%xmm1
    12c1:	movdqu 0x8(%rax,%r10,4),%xmm0
    12c8:	paddd  %xmm1,%xmm0
    12cc:	movdqu 0x10(%rax,%r10,4),%xmm1
    12d3:	movdqu 0x14(%rax,%r10,4),%xmm2
    12da:	paddd  %xmm1,%xmm2
    12de:	movdqu 0x18(%rax,%r10,4),%xmm1
    12e5:	paddd  %xmm2,%xmm1
    12e9:	movdqu %xmm0,0x4(%rdx,%r10,4)
    12f0:	movdqu %xmm1,0x14(%rdx,%r10,4)
    12f7:	add    $0x8,%r10
    12fb:	cmp    %r10,%r9
    12fe:	jne    12b0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    1300:	cmp    %r9,%r8
    1303:	je     1387 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1309:	mov    %ecx,%r8d
    130c:	sub    %esi,%r8d
    130f:	lea    0x1(%rsi),%r9
    1313:	test   $0x1,%r8b
    1317:	jne    1326 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd6>
    1319:	mov    %rsi,%r8
    131c:	mov    %rdi,%rsi
    131f:	cmp    %r9,%rcx
    1322:	jne    133f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xef>
    1324:	jmp    1387 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1326:	mov    (%rax,%rdi,4),%r8d
    132a:	add    -0x4(%rax,%rdi,4),%r8d
    132f:	add    (%rax,%rsi,4),%r8d
    1333:	mov    %r8d,(%rdx,%rdi,4)
    1337:	mov    %r9,%r8
    133a:	cmp    %r9,%rcx
    133d:	je     1387 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    133f:	neg    %rcx
    1342:	inc    %r8
    1345:	data16 cs nopw 0x0(%rax,%rax,1)
    1350:	mov    (%rax,%rsi,4),%edi
    1353:	add    -0x4(%rax,%rsi,4),%edi
    1357:	add    -0x4(%rax,%r8,4),%edi
    135c:	mov    %edi,(%rdx,%rsi,4)
    135f:	mov    -0x4(%rax,%r8,4),%esi
    1364:	add    -0x8(%rax,%r8,4),%esi
    1369:	add    (%rax,%r8,4),%esi
    136d:	mov    %esi,-0x4(%rdx,%r8,4)
    1372:	lea    (%rcx,%r8,1),%rdi
    1376:	add    $0x2,%rdi
    137a:	mov    %r8,%rsi
    137d:	add    $0x2,%r8
    1381:	cmp    $0x1,%rdi
    1385:	jne    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1387:	ret
    1388:	nopl   0x0(%rax,%rax,1)
