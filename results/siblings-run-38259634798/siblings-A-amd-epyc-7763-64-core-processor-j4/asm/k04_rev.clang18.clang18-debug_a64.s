0000000000001280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	push   %rax
    1281:	mov    (%rsi),%rax
    1284:	mov    0x8(%rsi),%rcx
    1288:	sub    %rax,%rcx
    128b:	je     12de <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    128d:	sar    $0x2,%rcx
    1291:	mov    (%rdi),%rdx
    1294:	mov    0x8(%rdi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	lea    -0x1(%rcx),%rdi
    12a3:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	cmp    %rsi,%rdi
    12c3:	jae    12e0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12c5:	mov    -0x4(%rax,%rcx,4),%r8d
    12ca:	add    %r8d,%r8d
    12cd:	mov    %r8d,-0x4(%rdx,%rcx,4)
    12d2:	lea    -0x1(%rcx),%r8
    12d6:	mov    %r8,%rcx
    12d9:	test   %r8,%r8
    12dc:	jne    12c0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12de:	pop    %rax
    12df:	ret
    12e0:	lea    0xd49(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    12e7:	lea    0xd45(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12ee:	xor    %eax,%eax
    12f0:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12f5:	mov    %rax,%rdi
    12f8:	call   1620 <__clang_call_terminate>
    12fd:	nopl   (%rax)
