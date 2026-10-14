0000000000001250 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1250:	mov    (%rsi),%rax
    1253:	mov    0x8(%rsi),%rcx
    1257:	sub    %rax,%rcx
    125a:	je     1391 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1260:	sar    $0x2,%rcx
    1264:	mov    (%rdx),%rdx
    1267:	mov    (%rdi),%rsi
    126a:	cmp    $0x1,%rcx
    126e:	mov    %rcx,%rdi
    1271:	adc    $0x0,%rdi
    1275:	cmp    $0xc,%rcx
    1279:	jae    1314 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    127f:	xor    %r8d,%r8d
    1282:	mov    %rdi,%r10
    1285:	mov    %r8,%r9
    1288:	and    $0x3,%r10
    128c:	je     12b4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    128e:	mov    %r8,%r9
    1291:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a0:	mov    (%rdx,%r9,4),%r11d
    12a4:	add    (%rax,%r9,4),%r11d
    12a8:	mov    %r11d,(%rsi,%r9,4)
    12ac:	inc    %r9
    12af:	dec    %r10
    12b2:	jne    12a0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    12b4:	sub    %rdi,%r8
    12b7:	cmp    $0xfffffffffffffffc,%r8
    12bb:	ja     1391 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    12c1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12d0:	mov    (%rdx,%r9,4),%edi
    12d4:	add    (%rax,%r9,4),%edi
    12d8:	mov    %edi,(%rsi,%r9,4)
    12dc:	mov    0x4(%rdx,%r9,4),%edi
    12e1:	add    0x4(%rax,%r9,4),%edi
    12e6:	mov    %edi,0x4(%rsi,%r9,4)
    12eb:	mov    0x8(%rdx,%r9,4),%edi
    12f0:	add    0x8(%rax,%r9,4),%edi
    12f5:	mov    %edi,0x8(%rsi,%r9,4)
    12fa:	mov    0xc(%rdx,%r9,4),%edi
    12ff:	add    0xc(%rax,%r9,4),%edi
    1304:	mov    %edi,0xc(%rsi,%r9,4)
    1309:	add    $0x4,%r9
    130d:	cmp    %r9,%rcx
    1310:	jne    12d0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    1312:	jmp    1391 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1314:	mov    %rsi,%r9
    1317:	sub    %rax,%r9
    131a:	xor    %r8d,%r8d
    131d:	cmp    $0x20,%r9
    1321:	jb     1282 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1327:	mov    %rsi,%r9
    132a:	sub    %rdx,%r9
    132d:	cmp    $0x20,%r9
    1331:	jb     1282 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1337:	mov    %rdi,%r8
    133a:	and    $0xfffffffffffffff8,%r8
    133e:	xor    %r9d,%r9d
    1341:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1350:	movdqu (%rax,%r9,4),%xmm0
    1356:	movdqu 0x10(%rax,%r9,4),%xmm1
    135d:	movdqu (%rdx,%r9,4),%xmm2
    1363:	paddd  %xmm0,%xmm2
    1367:	movdqu 0x10(%rdx,%r9,4),%xmm0
    136e:	paddd  %xmm1,%xmm0
    1372:	movdqu %xmm2,(%rsi,%r9,4)
    1378:	movdqu %xmm0,0x10(%rsi,%r9,4)
    137f:	add    $0x8,%r9
    1383:	cmp    %r9,%r8
    1386:	jne    1350 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1388:	cmp    %r8,%rdi
    138b:	jne    1282 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1391:	ret
    1392:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
