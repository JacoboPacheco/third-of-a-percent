0000000000001280 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1280:	push   %rax
    1281:	mov    (%rdi),%rax
    1284:	mov    0x8(%rdi),%rcx
    1288:	sub    %rax,%rcx
    128b:	je     12e4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x64>
    128d:	sar    $0x2,%rcx
    1291:	mov    (%rsi),%rdx
    1294:	mov    0x8(%rsi),%rsi
    1298:	sub    %rdx,%rsi
    129b:	sar    $0x2,%rsi
    129f:	cmp    $0x1,%rcx
    12a3:	adc    $0x0,%rcx
    12a7:	xor    %edi,%edi
    12a9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b8:	nopl   0x0(%rax,%rax,1)
    12c0:	cmp    %rdi,%rsi
    12c3:	jbe    12e6 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x66>
    12c5:	lea    0x1(%rdi),%r8
    12c9:	cmp    %r8,%rsi
    12cc:	jbe    12fb <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x7b>
    12ce:	mov    0x4(%rdx,%rdi,4),%r8d
    12d3:	add    (%rdx,%rdi,4),%r8d
    12d7:	mov    %r8d,(%rax,%rdi,2)
    12db:	add    $0x2,%rdi
    12df:	dec    %rcx
    12e2:	jne    12c0 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12e4:	pop    %rax
    12e5:	ret
    12e6:	lea    0xd43(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    12ed:	lea    0xd3f(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12f4:	xor    %eax,%eax
    12f6:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12fb:	lea    0xd2e(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    1302:	lea    0xd2a(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    1309:	xor    %eax,%eax
    130b:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    1310:	mov    %rax,%rdi
    1313:	call   1680 <__clang_call_terminate>
    1318:	mov    %rax,%rdi
    131b:	call   1680 <__clang_call_terminate>
