0000000000001250 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1250:	push   %rax
    1251:	mov    (%rdx),%rax
    1254:	mov    0x8(%rdx),%rcx
    1258:	sub    %rax,%rcx
    125b:	je     12ae <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x5e>
    125d:	sar    $0x2,%rcx
    1261:	mov    (%rsi),%rdx
    1264:	mov    0x8(%rsi),%rsi
    1268:	sub    %rdx,%rsi
    126b:	sar    $0x2,%rsi
    126f:	mov    (%rdi),%r8
    1272:	mov    0x8(%rdi),%rdi
    1276:	sub    %r8,%rdi
    1279:	sar    $0x2,%rdi
    127d:	cmp    $0x1,%rcx
    1281:	adc    $0x0,%rcx
    1285:	xor    %r9d,%r9d
    1288:	nopl   0x0(%rax,%rax,1)
    1290:	movslq (%rax,%r9,4),%r10
    1294:	cmp    %r10,%rsi
    1297:	jbe    12b0 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x60>
    1299:	cmp    %r9,%rdi
    129c:	je     12c5 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x75>
    129e:	mov    (%rdx,%r10,4),%r10d
    12a2:	mov    %r10d,(%r8,%r9,4)
    12a6:	inc    %r9
    12a9:	cmp    %r9,%rcx
    12ac:	jne    1290 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12ae:	pop    %rax
    12af:	ret
    12b0:	lea    0xda9(%rip),%rdi        # 2060 <_IO_stdin_used+0x60>
    12b7:	lea    0xda5(%rip),%rsi        # 2063 <_IO_stdin_used+0x63>
    12be:	xor    %eax,%eax
    12c0:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12c5:	lea    0xd94(%rip),%rdi        # 2060 <_IO_stdin_used+0x60>
    12cc:	lea    0xe01(%rip),%rsi        # 20d4 <_IO_stdin_used+0xd4>
    12d3:	xor    %eax,%eax
    12d5:	call   1100 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>
    12da:	mov    %rax,%rdi
    12dd:	call   1780 <__clang_call_terminate>
    12e2:	mov    %rax,%rdi
    12e5:	call   1780 <__clang_call_terminate>
    12ea:	nopw   0x0(%rax,%rax,1)
