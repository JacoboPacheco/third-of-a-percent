0000000000001280 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	mov    (%rsi),%rax
    1283:	mov    0x8(%rsi),%rcx
    1287:	sub    %rax,%rcx
    128a:	je     1358 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>
    1290:	sar    $0x2,%rcx
    1294:	mov    (%rdi),%rdx
    1297:	mov    0x8(%rdi),%rsi
    129b:	sub    %rdx,%rsi
    129e:	sar    $0x2,%rsi
    12a2:	cmp    $0x1,%rcx
    12a6:	adc    $0x0,%rcx
    12aa:	lea    -0x1(%rcx),%r8
    12ae:	cmp    %rsi,%r8
    12b1:	cmovae %rsi,%r8
    12b5:	xor    %edi,%edi
    12b7:	cmp    $0x8,%r8
    12bb:	jb     1340 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    12c1:	mov    %rdx,%r9
    12c4:	sub    %rax,%r9
    12c7:	cmp    $0x1f,%r9
    12cb:	jbe    1340 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    12cd:	inc    %r8
    12d0:	mov    %r8d,%edi
    12d3:	and    $0x7,%edi
    12d6:	mov    $0x8,%r9d
    12dc:	cmovne %rdi,%r9
    12e0:	mov    %r8,%rdi
    12e3:	sub    %r9,%rdi
    12e6:	xor    %r8d,%r8d
    12e9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f8:	nopl   0x0(%rax,%rax,1)
    1300:	movdqu (%rax,%r8,4),%xmm0
    1306:	movdqu 0x10(%rax,%r8,4),%xmm1
    130d:	paddd  %xmm0,%xmm0
    1311:	paddd  %xmm1,%xmm1
    1315:	movdqu %xmm0,(%rdx,%r8,4)
    131b:	movdqu %xmm1,0x10(%rdx,%r8,4)
    1322:	add    $0x8,%r8
    1326:	cmp    %r8,%rdi
    1329:	jne    1300 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    132b:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133a:	nopw   0x0(%rax,%rax,1)
    1340:	cmp    %rdi,%rsi
    1343:	je     1359 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd9>
    1345:	mov    (%rax,%rdi,4),%r8d
    1349:	add    %r8d,%r8d
    134c:	mov    %r8d,(%rdx,%rdi,4)
    1350:	inc    %rdi
    1353:	cmp    %rdi,%rcx
    1356:	jne    1340 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1358:	ret
    1359:	ud2
    135b:	nopl   0x0(%rax,%rax,1)
