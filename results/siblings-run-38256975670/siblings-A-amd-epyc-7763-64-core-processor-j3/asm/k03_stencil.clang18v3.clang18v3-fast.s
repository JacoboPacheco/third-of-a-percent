0000000000001220 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	push   %rbx
    1221:	mov    (%rsi),%rax
    1224:	mov    0x8(%rsi),%rcx
    1228:	sub    %rax,%rcx
    122b:	sar    $0x2,%rcx
    122f:	cmp    $0x3,%rcx
    1233:	jb     1375 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x155>
    1239:	mov    (%rdi),%rdx
    123c:	mov    0x8(%rdi),%rsi
    1240:	sub    %rdx,%rsi
    1243:	sar    $0x2,%rsi
    1247:	cmp    $0x1,%rsi
    124b:	adc    $0x0,%rsi
    124f:	lea    -0x1(%rsi),%r11
    1253:	lea    -0x3(%rcx),%r10
    1257:	cmp    %r10,%r11
    125a:	mov    %r10,%r9
    125d:	cmovb  %r11,%r9
    1261:	mov    $0x1,%edi
    1266:	mov    $0x2,%r8d
    126c:	cmp    $0x1f,%r9
    1270:	jbe    1348 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x128>
    1276:	lea    0x4(%rdx),%rbx
    127a:	cmp    %r10,%r11
    127d:	cmovb  %r11,%r10
    1281:	lea    (%rax,%r10,4),%r11
    1285:	add    $0xc,%r11
    1289:	cmp    %r11,%rbx
    128c:	jae    129f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7f>
    128e:	lea    (%rdx,%r10,4),%r10
    1292:	add    $0x8,%r10
    1296:	cmp    %r10,%rax
    1299:	jb     1348 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x128>
    129f:	inc    %r9
    12a2:	mov    %r9d,%edi
    12a5:	and    $0x1f,%edi
    12a8:	mov    $0x20,%r8d
    12ae:	cmovne %rdi,%r8
    12b2:	mov    %r9,%r10
    12b5:	sub    %r8,%r10
    12b8:	neg    %r8
    12bb:	add    %r9,%r8
    12be:	add    $0x2,%r8
    12c2:	lea    0x1(%r10),%rdi
    12c6:	xor    %r9d,%r9d
    12c9:	nopl   0x0(%rax)
    12d0:	vmovdqu 0x4(%rax,%r9,4),%ymm0
    12d7:	vmovdqu 0x24(%rax,%r9,4),%ymm1
    12de:	vmovdqu 0x44(%rax,%r9,4),%ymm2
    12e5:	vmovdqu 0x64(%rax,%r9,4),%ymm3
    12ec:	vpaddd (%rax,%r9,4),%ymm0,%ymm0
    12f2:	vpaddd 0x20(%rax,%r9,4),%ymm1,%ymm1
    12f9:	vpaddd 0x40(%rax,%r9,4),%ymm2,%ymm2
    1300:	vpaddd 0x60(%rax,%r9,4),%ymm3,%ymm3
    1307:	vpaddd 0x8(%rax,%r9,4),%ymm0,%ymm0
    130e:	vpaddd 0x28(%rax,%r9,4),%ymm1,%ymm1
    1315:	vpaddd 0x48(%rax,%r9,4),%ymm2,%ymm2
    131c:	vpaddd 0x68(%rax,%r9,4),%ymm3,%ymm3
    1323:	vmovdqu %ymm0,0x4(%rdx,%r9,4)
    132a:	vmovdqu %ymm1,0x24(%rdx,%r9,4)
    1331:	vmovdqu %ymm2,0x44(%rdx,%r9,4)
    1338:	vmovdqu %ymm3,0x64(%rdx,%r9,4)
    133f:	add    $0x20,%r9
    1343:	cmp    %r9,%r10
    1346:	jne    12d0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb0>
    1348:	inc    %rsi
    134b:	nopl   0x0(%rax,%rax,1)
    1350:	cmp    %r8,%rsi
    1353:	je     137a <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x15a>
    1355:	mov    %r8,%r9
    1358:	mov    (%rax,%rdi,4),%r8d
    135c:	add    -0x4(%rax,%rdi,4),%r8d
    1361:	add    (%rax,%r9,4),%r8d
    1365:	mov    %r8d,(%rdx,%rdi,4)
    1369:	lea    0x1(%r9),%r8
    136d:	mov    %r9,%rdi
    1370:	cmp    %r8,%rcx
    1373:	jne    1350 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x130>
    1375:	pop    %rbx
    1376:	vzeroupper
    1379:	ret
    137a:	ud2
    137c:	nopl   0x0(%rax)
