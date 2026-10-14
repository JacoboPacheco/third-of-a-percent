0000000000001280 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1280:	push   %rax
    1281:	mov    (%rdx),%rax
    1284:	mov    0x8(%rdx),%rcx
    1288:	sub    %rax,%rcx
    128b:	je     12de <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5e>
    128d:	sar    $0x2,%rcx
    1291:	mov    (%rsi),%rdx
    1294:	mov    0x8(%rsi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	mov    (%rdi),%r8
    12a2:	mov    0x8(%rdi),%rdi
    12a6:	sub    %r8,%rdi
    12a9:	sar    $0x2,%rdi
    12ad:	cmp    $0x1,%rcx
    12b1:	adc    $0x0,%rcx
    12b5:	xor    %r9d,%r9d
    12b8:	nopl   0x0(%rax,%rax,1)
    12c0:	movslq (%rax,%r9,4),%r10
    12c4:	cmp    %r10,%rsi
    12c7:	jbe    12e0 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x60>
    12c9:	cmp    %r9,%rdi
    12cc:	je     12f5 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x75>
    12ce:	mov    (%rdx,%r10,4),%r10d
    12d2:	mov    %r10d,(%r8,%r9,4)
    12d6:	inc    %r9
    12d9:	cmp    %r9,%rcx
    12dc:	jne    12c0 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12de:	pop    %rax
    12df:	ret
    12e0:	lea    0xd79(%rip),%rdi        # 2060 <_IO_stdin_used+0x60>
    12e7:	lea    0xd75(%rip),%rsi        # 2063 <_IO_stdin_used+0x63>
    12ee:	xor    %eax,%eax
    12f0:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12f5:	lea    0xd64(%rip),%rdi        # 2060 <_IO_stdin_used+0x60>
    12fc:	lea    0xdd1(%rip),%rsi        # 20d4 <_IO_stdin_used+0xd4>
    1303:	xor    %eax,%eax
    1305:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    130a:	mov    %rax,%rdi
    130d:	call   1830 <__clang_call_terminate>
    1312:	mov    %rax,%rdi
    1315:	call   1830 <__clang_call_terminate>
    131a:	nopw   0x0(%rax,%rax,1)
