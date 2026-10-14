0000000000001250 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	push   %rax
    1251:	mov    (%rdi),%rax
    1254:	mov    0x8(%rdi),%rcx
    1258:	sub    %rax,%rcx
    125b:	je     12a4 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x54>
    125d:	sar    $0x2,%rcx
    1261:	mov    (%rsi),%rdx
    1264:	mov    0x8(%rsi),%rsi
    1268:	sub    %rdx,%rsi
    126b:	sar    $0x2,%rsi
    126f:	cmp    $0x1,%rcx
    1273:	adc    $0x0,%rcx
    1277:	xor    %edi,%edi
    1279:	nopl   0x0(%rax)
    1280:	cmp    %rdi,%rsi
    1283:	jbe    12a6 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x56>
    1285:	lea    0x1(%rdi),%r8
    1289:	cmp    %r8,%rsi
    128c:	jbe    12bb <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x6b>
    128e:	mov    0x4(%rdx,%rdi,4),%r8d
    1293:	add    (%rdx,%rdi,4),%r8d
    1297:	mov    %r8d,(%rax,%rdi,2)
    129b:	add    $0x2,%rdi
    129f:	dec    %rcx
    12a2:	jne    1280 <_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    12a4:	pop    %rax
    12a5:	ret
    12a6:	lea    0xd83(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    12ad:	lea    0xd7f(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12b4:	xor    %eax,%eax
    12b6:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12bb:	lea    0xd6e(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    12c2:	lea    0xd6a(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12c9:	xor    %eax,%eax
    12cb:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12d0:	mov    %rax,%rdi
    12d3:	call   1610 <__clang_call_terminate>
    12d8:	mov    %rax,%rdi
    12db:	call   1610 <__clang_call_terminate>
