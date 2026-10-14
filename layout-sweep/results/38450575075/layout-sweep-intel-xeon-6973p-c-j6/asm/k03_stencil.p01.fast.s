0000000000001230 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1230:	push   %rbx
    1231:	mov    (%rsi),%rax
    1234:	mov    0x8(%rsi),%rcx
    1238:	sub    %rax,%rcx
    123b:	sar    $0x2,%rcx
    123f:	cmp    $0x3,%rcx
    1243:	jb     1365 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x135>
    1249:	mov    (%rdi),%rdx
    124c:	mov    0x8(%rdi),%rsi
    1250:	sub    %rdx,%rsi
    1253:	sar    $0x2,%rsi
    1257:	cmp    $0x1,%rsi
    125b:	adc    $0x0,%rsi
    125f:	lea    -0x1(%rsi),%r11
    1263:	lea    -0x3(%rcx),%r10
    1267:	cmp    %r10,%r11
    126a:	mov    %r10,%r9
    126d:	cmovb  %r11,%r9
    1271:	mov    $0x1,%edi
    1276:	mov    $0x2,%r8d
    127c:	cmp    $0xb,%r9
    1280:	jbe    1330 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1286:	lea    0x4(%rdx),%rbx
    128a:	cmp    %r10,%r11
    128d:	cmovb  %r11,%r10
    1291:	lea    (%rax,%r10,4),%r11
    1295:	add    $0xc,%r11
    1299:	cmp    %r11,%rbx
    129c:	jae    12af <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7f>
    129e:	lea    (%rdx,%r10,4),%r10
    12a2:	add    $0x8,%r10
    12a6:	cmp    %r10,%rax
    12a9:	jb     1330 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    12af:	inc    %r9
    12b2:	mov    %r9d,%edi
    12b5:	and    $0x7,%edi
    12b8:	mov    $0x8,%r8d
    12be:	cmovne %rdi,%r8
    12c2:	mov    %r9,%r10
    12c5:	sub    %r8,%r10
    12c8:	neg    %r8
    12cb:	add    %r9,%r8
    12ce:	add    $0x2,%r8
    12d2:	lea    0x1(%r10),%rdi
    12d6:	xor    %r9d,%r9d
    12d9:	nopl   0x0(%rax)
    12e0:	movdqu (%rax,%r9,4),%xmm0
    12e6:	movdqu 0x4(%rax,%r9,4),%xmm1
    12ed:	paddd  %xmm0,%xmm1
    12f1:	movdqu 0x8(%rax,%r9,4),%xmm0
    12f8:	paddd  %xmm1,%xmm0
    12fc:	movdqu 0x10(%rax,%r9,4),%xmm1
    1303:	movdqu 0x14(%rax,%r9,4),%xmm2
    130a:	paddd  %xmm1,%xmm2
    130e:	movdqu 0x18(%rax,%r9,4),%xmm1
    1315:	paddd  %xmm2,%xmm1
    1319:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1320:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1327:	add    $0x8,%r9
    132b:	cmp    %r9,%r10
    132e:	jne    12e0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>
    1330:	inc    %rsi
    1333:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	cmp    %r8,%rsi
    1343:	je     1367 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1345:	mov    %r8,%r9
    1348:	mov    (%rax,%rdi,4),%r8d
    134c:	add    -0x4(%rax,%rdi,4),%r8d
    1351:	add    (%rax,%r9,4),%r8d
    1355:	mov    %r8d,(%rdx,%rdi,4)
    1359:	lea    0x1(%r9),%r8
    135d:	mov    %r9,%rdi
    1360:	cmp    %r8,%rcx
    1363:	jne    1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    1365:	pop    %rbx
    1366:	ret
    1367:	ud2
    1369:	nopl   0x0(%rax)
