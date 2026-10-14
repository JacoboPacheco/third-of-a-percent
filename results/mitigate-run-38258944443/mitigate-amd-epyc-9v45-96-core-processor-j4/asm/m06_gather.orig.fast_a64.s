0000000000001280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	mov    (%rdx),%rax
    1283:	mov    0x8(%rdx),%rcx
    1287:	sub    %rax,%rcx
    128a:	je     12de <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5e>
    128c:	sar    $0x2,%rcx
    1290:	mov    (%rsi),%rdx
    1293:	mov    0x8(%rsi),%rsi
    1297:	sub    %rdx,%rsi
    129a:	sar    $0x2,%rsi
    129e:	mov    (%rdi),%r8
    12a1:	mov    0x8(%rdi),%rdi
    12a5:	sub    %r8,%rdi
    12a8:	sar    $0x2,%rdi
    12ac:	cmp    $0x1,%rcx
    12b0:	adc    $0x0,%rcx
    12b4:	xor    %r9d,%r9d
    12b7:	nopw   0x0(%rax,%rax,1)
    12c0:	movslq (%rax,%r9,4),%r10
    12c4:	cmp    %r10,%rsi
    12c7:	jbe    12df <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    12c9:	cmp    %r9,%rdi
    12cc:	je     12df <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5f>
    12ce:	mov    (%rdx,%r10,4),%r10d
    12d2:	mov    %r10d,(%r8,%r9,4)
    12d6:	inc    %r9
    12d9:	cmp    %r9,%rcx
    12dc:	jne    12c0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12de:	ret
    12df:	ud2
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
