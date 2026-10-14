0000000000001240 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1317 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd7>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdi),%rdx
    1257:	cmp    $0x1,%rcx
    125b:	mov    %rcx,%rsi
    125e:	adc    $0x0,%rsi
    1262:	xor    %edi,%edi
    1264:	cmp    $0x8,%rcx
    1268:	jb     12b0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    126a:	mov    %rdx,%r8
    126d:	sub    %rax,%r8
    1270:	cmp    $0x20,%r8
    1274:	jb     12b0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    1276:	mov    %rsi,%rdi
    1279:	and    $0xfffffffffffffff8,%rdi
    127d:	xor    %r8d,%r8d
    1280:	movdqu (%rax,%r8,4),%xmm0
    1286:	movdqu 0x10(%rax,%r8,4),%xmm1
    128d:	paddd  %xmm0,%xmm0
    1291:	paddd  %xmm1,%xmm1
    1295:	movdqu %xmm0,(%rdx,%r8,4)
    129b:	movdqu %xmm1,0x10(%rdx,%r8,4)
    12a2:	add    $0x8,%r8
    12a6:	cmp    %r8,%rdi
    12a9:	jne    1280 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12ab:	cmp    %rdi,%rsi
    12ae:	je     1317 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd7>
    12b0:	mov    %rsi,%r9
    12b3:	mov    %rdi,%r8
    12b6:	and    $0x3,%r9
    12ba:	je     12d3 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x93>
    12bc:	mov    %rdi,%r8
    12bf:	nop
    12c0:	mov    (%rax,%r8,4),%r10d
    12c4:	add    %r10d,%r10d
    12c7:	mov    %r10d,(%rdx,%r8,4)
    12cb:	inc    %r8
    12ce:	dec    %r9
    12d1:	jne    12c0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12d3:	sub    %rsi,%rdi
    12d6:	cmp    $0xfffffffffffffffc,%rdi
    12da:	ja     1317 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd7>
    12dc:	nopl   0x0(%rax)
    12e0:	mov    (%rax,%r8,4),%esi
    12e4:	add    %esi,%esi
    12e6:	mov    %esi,(%rdx,%r8,4)
    12ea:	mov    0x4(%rax,%r8,4),%esi
    12ef:	add    %esi,%esi
    12f1:	mov    %esi,0x4(%rdx,%r8,4)
    12f6:	mov    0x8(%rax,%r8,4),%esi
    12fb:	add    %esi,%esi
    12fd:	mov    %esi,0x8(%rdx,%r8,4)
    1302:	mov    0xc(%rax,%r8,4),%esi
    1307:	add    %esi,%esi
    1309:	mov    %esi,0xc(%rdx,%r8,4)
    130e:	add    $0x4,%r8
    1312:	cmp    %r8,%rcx
    1315:	jne    12e0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    1317:	ret
    1318:	nopl   0x0(%rax,%rax,1)
