0000000000001250 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	push   %rax
    1251:	mov    (%rsi),%rax
    1254:	mov    0x8(%rsi),%rcx
    1258:	sub    %rax,%rcx
    125b:	je     1296 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x46>
    125d:	sar    $0x2,%rcx
    1261:	mov    (%rdi),%rdx
    1264:	mov    0x8(%rdi),%rsi
    1268:	sub    %rdx,%rsi
    126b:	sar    $0x2,%rsi
    126f:	cmp    $0x1,%rcx
    1273:	adc    $0x0,%rcx
    1277:	xor    %edi,%edi
    1279:	nopl   0x0(%rax)
    1280:	movzbl (%rax,%rdi,4),%r8d
    1285:	cmp    %r8,%rsi
    1288:	jbe    1298 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x48>
    128a:	incl   (%rdx,%r8,4)
    128e:	inc    %rdi
    1291:	cmp    %rdi,%rcx
    1294:	jne    1280 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1296:	pop    %rax
    1297:	ret
    1298:	lea    0xd91(%rip),%rdi        # 2030 <_IO_stdin_used+0x30>
    129f:	lea    0xd8d(%rip),%rsi        # 2033 <_IO_stdin_used+0x33>
    12a6:	xor    %eax,%eax
    12a8:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12ad:	mov    %rax,%rdi
    12b0:	call   15b0 <__clang_call_terminate>
    12b5:	data16 cs nopw 0x0(%rax,%rax,1)
