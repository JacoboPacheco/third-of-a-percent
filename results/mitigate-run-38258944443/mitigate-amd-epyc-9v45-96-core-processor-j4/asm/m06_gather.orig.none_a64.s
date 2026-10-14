0000000000001280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	mov    (%rdx),%rcx
    1283:	mov    0x8(%rdx),%r9
    1287:	sub    %rcx,%r9
    128a:	je     1354 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd4>
    1290:	sar    $0x2,%r9
    1294:	mov    (%rsi),%rax
    1297:	cmp    $0x1,%r9
    129b:	mov    %r9,%r8
    129e:	adc    $0x0,%r8
    12a2:	mov    (%rdi),%rsi
    12a5:	mov    %r8d,%edx
    12a8:	and    $0x3,%edx
    12ab:	cmp    $0x4,%r9
    12af:	jae    12b5 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x35>
    12b1:	xor    %edi,%edi
    12b3:	jmp    12ff <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x7f>
    12b5:	and    $0xfffffffffffffffc,%r8
    12b9:	xor    %edi,%edi
    12bb:	nopl   0x0(%rax,%rax,1)
    12c0:	movslq (%rcx,%rdi,4),%r9
    12c4:	mov    (%rax,%r9,4),%r9d
    12c8:	mov    %r9d,(%rsi,%rdi,4)
    12cc:	movslq 0x4(%rcx,%rdi,4),%r9
    12d1:	mov    (%rax,%r9,4),%r9d
    12d5:	mov    %r9d,0x4(%rsi,%rdi,4)
    12da:	movslq 0x8(%rcx,%rdi,4),%r9
    12df:	mov    (%rax,%r9,4),%r9d
    12e3:	mov    %r9d,0x8(%rsi,%rdi,4)
    12e8:	movslq 0xc(%rcx,%rdi,4),%r9
    12ed:	mov    (%rax,%r9,4),%r9d
    12f1:	mov    %r9d,0xc(%rsi,%rdi,4)
    12f6:	add    $0x4,%rdi
    12fa:	cmp    %rdi,%r8
    12fd:	jne    12c0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12ff:	test   %rdx,%rdx
    1302:	je     1354 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd4>
    1304:	lea    (%rsi,%rdi,4),%rsi
    1308:	lea    (%rcx,%rdi,4),%rcx
    130c:	xor    %edi,%edi
    130e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    131d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    132c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    133b:	nopl   0x0(%rax,%rax,1)
    1340:	movslq (%rcx,%rdi,4),%r8
    1344:	mov    (%rax,%r8,4),%r8d
    1348:	mov    %r8d,(%rsi,%rdi,4)
    134c:	inc    %rdi
    134f:	cmp    %rdi,%rdx
    1352:	jne    1340 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1354:	ret
    1355:	data16 cs nopw 0x0(%rax,%rax,1)
