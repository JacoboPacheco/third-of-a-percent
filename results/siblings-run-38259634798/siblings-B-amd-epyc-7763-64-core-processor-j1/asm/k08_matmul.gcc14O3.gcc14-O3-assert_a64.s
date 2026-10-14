0000000000001970 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    1970:	endbr64
    1974:	test   %rcx,%rcx
    1977:	je     1ab0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x140>
    197d:	push   %r15
    197f:	mov    %rdx,%r9
    1982:	mov    %rcx,%r11
    1985:	xor    %edx,%edx
    1987:	push   %r14
    1989:	mov    %rcx,%r10
    198c:	push   %r13
    198e:	push   %r12
    1990:	xor    %r12d,%r12d
    1993:	push   %rbp
    1994:	push   %rbx
    1995:	xor    %ebx,%ebx
    1997:	sub    $0x28,%rsp
    199b:	mov    (%rsi),%r13
    199e:	mov    0x8(%rsi),%rax
    19a2:	sub    %r13,%rax
    19a5:	sar    $0x2,%rax
    19a9:	mov    %rax,%r14
    19ac:	mov    %rbx,0x18(%rsp)
    19b1:	mov    %rdx,%r8
    19b4:	mov    %r12,%rcx
    19b7:	mov    %rdx,%rbx
    19ba:	mov    %r10,%rsi
    19bd:	cmp    %r14,%rcx
    19c0:	jae    1a70 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    19c6:	mov    (%r9),%rax
    19c9:	mov    0x8(%r9),%r10
    19cd:	mov    %r12,0x8(%rsp)
    19d2:	mov    %r13,0x10(%rsp)
    19d7:	mov    0x0(%r13,%rcx,4),%r15d
    19dc:	sub    %rax,%r10
    19df:	lea    (%rax,%r8,4),%rbp
    19e3:	mov    %r12,%rax
    19e6:	sar    $0x2,%r10
    19ea:	lea    (%rax,%r8,1),%rdx
    19ee:	cmp    %r10,%rdx
    19f1:	jae    1a70 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    19f3:	mov    (%rdi),%r12
    19f6:	mov    0x8(%rdi),%rdx
    19fa:	mov    0x0(%rbp,%rax,4),%r13d
    19ff:	sub    %r12,%rdx
    1a02:	sar    $0x2,%rdx
    1a06:	imul   %r15d,%r13d
    1a0a:	cmp    %rdx,%rax
    1a0d:	jae    1a90 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x120>
    1a13:	add    %r13d,(%r12,%rax,4)
    1a17:	add    $0x1,%rax
    1a1b:	cmp    %r11,%rax
    1a1e:	jne    19ea <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x7a>
    1a20:	add    $0x1,%rcx
    1a24:	mov    0x8(%rsp),%r12
    1a29:	mov    0x10(%rsp),%r13
    1a2e:	add    %rsi,%r8
    1a31:	cmp    %rcx,%r11
    1a34:	jne    19bd <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x4d>
    1a36:	mov    %rbx,%rdx
    1a39:	mov    0x18(%rsp),%rbx
    1a3e:	mov    %rsi,%r10
    1a41:	add    %rsi,%r11
    1a44:	add    %rsi,%r12
    1a47:	sub    %rsi,%rdx
    1a4a:	add    $0x1,%rbx
    1a4e:	cmp    %rbx,%rsi
    1a51:	jne    19ac <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x3c>
    1a57:	add    $0x28,%rsp
    1a5b:	pop    %rbx
    1a5c:	pop    %rbp
    1a5d:	pop    %r12
    1a5f:	pop    %r13
    1a61:	pop    %r14
    1a63:	pop    %r15
    1a65:	ret
    1a66:	cs nopw 0x0(%rax,%rax,1)
    1a70:	lea    0x58d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1a77:	lea    0x5c2(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    1a7e:	mov    $0x47d,%esi
    1a83:	lea    0x68e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1a8a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1a8f:	nop
    1a90:	lea    0x56d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1a97:	lea    0x6a2(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    1a9e:	mov    $0x46a,%esi
    1aa3:	lea    0x66e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1aaa:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1aaf:	nop
    1ab0:	ret
    1ab1:	cs nopw 0x0(%rax,%rax,1)
    1abb:	nopl   0x0(%rax,%rax,1)
