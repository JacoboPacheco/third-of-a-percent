0000000000001280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	mov    (%rdx),%rax
    1283:	mov    0x8(%rdx),%rdx
    1287:	mov    %rdx,%r8
    128a:	sub    %rax,%r8
    128d:	mov    (%rdi),%rcx
    1290:	mov    0x8(%rdi),%rdi
    1294:	sub    %rcx,%rdi
    1297:	cmp    %r8,%rdi
    129a:	jb     1395 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x115>
    12a0:	cmp    %rax,%rdx
    12a3:	je     1394 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x114>
    12a9:	sar    $0x2,%r8
    12ad:	cmp    $0x1,%r8
    12b1:	mov    %r8,%rdi
    12b4:	adc    $0x0,%rdi
    12b8:	mov    (%rsi),%rdx
    12bb:	mov    %edi,%esi
    12bd:	and    $0x3,%esi
    12c0:	cmp    $0x4,%r8
    12c4:	jae    12cb <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x4b>
    12c6:	xor    %r8d,%r8d
    12c9:	jmp    133f <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xbf>
    12cb:	and    $0xfffffffffffffffc,%rdi
    12cf:	xor    %r8d,%r8d
    12d2:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	movslq (%rax,%r8,4),%r9
    1304:	mov    (%rdx,%r9,4),%r9d
    1308:	mov    %r9d,(%rcx,%r8,4)
    130c:	movslq 0x4(%rax,%r8,4),%r9
    1311:	mov    (%rdx,%r9,4),%r9d
    1315:	mov    %r9d,0x4(%rcx,%r8,4)
    131a:	movslq 0x8(%rax,%r8,4),%r9
    131f:	mov    (%rdx,%r9,4),%r9d
    1323:	mov    %r9d,0x8(%rcx,%r8,4)
    1328:	movslq 0xc(%rax,%r8,4),%r9
    132d:	mov    (%rdx,%r9,4),%r9d
    1331:	mov    %r9d,0xc(%rcx,%r8,4)
    1336:	add    $0x4,%r8
    133a:	cmp    %r8,%rdi
    133d:	jne    1300 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    133f:	test   %rsi,%rsi
    1342:	je     1394 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x114>
    1344:	lea    (%rcx,%r8,4),%rcx
    1348:	lea    (%rax,%r8,4),%rax
    134c:	xor    %edi,%edi
    134e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    135d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137b:	nopl   0x0(%rax,%rax,1)
    1380:	movslq (%rax,%rdi,4),%r8
    1384:	mov    (%rdx,%r8,4),%r8d
    1388:	mov    %r8d,(%rcx,%rdi,4)
    138c:	inc    %rdi
    138f:	cmp    %rdi,%rsi
    1392:	jne    1380 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1394:	ret
    1395:	ud2
    1397:	nopw   0x0(%rax,%rax,1)
