0000000000001240 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
    1240:	test   %rdx,%rdx
    1243:	je     132f <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xef>
    1249:	mov    (%rsi),%rax
    124c:	mov    (%rdi),%rcx
    124f:	xor    %esi,%esi
    1251:	cmp    $0x8,%rdx
    1255:	jb     12b0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x70>
    1257:	mov    %rcx,%rdi
    125a:	sub    %rax,%rdi
    125d:	cmp    $0x20,%rdi
    1261:	jb     12b0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x70>
    1263:	mov    %rdx,%rsi
    1266:	and    $0xfffffffffffffff8,%rsi
    126a:	xor    %edi,%edi
    126c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127b:	nopl   0x0(%rax,%rax,1)
    1280:	movdqu (%rax,%rdi,4),%xmm0
    1285:	movdqu 0x10(%rax,%rdi,4),%xmm1
    128b:	paddd  %xmm0,%xmm0
    128f:	paddd  %xmm1,%xmm1
    1293:	movdqu %xmm0,(%rcx,%rdi,4)
    1298:	movdqu %xmm1,0x10(%rcx,%rdi,4)
    129e:	add    $0x8,%rdi
    12a2:	cmp    %rdi,%rsi
    12a5:	jne    1280 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x40>
    12a7:	cmp    %rdx,%rsi
    12aa:	je     132f <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xef>
    12b0:	mov    %rdx,%r8
    12b3:	mov    %rsi,%rdi
    12b6:	and    $0x3,%r8
    12ba:	je     12d3 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x93>
    12bc:	mov    %rsi,%rdi
    12bf:	nop
    12c0:	mov    (%rax,%rdi,4),%r9d
    12c4:	add    %r9d,%r9d
    12c7:	mov    %r9d,(%rcx,%rdi,4)
    12cb:	inc    %rdi
    12ce:	dec    %r8
    12d1:	jne    12c0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>
    12d3:	sub    %rdx,%rsi
    12d6:	cmp    $0xfffffffffffffffc,%rsi
    12da:	ja     132f <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xef>
    12dc:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12eb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fa:	nopw   0x0(%rax,%rax,1)
    1300:	mov    (%rax,%rdi,4),%esi
    1303:	add    %esi,%esi
    1305:	mov    %esi,(%rcx,%rdi,4)
    1308:	mov    0x4(%rax,%rdi,4),%esi
    130c:	add    %esi,%esi
    130e:	mov    %esi,0x4(%rcx,%rdi,4)
    1312:	mov    0x8(%rax,%rdi,4),%esi
    1316:	add    %esi,%esi
    1318:	mov    %esi,0x8(%rcx,%rdi,4)
    131c:	mov    0xc(%rax,%rdi,4),%esi
    1320:	add    %esi,%esi
    1322:	mov    %esi,0xc(%rcx,%rdi,4)
    1326:	add    $0x4,%rdi
    132a:	cmp    %rdi,%rdx
    132d:	jne    1300 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xc0>
    132f:	ret
