0000000000001240 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	push   %rbx
    1241:	mov    (%rsi),%rax
    1244:	mov    0x8(%rsi),%rcx
    1248:	sub    %rax,%rcx
    124b:	sar    $0x2,%rcx
    124f:	cmp    $0x3,%rcx
    1253:	jb     1375 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x135>
    1259:	mov    (%rdi),%rdx
    125c:	mov    0x8(%rdi),%rsi
    1260:	sub    %rdx,%rsi
    1263:	sar    $0x2,%rsi
    1267:	cmp    $0x1,%rsi
    126b:	adc    $0x0,%rsi
    126f:	lea    -0x1(%rsi),%r11
    1273:	lea    -0x3(%rcx),%r10
    1277:	cmp    %r10,%r11
    127a:	mov    %r10,%r9
    127d:	cmovb  %r11,%r9
    1281:	mov    $0x1,%edi
    1286:	mov    $0x2,%r8d
    128c:	cmp    $0xb,%r9
    1290:	jbe    1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1296:	lea    0x4(%rdx),%rbx
    129a:	cmp    %r10,%r11
    129d:	cmovb  %r11,%r10
    12a1:	lea    (%rax,%r10,4),%r11
    12a5:	add    $0xc,%r11
    12a9:	cmp    %r11,%rbx
    12ac:	jae    12bf <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7f>
    12ae:	lea    (%rdx,%r10,4),%r10
    12b2:	add    $0x8,%r10
    12b6:	cmp    %r10,%rax
    12b9:	jb     1340 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    12bf:	inc    %r9
    12c2:	mov    %r9d,%edi
    12c5:	and    $0x7,%edi
    12c8:	mov    $0x8,%r8d
    12ce:	cmovne %rdi,%r8
    12d2:	mov    %r9,%r10
    12d5:	sub    %r8,%r10
    12d8:	neg    %r8
    12db:	add    %r9,%r8
    12de:	add    $0x2,%r8
    12e2:	lea    0x1(%r10),%rdi
    12e6:	xor    %r9d,%r9d
    12e9:	nopl   0x0(%rax)
    12f0:	movdqu (%rax,%r9,4),%xmm0
    12f6:	movdqu 0x4(%rax,%r9,4),%xmm1
    12fd:	paddd  %xmm0,%xmm1
    1301:	movdqu 0x8(%rax,%r9,4),%xmm0
    1308:	paddd  %xmm1,%xmm0
    130c:	movdqu 0x10(%rax,%r9,4),%xmm1
    1313:	movdqu 0x14(%rax,%r9,4),%xmm2
    131a:	paddd  %xmm1,%xmm2
    131e:	movdqu 0x18(%rax,%r9,4),%xmm1
    1325:	paddd  %xmm2,%xmm1
    1329:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1330:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1337:	add    $0x8,%r9
    133b:	cmp    %r9,%r10
    133e:	jne    12f0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>
    1340:	inc    %rsi
    1343:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1350:	cmp    %r8,%rsi
    1353:	je     1377 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1355:	mov    %r8,%r9
    1358:	mov    (%rax,%rdi,4),%r8d
    135c:	add    -0x4(%rax,%rdi,4),%r8d
    1361:	add    (%rax,%r9,4),%r8d
    1365:	mov    %r8d,(%rdx,%rdi,4)
    1369:	lea    0x1(%r9),%r8
    136d:	mov    %r9,%rdi
    1370:	cmp    %r8,%rcx
    1373:	jne    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    1375:	pop    %rbx
    1376:	ret
    1377:	ud2
    1379:	nopl   0x0(%rax)
