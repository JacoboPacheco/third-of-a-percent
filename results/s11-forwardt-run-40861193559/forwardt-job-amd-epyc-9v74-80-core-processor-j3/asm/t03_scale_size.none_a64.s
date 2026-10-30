0000000000001240 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1377 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdi),%rdx
    1257:	cmp    $0x1,%rcx
    125b:	mov    %rcx,%rsi
    125e:	adc    $0x0,%rsi
    1262:	xor    %edi,%edi
    1264:	cmp    $0x8,%rcx
    1268:	jb     12b4 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
    126a:	mov    %rdx,%r8
    126d:	sub    %rax,%r8
    1270:	cmp    $0x20,%r8
    1274:	jb     12b4 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
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
    12a9:	jne    1280 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12ab:	cmp    %rdi,%rsi
    12ae:	je     1377 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    12b4:	mov    %rsi,%r9
    12b7:	mov    %rdi,%r8
    12ba:	and    $0x3,%r9
    12be:	je     1313 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd3>
    12c0:	mov    %rdi,%r8
    12c3:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12d2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	mov    (%rax,%r8,4),%r10d
    1304:	add    %r10d,%r10d
    1307:	mov    %r10d,(%rdx,%r8,4)
    130b:	inc    %r8
    130e:	dec    %r9
    1311:	jne    1300 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1313:	sub    %rsi,%rdi
    1316:	cmp    $0xfffffffffffffffc,%rdi
    131a:	ja     1377 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    131c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    132b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133a:	nopw   0x0(%rax,%rax,1)
    1340:	mov    (%rax,%r8,4),%esi
    1344:	add    %esi,%esi
    1346:	mov    %esi,(%rdx,%r8,4)
    134a:	mov    0x4(%rax,%r8,4),%esi
    134f:	add    %esi,%esi
    1351:	mov    %esi,0x4(%rdx,%r8,4)
    1356:	mov    0x8(%rax,%r8,4),%esi
    135b:	add    %esi,%esi
    135d:	mov    %esi,0x8(%rdx,%r8,4)
    1362:	mov    0xc(%rax,%r8,4),%esi
    1367:	add    %esi,%esi
    1369:	mov    %esi,0xc(%rdx,%r8,4)
    136e:	add    $0x4,%r8
    1372:	cmp    %r8,%rcx
    1375:	jne    1340 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1377:	ret
    1378:	nopl   0x0(%rax,%rax,1)
