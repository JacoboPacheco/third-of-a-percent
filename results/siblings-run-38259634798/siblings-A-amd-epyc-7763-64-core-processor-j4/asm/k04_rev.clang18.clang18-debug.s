0000000000001250 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	push   %rax
    1251:	mov    (%rsi),%rax
    1254:	mov    0x8(%rsi),%rcx
    1258:	sub    %rax,%rcx
    125b:	je     129e <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    125d:	sar    $0x2,%rcx
    1261:	mov    (%rdi),%rdx
    1264:	mov    0x8(%rdi),%rsi
    1268:	sub    %rdx,%rsi
    126b:	sar    $0x2,%rsi
    126f:	lea    -0x1(%rcx),%rdi
    1273:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1280:	cmp    %rsi,%rdi
    1283:	jae    12a0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x50>
    1285:	mov    -0x4(%rax,%rcx,4),%r8d
    128a:	add    %r8d,%r8d
    128d:	mov    %r8d,-0x4(%rdx,%rcx,4)
    1292:	lea    -0x1(%rcx),%r8
    1296:	mov    %r8,%rcx
    1299:	test   %r8,%r8
    129c:	jne    1280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    129e:	pop    %rax
    129f:	ret
    12a0:	lea    0xd89(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    12a7:	lea    0xd85(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12ae:	xor    %eax,%eax
    12b0:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12b5:	mov    %rax,%rdi
    12b8:	call   1590 <__clang_call_terminate>
    12bd:	nopl   (%rax)
