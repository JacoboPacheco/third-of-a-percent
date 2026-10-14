0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%r8
    1243:	mov    0x8(%rsi),%rax
    1247:	sub    %r8,%rax
    124a:	je     139e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x15e>
    1250:	sar    $0x2,%rax
    1254:	mov    (%rdx),%rsi
    1257:	mov    0x8(%rdx),%rcx
    125b:	sub    %rsi,%rcx
    125e:	sar    $0x2,%rcx
    1262:	mov    (%rdi),%r9
    1265:	mov    0x8(%rdi),%rdx
    1269:	sub    %r9,%rdx
    126c:	sar    $0x2,%rdx
    1270:	cmp    $0x1,%rax
    1274:	adc    $0x0,%rax
    1278:	lea    -0x1(%rax),%r10
    127c:	cmp    %rdx,%r10
    127f:	cmovae %rdx,%r10
    1283:	cmp    %rcx,%r10
    1286:	cmovae %rcx,%r10
    128a:	cmp    $0xf,%r10
    128e:	ja     1297 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x57>
    1290:	xor    %edi,%edi
    1292:	jmp    1330 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xf0>
    1297:	mov    %r9,%r11
    129a:	sub    %r8,%r11
    129d:	xor    %edi,%edi
    129f:	cmp    $0x40,%r11
    12a3:	jb     1330 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xf0>
    12a9:	mov    %r9,%r11
    12ac:	sub    %rsi,%r11
    12af:	cmp    $0x40,%r11
    12b3:	jb     1330 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xf0>
    12b9:	inc    %r10
    12bc:	mov    %r10d,%edi
    12bf:	and    $0xf,%edi
    12c2:	mov    $0x10,%r11d
    12c8:	cmovne %rdi,%r11
    12cc:	mov    %r10,%rdi
    12cf:	sub    %r11,%rdi
    12d2:	xor    %r10d,%r10d
    12d5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e4:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	vmovdqu (%rsi,%r10,4),%ymm0
    1306:	vmovdqu 0x20(%rsi,%r10,4),%ymm1
    130d:	vpaddd (%r8,%r10,4),%ymm0,%ymm0
    1313:	vpaddd 0x20(%r8,%r10,4),%ymm1,%ymm1
    131a:	vmovdqu %ymm0,(%r9,%r10,4)
    1320:	vmovdqu %ymm1,0x20(%r9,%r10,4)
    1327:	add    $0x10,%r10
    132b:	cmp    %r10,%rdi
    132e:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1330:	sub    %rdi,%rdx
    1333:	sub    %rdi,%rcx
    1336:	sub    %rdi,%rax
    1339:	lea    (%r8,%rdi,4),%r8
    133d:	lea    (%rsi,%rdi,4),%rsi
    1341:	lea    (%r9,%rdi,4),%rdi
    1345:	xor    %r9d,%r9d
    1348:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1357:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1366:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1375:	data16 cs nopw 0x0(%rax,%rax,1)
    1380:	cmp    %r9,%rcx
    1383:	je     13a2 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x162>
    1385:	cmp    %r9,%rdx
    1388:	je     13a2 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x162>
    138a:	mov    (%rsi,%r9,4),%r10d
    138e:	add    (%r8,%r9,4),%r10d
    1392:	mov    %r10d,(%rdi,%r9,4)
    1396:	inc    %r9
    1399:	cmp    %r9,%rax
    139c:	jne    1380 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>
    139e:	vzeroupper
    13a1:	ret
    13a2:	ud2
    13a4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
