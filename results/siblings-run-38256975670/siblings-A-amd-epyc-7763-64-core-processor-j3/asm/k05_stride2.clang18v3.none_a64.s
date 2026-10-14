0000000000001240 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1408 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1c8>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rsi),%rdx
    1257:	cmp    $0x1,%rcx
    125b:	mov    %rcx,%rsi
    125e:	adc    $0x0,%rsi
    1262:	cmp    $0x20,%rcx
    1266:	jb     1282 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x42>
    1268:	lea    (%rdx,%rsi,8),%rdi
    126c:	cmp    %rdi,%rax
    126f:	jae    1348 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x108>
    1275:	lea    (%rax,%rsi,4),%rdi
    1279:	cmp    %rdi,%rdx
    127c:	jae    1348 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x108>
    1282:	xor    %edi,%edi
    1284:	mov    %rsi,%r9
    1287:	mov    %rdi,%r8
    128a:	and    $0x3,%r9
    128e:	je     12d5 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x95>
    1290:	mov    %rdi,%r8
    1293:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    0x4(%rdx,%r8,8),%r10d
    12c5:	add    (%rdx,%r8,8),%r10d
    12c9:	mov    %r10d,(%rax,%r8,4)
    12cd:	inc    %r8
    12d0:	dec    %r9
    12d3:	jne    12c0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12d5:	sub    %rsi,%rdi
    12d8:	cmp    $0xfffffffffffffffc,%rdi
    12dc:	ja     1408 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1c8>
    12e2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	mov    0x4(%rdx,%r8,8),%esi
    1305:	add    (%rdx,%r8,8),%esi
    1309:	mov    %esi,(%rax,%r8,4)
    130d:	mov    0xc(%rdx,%r8,8),%esi
    1312:	add    0x8(%rdx,%r8,8),%esi
    1317:	mov    %esi,0x4(%rax,%r8,4)
    131c:	mov    0x14(%rdx,%r8,8),%esi
    1321:	add    0x10(%rdx,%r8,8),%esi
    1326:	mov    %esi,0x8(%rax,%r8,4)
    132b:	mov    0x1c(%rdx,%r8,8),%esi
    1330:	add    0x18(%rdx,%r8,8),%esi
    1335:	mov    %esi,0xc(%rax,%r8,4)
    133a:	add    $0x4,%r8
    133e:	cmp    %r8,%rcx
    1341:	jne    1300 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1343:	jmp    1408 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x1c8>
    1348:	mov    %rsi,%rdi
    134b:	and    $0xffffffffffffffe0,%rdi
    134f:	xor    %r8d,%r8d
    1352:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1361:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1370:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137f:	nop
    1380:	vmovdqu (%rdx,%r8,8),%ymm0
    1386:	vmovdqu 0x40(%rdx,%r8,8),%ymm1
    138d:	vphaddd 0x20(%rdx,%r8,8),%ymm0,%ymm0
    1394:	vphaddd 0x60(%rdx,%r8,8),%ymm1,%ymm1
    139b:	vmovdqu 0x80(%rdx,%r8,8),%ymm2
    13a5:	vmovdqu 0xc0(%rdx,%r8,8),%ymm3
    13af:	vpermq $0xd8,%ymm0,%ymm0
    13b5:	vpermq $0xd8,%ymm1,%ymm1
    13bb:	vphaddd 0xa0(%rdx,%r8,8),%ymm2,%ymm2
    13c5:	vphaddd 0xe0(%rdx,%r8,8),%ymm3,%ymm3
    13cf:	vpermq $0xd8,%ymm2,%ymm2
    13d5:	vpermq $0xd8,%ymm3,%ymm3
    13db:	vmovdqu %ymm0,(%rax,%r8,4)
    13e1:	vmovdqu %ymm1,0x20(%rax,%r8,4)
    13e8:	vmovdqu %ymm2,0x40(%rax,%r8,4)
    13ef:	vmovdqu %ymm3,0x60(%rax,%r8,4)
    13f6:	add    $0x20,%r8
    13fa:	cmp    %r8,%rdi
    13fd:	jne    1380 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>
    13ff:	cmp    %rdi,%rsi
    1402:	jne    1284 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x44>
    1408:	vzeroupper
    140b:	ret
    140c:	nopl   0x0(%rax)
