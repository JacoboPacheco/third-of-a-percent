0000000000001280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	mov    (%rdx),%rax
    1283:	mov    0x8(%rdx),%r8
    1287:	mov    %r8,%rcx
    128a:	sub    %rax,%rcx
    128d:	mov    (%rdi),%rdx
    1290:	mov    0x8(%rdi),%rdi
    1294:	sub    %rdx,%rdi
    1297:	cmp    %rcx,%rdi
    129a:	jb     12da <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5a>
    129c:	cmp    %rax,%r8
    129f:	je     12d9 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x59>
    12a1:	sar    $0x2,%rcx
    12a5:	mov    (%rsi),%rdi
    12a8:	mov    0x8(%rsi),%rsi
    12ac:	sub    %rdi,%rsi
    12af:	sar    $0x2,%rsi
    12b3:	cmp    $0x1,%rcx
    12b7:	adc    $0x0,%rcx
    12bb:	xor    %r8d,%r8d
    12be:	xchg   %ax,%ax
    12c0:	movslq (%rax,%r8,4),%r9
    12c4:	cmp    %r9,%rsi
    12c7:	jbe    12da <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5a>
    12c9:	mov    (%rdi,%r9,4),%r9d
    12cd:	mov    %r9d,(%rdx,%r8,4)
    12d1:	inc    %r8
    12d4:	cmp    %r8,%rcx
    12d7:	jne    12c0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12d9:	ret
    12da:	ud2
    12dc:	nopl   0x0(%rax)
