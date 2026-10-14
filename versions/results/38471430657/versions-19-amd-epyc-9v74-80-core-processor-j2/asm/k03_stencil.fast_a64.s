0000000000001240 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	push   %rbx
    1241:	mov    (%rsi),%rax
    1244:	mov    0x8(%rsi),%rcx
    1248:	sub    %rax,%rcx
    124b:	sar    $0x2,%rcx
    124f:	cmp    $0x3,%rcx
    1253:	jb     13a5 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x165>
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
    1290:	jbe    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    1296:	cmp    %r10,%r11
    1299:	cmovb  %r11,%r10
    129d:	lea    0x4(%rdx),%r11
    12a1:	lea    (%rdx,%r10,4),%rbx
    12a5:	add    $0x8,%rbx
    12a9:	lea    (%rax,%r10,4),%r10
    12ad:	add    $0xc,%r10
    12b1:	cmp    %r10,%r11
    12b4:	setb   %r10b
    12b8:	cmp    %rbx,%rax
    12bb:	setb   %r11b
    12bf:	test   %r11b,%r10b
    12c2:	jne    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>
    12c8:	inc    %r9
    12cb:	mov    %r9d,%edi
    12ce:	and    $0x7,%edi
    12d1:	mov    $0x8,%r8d
    12d7:	cmovne %rdi,%r8
    12db:	mov    %r9,%r10
    12de:	sub    %r8,%r10
    12e1:	neg    %r8
    12e4:	add    %r9,%r8
    12e7:	add    $0x2,%r8
    12eb:	lea    0x1(%r10),%rdi
    12ef:	xor    %r9d,%r9d
    12f2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	movdqu (%rax,%r9,4),%xmm0
    1306:	movdqu 0x4(%rax,%r9,4),%xmm1
    130d:	paddd  %xmm0,%xmm1
    1311:	movdqu 0x8(%rax,%r9,4),%xmm0
    1318:	paddd  %xmm1,%xmm0
    131c:	movdqu 0x10(%rax,%r9,4),%xmm1
    1323:	movdqu 0x14(%rax,%r9,4),%xmm2
    132a:	paddd  %xmm1,%xmm2
    132e:	movdqu 0x18(%rax,%r9,4),%xmm1
    1335:	paddd  %xmm2,%xmm1
    1339:	movdqu %xmm0,0x4(%rdx,%r9,4)
    1340:	movdqu %xmm1,0x14(%rdx,%r9,4)
    1347:	add    $0x8,%r9
    134b:	cmp    %r9,%r10
    134e:	jne    1300 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1350:	inc    %rsi
    1353:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1362:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1371:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	cmp    %r8,%rsi
    1383:	je     13a7 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x167>
    1385:	mov    %r8,%r9
    1388:	mov    (%rax,%rdi,4),%r8d
    138c:	add    -0x4(%rax,%rdi,4),%r8d
    1391:	add    (%rax,%r9,4),%r8d
    1395:	mov    %r8d,(%rdx,%rdi,4)
    1399:	lea    0x1(%r9),%r8
    139d:	mov    %r9,%rdi
    13a0:	cmp    %r8,%rcx
    13a3:	jne    1380 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13a5:	pop    %rbx
    13a6:	ret
    13a7:	ud2
    13a9:	nopl   0x0(%rax)
