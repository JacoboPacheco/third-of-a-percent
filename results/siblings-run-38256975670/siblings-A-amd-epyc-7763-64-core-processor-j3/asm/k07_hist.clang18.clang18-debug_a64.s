0000000000001280 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	push   %rax
    1281:	mov    (%rsi),%rax
    1284:	mov    0x8(%rsi),%rcx
    1288:	sub    %rax,%rcx
    128b:	je     12d6 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x56>
    128d:	sar    $0x2,%rcx
    1291:	mov    (%rdi),%rdx
    1294:	mov    0x8(%rdi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	cmp    $0x1,%rcx
    12a3:	adc    $0x0,%rcx
    12a7:	xor    %edi,%edi
    12a9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b8:	nopl   0x0(%rax,%rax,1)
    12c0:	movzbl (%rax,%rdi,4),%r8d
    12c5:	cmp    %r8,%rsi
    12c8:	jbe    12d8 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x58>
    12ca:	incl   (%rdx,%r8,4)
    12ce:	inc    %rdi
    12d1:	cmp    %rdi,%rcx
    12d4:	jne    12c0 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12d6:	pop    %rax
    12d7:	ret
    12d8:	lea    0xd51(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    12df:	lea    0xd4d(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12e6:	xor    %eax,%eax
    12e8:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12ed:	mov    %rax,%rdi
    12f0:	call   1640 <__clang_call_terminate>
    12f5:	data16 cs nopw 0x0(%rax,%rax,1)
