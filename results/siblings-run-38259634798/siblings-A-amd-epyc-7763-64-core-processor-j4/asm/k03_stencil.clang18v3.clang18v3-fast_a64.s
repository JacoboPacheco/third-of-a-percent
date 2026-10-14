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
    128c:	cmp    $0x1f,%r9
    1290:	jbe    1378 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x138>
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
    12b9:	jb     1378 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x138>
    12bf:	inc    %r9
    12c2:	mov    %r9d,%edi
    12c5:	and    $0x1f,%edi
    12c8:	mov    $0x20,%r8d
    12ce:	cmovne %rdi,%r8
    12d2:	mov    %r9,%r10
    12d5:	sub    %r8,%r10
    12d8:	neg    %r8
    12db:	add    %r9,%r8
    12de:	add    $0x2,%r8
    12e2:	lea    0x1(%r10),%rdi
    12e6:	xor    %r9d,%r9d
    12e9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f8:	nopl   0x0(%rax,%rax,1)
    1300:	vmovdqu 0x4(%rax,%r9,4),%ymm0
    1307:	vmovdqu 0x24(%rax,%r9,4),%ymm1
    130e:	vmovdqu 0x44(%rax,%r9,4),%ymm2
    1315:	vmovdqu 0x64(%rax,%r9,4),%ymm3
    131c:	vpaddd (%rax,%r9,4),%ymm0,%ymm0
    1322:	vpaddd 0x20(%rax,%r9,4),%ymm1,%ymm1
    1329:	vpaddd 0x40(%rax,%r9,4),%ymm2,%ymm2
    1330:	vpaddd 0x60(%rax,%r9,4),%ymm3,%ymm3
    1337:	vpaddd 0x8(%rax,%r9,4),%ymm0,%ymm0
    133e:	vpaddd 0x28(%rax,%r9,4),%ymm1,%ymm1
    1345:	vpaddd 0x48(%rax,%r9,4),%ymm2,%ymm2
    134c:	vpaddd 0x68(%rax,%r9,4),%ymm3,%ymm3
    1353:	vmovdqu %ymm0,0x4(%rdx,%r9,4)
    135a:	vmovdqu %ymm1,0x24(%rdx,%r9,4)
    1361:	vmovdqu %ymm2,0x44(%rdx,%r9,4)
    1368:	vmovdqu %ymm3,0x64(%rdx,%r9,4)
    136f:	add    $0x20,%r9
    1373:	cmp    %r9,%r10
    1376:	jne    1300 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1378:	inc    %rsi
    137b:	nopl   0x0(%rax,%rax,1)
    1380:	cmp    %r8,%rsi
    1383:	je     13aa <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x16a>
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
    13a6:	vzeroupper
    13a9:	ret
    13aa:	ud2
    13ac:	nopl   0x0(%rax)
