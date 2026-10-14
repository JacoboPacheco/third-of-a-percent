0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1351 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x131>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdx),%rdx
    1237:	mov    (%rdi),%rsi
    123a:	cmp    $0x1,%rcx
    123e:	mov    %rcx,%rdi
    1241:	adc    $0x0,%rdi
    1245:	cmp    $0xc,%rcx
    1249:	jb     1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    124b:	mov    %rsi,%r8
    124e:	sub    %rax,%r8
    1251:	cmp    $0x20,%r8
    1255:	setb   %r8b
    1259:	mov    %rsi,%r9
    125c:	sub    %rdx,%r9
    125f:	cmp    $0x20,%r9
    1263:	setb   %r9b
    1267:	or     %r8b,%r9b
    126a:	je     1304 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe4>
    1270:	xor    %r8d,%r8d
    1273:	mov    %rdi,%r10
    1276:	mov    %r8,%r9
    1279:	and    $0x3,%r10
    127d:	je     12a4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x84>
    127f:	mov    %r8,%r9
    1282:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	mov    (%rdx,%r9,4),%r11d
    1294:	add    (%rax,%r9,4),%r11d
    1298:	mov    %r11d,(%rsi,%r9,4)
    129c:	inc    %r9
    129f:	dec    %r10
    12a2:	jne    1290 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x70>
    12a4:	sub    %rdi,%r8
    12a7:	cmp    $0xfffffffffffffffc,%r8
    12ab:	ja     1351 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x131>
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
    1300:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa0>
    1302:	jmp    1351 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x131>
    1304:	mov    %rdi,%r8
    1307:	and    $0xfffffffffffffff8,%r8
    130b:	xor    %r9d,%r9d
    130e:	xchg   %ax,%ax
    1310:	movdqu (%rax,%r9,4),%xmm0
    1316:	movdqu 0x10(%rax,%r9,4),%xmm1
    131d:	movdqu (%rdx,%r9,4),%xmm2
    1323:	paddd  %xmm0,%xmm2
    1327:	movdqu 0x10(%rdx,%r9,4),%xmm0
    132e:	paddd  %xmm1,%xmm0
    1332:	movdqu %xmm2,(%rsi,%r9,4)
    1338:	movdqu %xmm0,0x10(%rsi,%r9,4)
    133f:	add    $0x8,%r9
    1343:	cmp    %r9,%r8
    1346:	jne    1310 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xf0>
    1348:	cmp    %r8,%rcx
    134b:	jne    1273 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x53>
    1351:	ret
    1352:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
