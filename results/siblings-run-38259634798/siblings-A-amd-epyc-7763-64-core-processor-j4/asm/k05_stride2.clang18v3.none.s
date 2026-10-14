0000000000001220 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rdi),%rax
    1223:	mov    0x8(%rdi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1398 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x178>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rsi),%rdx
    1237:	cmp    $0x1,%rcx
    123b:	mov    %rcx,%rsi
    123e:	adc    $0x0,%rsi
    1242:	cmp    $0x20,%rcx
    1246:	jb     1262 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x42>
    1248:	lea    (%rdx,%rsi,8),%rdi
    124c:	cmp    %rdi,%rax
    124f:	jae    12f8 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>
    1255:	lea    (%rax,%rsi,4),%rdi
    1259:	cmp    %rdi,%rdx
    125c:	jae    12f8 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>
    1262:	xor    %edi,%edi
    1264:	mov    %rsi,%r9
    1267:	mov    %rdi,%r8
    126a:	and    $0x3,%r9
    126e:	je     1295 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x75>
    1270:	mov    %rdi,%r8
    1273:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1280:	mov    0x4(%rdx,%r8,8),%r10d
    1285:	add    (%rdx,%r8,8),%r10d
    1289:	mov    %r10d,(%rax,%r8,4)
    128d:	inc    %r8
    1290:	dec    %r9
    1293:	jne    1280 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    1295:	sub    %rsi,%rdi
    1298:	cmp    $0xfffffffffffffffc,%rdi
    129c:	ja     1398 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x178>
    12a2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	mov    0x4(%rdx,%r8,8),%esi
    12b5:	add    (%rdx,%r8,8),%esi
    12b9:	mov    %esi,(%rax,%r8,4)
    12bd:	mov    0xc(%rdx,%r8,8),%esi
    12c2:	add    0x8(%rdx,%r8,8),%esi
    12c7:	mov    %esi,0x4(%rax,%r8,4)
    12cc:	mov    0x14(%rdx,%r8,8),%esi
    12d1:	add    0x10(%rdx,%r8,8),%esi
    12d6:	mov    %esi,0x8(%rax,%r8,4)
    12db:	mov    0x1c(%rdx,%r8,8),%esi
    12e0:	add    0x18(%rdx,%r8,8),%esi
    12e5:	mov    %esi,0xc(%rax,%r8,4)
    12ea:	add    $0x4,%r8
    12ee:	cmp    %r8,%rcx
    12f1:	jne    12b0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>
    12f3:	jmp    1398 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x178>
    12f8:	mov    %rsi,%rdi
    12fb:	and    $0xffffffffffffffe0,%rdi
    12ff:	xor    %r8d,%r8d
    1302:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1310:	vmovdqu (%rdx,%r8,8),%ymm0
    1316:	vmovdqu 0x40(%rdx,%r8,8),%ymm1
    131d:	vphaddd 0x20(%rdx,%r8,8),%ymm0,%ymm0
    1324:	vphaddd 0x60(%rdx,%r8,8),%ymm1,%ymm1
    132b:	vmovdqu 0x80(%rdx,%r8,8),%ymm2
    1335:	vmovdqu 0xc0(%rdx,%r8,8),%ymm3
    133f:	vpermq $0xd8,%ymm0,%ymm0
    1345:	vpermq $0xd8,%ymm1,%ymm1
    134b:	vphaddd 0xa0(%rdx,%r8,8),%ymm2,%ymm2
    1355:	vphaddd 0xe0(%rdx,%r8,8),%ymm3,%ymm3
    135f:	vpermq $0xd8,%ymm2,%ymm2
    1365:	vpermq $0xd8,%ymm3,%ymm3
    136b:	vmovdqu %ymm0,(%rax,%r8,4)
    1371:	vmovdqu %ymm1,0x20(%rax,%r8,4)
    1378:	vmovdqu %ymm2,0x40(%rax,%r8,4)
    137f:	vmovdqu %ymm3,0x60(%rax,%r8,4)
    1386:	add    $0x20,%r8
    138a:	cmp    %r8,%rdi
    138d:	jne    1310 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf0>
    138f:	cmp    %rdi,%rsi
    1392:	jne    1264 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x44>
    1398:	vzeroupper
    139b:	ret
    139c:	nopl   0x0(%rax)
