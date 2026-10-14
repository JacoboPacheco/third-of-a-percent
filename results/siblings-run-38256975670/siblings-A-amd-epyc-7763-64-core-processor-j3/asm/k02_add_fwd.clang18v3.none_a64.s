0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1423 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1e3>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdx),%rdx
    1257:	mov    (%rdi),%rsi
    125a:	cmp    $0x1,%rcx
    125e:	mov    %rcx,%rdi
    1261:	adc    $0x0,%rdi
    1265:	cmp    $0x20,%rcx
    1269:	jae    1383 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x143>
    126f:	xor    %r8d,%r8d
    1272:	mov    %rdi,%r10
    1275:	mov    %r8,%r9
    1278:	and    $0x7,%r10
    127c:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>
    127e:	mov    %r8,%r9
    1281:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    129f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ae:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bd:	nopl   (%rax)
    12c0:	mov    (%rdx,%r9,4),%r11d
    12c4:	add    (%rax,%r9,4),%r11d
    12c8:	mov    %r11d,(%rsi,%r9,4)
    12cc:	inc    %r9
    12cf:	dec    %r10
    12d2:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12d4:	sub    %rdi,%r8
    12d7:	cmp    $0xfffffffffffffff8,%r8
    12db:	ja     1423 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1e3>
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	mov    (%rdx,%r9,4),%edi
    1304:	add    (%rax,%r9,4),%edi
    1308:	mov    %edi,(%rsi,%r9,4)
    130c:	mov    0x4(%rdx,%r9,4),%edi
    1311:	add    0x4(%rax,%r9,4),%edi
    1316:	mov    %edi,0x4(%rsi,%r9,4)
    131b:	mov    0x8(%rdx,%r9,4),%edi
    1320:	add    0x8(%rax,%r9,4),%edi
    1325:	mov    %edi,0x8(%rsi,%r9,4)
    132a:	mov    0xc(%rdx,%r9,4),%edi
    132f:	add    0xc(%rax,%r9,4),%edi
    1334:	mov    %edi,0xc(%rsi,%r9,4)
    1339:	mov    0x10(%rdx,%r9,4),%edi
    133e:	add    0x10(%rax,%r9,4),%edi
    1343:	mov    %edi,0x10(%rsi,%r9,4)
    1348:	mov    0x14(%rdx,%r9,4),%edi
    134d:	add    0x14(%rax,%r9,4),%edi
    1352:	mov    %edi,0x14(%rsi,%r9,4)
    1357:	mov    0x18(%rdx,%r9,4),%edi
    135c:	add    0x18(%rax,%r9,4),%edi
    1361:	mov    %edi,0x18(%rsi,%r9,4)
    1366:	mov    0x1c(%rdx,%r9,4),%edi
    136b:	add    0x1c(%rax,%r9,4),%edi
    1370:	mov    %edi,0x1c(%rsi,%r9,4)
    1375:	add    $0x8,%r9
    1379:	cmp    %r9,%rcx
    137c:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    137e:	jmp    1423 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1e3>
    1383:	mov    %rsi,%r9
    1386:	sub    %rax,%r9
    1389:	xor    %r8d,%r8d
    138c:	cmp    $0x80,%r9
    1393:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1399:	mov    %rsi,%r9
    139c:	sub    %rdx,%r9
    139f:	cmp    $0x80,%r9
    13a6:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    13ac:	mov    %rdi,%r8
    13af:	and    $0xffffffffffffffe0,%r8
    13b3:	xor    %r9d,%r9d
    13b6:	cs nopw 0x0(%rax,%rax,1)
    13c0:	vmovdqu (%rdx,%r9,4),%ymm0
    13c6:	vmovdqu 0x20(%rdx,%r9,4),%ymm1
    13cd:	vmovdqu 0x40(%rdx,%r9,4),%ymm2
    13d4:	vmovdqu 0x60(%rdx,%r9,4),%ymm3
    13db:	vpaddd (%rax,%r9,4),%ymm0,%ymm0
    13e1:	vpaddd 0x20(%rax,%r9,4),%ymm1,%ymm1
    13e8:	vpaddd 0x40(%rax,%r9,4),%ymm2,%ymm2
    13ef:	vpaddd 0x60(%rax,%r9,4),%ymm3,%ymm3
    13f6:	vmovdqu %ymm0,(%rsi,%r9,4)
    13fc:	vmovdqu %ymm1,0x20(%rsi,%r9,4)
    1403:	vmovdqu %ymm2,0x40(%rsi,%r9,4)
    140a:	vmovdqu %ymm3,0x60(%rsi,%r9,4)
    1411:	add    $0x20,%r9
    1415:	cmp    %r9,%r8
    1418:	jne    13c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x180>
    141a:	cmp    %r8,%rdi
    141d:	jne    1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1423:	vzeroupper
    1426:	ret
    1427:	nopw   0x0(%rax,%rax,1)
