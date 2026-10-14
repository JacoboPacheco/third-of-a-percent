0000000000001280 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rsi),%rax
    1283:	mov    0x8(%rsi),%rcx
    1287:	sub    %rax,%rcx
    128a:	je     13b7 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1290:	sar    $0x2,%rcx
    1294:	mov    (%rdi),%rdx
    1297:	cmp    $0x1,%rcx
    129b:	mov    %rcx,%rsi
    129e:	adc    $0x0,%rsi
    12a2:	xor    %edi,%edi
    12a4:	cmp    $0x8,%rcx
    12a8:	jb     12f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
    12aa:	mov    %rdx,%r8
    12ad:	sub    %rax,%r8
    12b0:	cmp    $0x20,%r8
    12b4:	jb     12f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
    12b6:	mov    %rsi,%rdi
    12b9:	and    $0xfffffffffffffff8,%rdi
    12bd:	xor    %r8d,%r8d
    12c0:	movdqu (%rax,%r8,4),%xmm0
    12c6:	movdqu 0x10(%rax,%r8,4),%xmm1
    12cd:	paddd  %xmm0,%xmm0
    12d1:	paddd  %xmm1,%xmm1
    12d5:	movdqu %xmm0,(%rdx,%r8,4)
    12db:	movdqu %xmm1,0x10(%rdx,%r8,4)
    12e2:	add    $0x8,%r8
    12e6:	cmp    %r8,%rdi
    12e9:	jne    12c0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12eb:	cmp    %rdi,%rsi
    12ee:	je     13b7 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    12f4:	mov    %rsi,%r9
    12f7:	mov    %rdi,%r8
    12fa:	and    $0x3,%r9
    12fe:	je     1353 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd3>
    1300:	mov    %rdi,%r8
    1303:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1312:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1321:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1330:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133f:	nop
    1340:	mov    (%rax,%r8,4),%r10d
    1344:	add    %r10d,%r10d
    1347:	mov    %r10d,(%rdx,%r8,4)
    134b:	inc    %r8
    134e:	dec    %r9
    1351:	jne    1340 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1353:	sub    %rsi,%rdi
    1356:	cmp    $0xfffffffffffffffc,%rdi
    135a:	ja     13b7 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    135c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137a:	nopw   0x0(%rax,%rax,1)
    1380:	mov    (%rax,%r8,4),%esi
    1384:	add    %esi,%esi
    1386:	mov    %esi,(%rdx,%r8,4)
    138a:	mov    0x4(%rax,%r8,4),%esi
    138f:	add    %esi,%esi
    1391:	mov    %esi,0x4(%rdx,%r8,4)
    1396:	mov    0x8(%rax,%r8,4),%esi
    139b:	add    %esi,%esi
    139d:	mov    %esi,0x8(%rdx,%r8,4)
    13a2:	mov    0xc(%rax,%r8,4),%esi
    13a7:	add    %esi,%esi
    13a9:	mov    %esi,0xc(%rdx,%r8,4)
    13ae:	add    $0x4,%r8
    13b2:	cmp    %r8,%rcx
    13b5:	jne    1380 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    13b7:	ret
    13b8:	nopl   0x0(%rax,%rax,1)
