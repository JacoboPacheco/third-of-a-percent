0000000000001240 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%rax
    1243:	mov    0x8(%rdx),%rdx
    1247:	mov    %rdx,%r8
    124a:	sub    %rax,%r8
    124d:	mov    (%rdi),%rcx
    1250:	mov    0x8(%rdi),%rdi
    1254:	sub    %rcx,%rdi
    1257:	cmp    %r8,%rdi
    125a:	jb     1305 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc5>
    1260:	cmp    %rax,%rdx
    1263:	je     1304 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    1269:	sar    $0x2,%r8
    126d:	cmp    $0x1,%r8
    1271:	mov    %r8,%rdi
    1274:	adc    $0x0,%rdi
    1278:	mov    (%rsi),%rdx
    127b:	mov    %edi,%esi
    127d:	and    $0x3,%esi
    1280:	cmp    $0x4,%r8
    1284:	jae    128b <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x4b>
    1286:	xor    %r8d,%r8d
    1289:	jmp    12df <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x9f>
    128b:	and    $0xfffffffffffffffc,%rdi
    128f:	xor    %r8d,%r8d
    1292:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a0:	movslq (%rax,%r8,4),%r9
    12a4:	mov    (%rdx,%r9,4),%r9d
    12a8:	mov    %r9d,(%rcx,%r8,4)
    12ac:	movslq 0x4(%rax,%r8,4),%r9
    12b1:	mov    (%rdx,%r9,4),%r9d
    12b5:	mov    %r9d,0x4(%rcx,%r8,4)
    12ba:	movslq 0x8(%rax,%r8,4),%r9
    12bf:	mov    (%rdx,%r9,4),%r9d
    12c3:	mov    %r9d,0x8(%rcx,%r8,4)
    12c8:	movslq 0xc(%rax,%r8,4),%r9
    12cd:	mov    (%rdx,%r9,4),%r9d
    12d1:	mov    %r9d,0xc(%rcx,%r8,4)
    12d6:	add    $0x4,%r8
    12da:	cmp    %r8,%rdi
    12dd:	jne    12a0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x60>
    12df:	test   %rsi,%rsi
    12e2:	je     1304 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    12e4:	lea    (%rcx,%r8,4),%rcx
    12e8:	lea    (%rax,%r8,4),%rax
    12ec:	xor    %edi,%edi
    12ee:	xchg   %ax,%ax
    12f0:	movslq (%rax,%rdi,4),%r8
    12f4:	mov    (%rdx,%r8,4),%r8d
    12f8:	mov    %r8d,(%rcx,%rdi,4)
    12fc:	inc    %rdi
    12ff:	cmp    %rdi,%rsi
    1302:	jne    12f0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xb0>
    1304:	ret
    1305:	ud2
    1307:	nopw   0x0(%rax,%rax,1)
