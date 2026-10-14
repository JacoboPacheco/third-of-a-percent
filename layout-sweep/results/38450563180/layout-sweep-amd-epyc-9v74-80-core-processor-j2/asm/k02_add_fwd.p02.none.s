0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1381 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdx),%rdx
    1257:	mov    (%rdi),%rsi
    125a:	cmp    $0x1,%rcx
    125e:	mov    %rcx,%rdi
    1261:	adc    $0x0,%rdi
    1265:	cmp    $0xc,%rcx
    1269:	jae    1304 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    126f:	xor    %r8d,%r8d
    1272:	mov    %rdi,%r10
    1275:	mov    %r8,%r9
    1278:	and    $0x3,%r10
    127c:	je     12a4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    127e:	mov    %r8,%r9
    1281:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	mov    (%rdx,%r9,4),%r11d
    1294:	add    (%rax,%r9,4),%r11d
    1298:	mov    %r11d,(%rsi,%r9,4)
    129c:	inc    %r9
    129f:	dec    %r10
    12a2:	jne    1290 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    12a4:	sub    %rdi,%r8
    12a7:	cmp    $0xfffffffffffffffc,%r8
    12ab:	ja     1381 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    12b1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    (%rdx,%r9,4),%edi
    12c4:	add    (%rax,%r9,4),%edi
    12c8:	mov    %edi,(%rsi,%r9,4)
    12cc:	mov    0x4(%rdx,%r9,4),%edi
    12d1:	add    0x4(%rax,%r9,4),%edi
    12d6:	mov    %edi,0x4(%rsi,%r9,4)
    12db:	mov    0x8(%rdx,%r9,4),%edi
    12e0:	add    0x8(%rax,%r9,4),%edi
    12e5:	mov    %edi,0x8(%rsi,%r9,4)
    12ea:	mov    0xc(%rdx,%r9,4),%edi
    12ef:	add    0xc(%rax,%r9,4),%edi
    12f4:	mov    %edi,0xc(%rsi,%r9,4)
    12f9:	add    $0x4,%r9
    12fd:	cmp    %r9,%rcx
    1300:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    1302:	jmp    1381 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1304:	mov    %rsi,%r9
    1307:	sub    %rax,%r9
    130a:	xor    %r8d,%r8d
    130d:	cmp    $0x20,%r9
    1311:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1317:	mov    %rsi,%r9
    131a:	sub    %rdx,%r9
    131d:	cmp    $0x20,%r9
    1321:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1327:	mov    %rdi,%r8
    132a:	and    $0xfffffffffffffff8,%r8
    132e:	xor    %r9d,%r9d
    1331:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	movdqu (%rax,%r9,4),%xmm0
    1346:	movdqu 0x10(%rax,%r9,4),%xmm1
    134d:	movdqu (%rdx,%r9,4),%xmm2
    1353:	paddd  %xmm0,%xmm2
    1357:	movdqu 0x10(%rdx,%r9,4),%xmm0
    135e:	paddd  %xmm1,%xmm0
    1362:	movdqu %xmm2,(%rsi,%r9,4)
    1368:	movdqu %xmm0,0x10(%rsi,%r9,4)
    136f:	add    $0x8,%r9
    1373:	cmp    %r9,%r8
    1376:	jne    1340 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1378:	cmp    %r8,%rdi
    137b:	jne    1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1381:	ret
    1382:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
