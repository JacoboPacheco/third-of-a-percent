0000000000001930 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    1930:	endbr64
    1934:	test   %rcx,%rcx
    1937:	je     1a70 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x140>
    193d:	push   %r15
    193f:	mov    %rdx,%r9
    1942:	mov    %rcx,%r11
    1945:	xor    %edx,%edx
    1947:	push   %r14
    1949:	mov    %rcx,%r10
    194c:	push   %r13
    194e:	push   %r12
    1950:	xor    %r12d,%r12d
    1953:	push   %rbp
    1954:	push   %rbx
    1955:	xor    %ebx,%ebx
    1957:	sub    $0x28,%rsp
    195b:	mov    (%rsi),%r13
    195e:	mov    0x8(%rsi),%rax
    1962:	sub    %r13,%rax
    1965:	sar    $0x2,%rax
    1969:	mov    %rax,%r14
    196c:	mov    %rbx,0x18(%rsp)
    1971:	mov    %rdx,%r8
    1974:	mov    %r12,%rcx
    1977:	mov    %rdx,%rbx
    197a:	mov    %r10,%rsi
    197d:	cmp    %r14,%rcx
    1980:	jae    1a30 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    1986:	mov    (%r9),%rax
    1989:	mov    0x8(%r9),%r10
    198d:	mov    %r12,0x8(%rsp)
    1992:	mov    %r13,0x10(%rsp)
    1997:	mov    0x0(%r13,%rcx,4),%r15d
    199c:	sub    %rax,%r10
    199f:	lea    (%rax,%r8,4),%rbp
    19a3:	mov    %r12,%rax
    19a6:	sar    $0x2,%r10
    19aa:	lea    (%rax,%r8,1),%rdx
    19ae:	cmp    %r10,%rdx
    19b1:	jae    1a30 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    19b3:	mov    (%rdi),%r12
    19b6:	mov    0x8(%rdi),%rdx
    19ba:	mov    0x0(%rbp,%rax,4),%r13d
    19bf:	sub    %r12,%rdx
    19c2:	sar    $0x2,%rdx
    19c6:	imul   %r15d,%r13d
    19ca:	cmp    %rdx,%rax
    19cd:	jae    1a50 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x120>
    19d3:	add    %r13d,(%r12,%rax,4)
    19d7:	add    $0x1,%rax
    19db:	cmp    %r11,%rax
    19de:	jne    19aa <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x7a>
    19e0:	add    $0x1,%rcx
    19e4:	mov    0x8(%rsp),%r12
    19e9:	mov    0x10(%rsp),%r13
    19ee:	add    %rsi,%r8
    19f1:	cmp    %rcx,%r11
    19f4:	jne    197d <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x4d>
    19f6:	mov    %rbx,%rdx
    19f9:	mov    0x18(%rsp),%rbx
    19fe:	mov    %rsi,%r10
    1a01:	add    %rsi,%r11
    1a04:	add    %rsi,%r12
    1a07:	sub    %rsi,%rdx
    1a0a:	add    $0x1,%rbx
    1a0e:	cmp    %rbx,%rsi
    1a11:	jne    196c <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x3c>
    1a17:	add    $0x28,%rsp
    1a1b:	pop    %rbx
    1a1c:	pop    %rbp
    1a1d:	pop    %r12
    1a1f:	pop    %r13
    1a21:	pop    %r14
    1a23:	pop    %r15
    1a25:	ret
    1a26:	cs nopw 0x0(%rax,%rax,1)
    1a30:	lea    0x5cd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1a37:	lea    0x602(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    1a3e:	mov    $0x47d,%esi
    1a43:	lea    0x6ce(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1a4a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1a4f:	nop
    1a50:	lea    0x5ad(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1a57:	lea    0x6e2(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    1a5e:	mov    $0x46a,%esi
    1a63:	lea    0x6ae(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1a6a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1a6f:	nop
    1a70:	ret
    1a71:	cs nopw 0x0(%rax,%rax,1)
    1a7b:	nopl   0x0(%rax,%rax,1)
