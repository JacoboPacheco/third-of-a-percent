00000000000011e0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
    11e0:	test   %edx,%edx
    11e2:	jle    122e <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x4e>
    11e4:	mov    (%rsi),%rax
    11e7:	mov    0x8(%rsi),%rsi
    11eb:	sub    %rax,%rsi
    11ee:	sar    $0x2,%rsi
    11f2:	mov    (%rdi),%r8
    11f5:	mov    0x8(%rdi),%rdi
    11f9:	sub    %r8,%rdi
    11fc:	sar    $0x2,%rdi
    1200:	movslq %ecx,%rcx
    1203:	mov    %edx,%edx
    1205:	lea    (%r8,%rcx,4),%r8
    1209:	xor    %r9d,%r9d
    120c:	nopl   0x0(%rax)
    1210:	cmp    %r9,%rsi
    1213:	je     122f <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x4f>
    1215:	lea    (%rcx,%r9,1),%r10
    1219:	cmp    %r10,%rdi
    121c:	jbe    122f <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x4f>
    121e:	mov    (%rax,%r9,4),%r10d
    1222:	mov    %r10d,(%r8,%r9,4)
    1226:	inc    %r9
    1229:	cmp    %r9,%rdx
    122c:	jne    1210 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x30>
    122e:	ret
    122f:	ud2
    1231:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
