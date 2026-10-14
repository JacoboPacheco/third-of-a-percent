0000000000001820 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    1820:	endbr64
    1824:	test   %rcx,%rcx
    1827:	je     1960 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x140>
    182d:	push   %r15
    182f:	mov    %rdx,%r9
    1832:	mov    %rcx,%r11
    1835:	xor    %edx,%edx
    1837:	push   %r14
    1839:	mov    %rcx,%r10
    183c:	push   %r13
    183e:	push   %r12
    1840:	xor    %r12d,%r12d
    1843:	push   %rbp
    1844:	push   %rbx
    1845:	xor    %ebx,%ebx
    1847:	sub    $0x28,%rsp
    184b:	mov    (%rsi),%r13
    184e:	mov    0x8(%rsi),%rax
    1852:	sub    %r13,%rax
    1855:	sar    $0x2,%rax
    1859:	mov    %rax,%r14
    185c:	mov    %rbx,0x18(%rsp)
    1861:	mov    %rdx,%r8
    1864:	mov    %r12,%rcx
    1867:	mov    %rdx,%rbx
    186a:	mov    %r10,%rsi
    186d:	cmp    %r14,%rcx
    1870:	jae    1920 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    1876:	mov    (%r9),%rax
    1879:	mov    0x8(%r9),%r10
    187d:	mov    %rcx,0x8(%rsp)
    1882:	mov    %r13,0x10(%rsp)
    1887:	mov    0x0(%r13,%rcx,4),%r15d
    188c:	sub    %rax,%r10
    188f:	lea    (%rax,%r8,4),%rbp
    1893:	mov    %r12,%rax
    1896:	sar    $0x2,%r10
    189a:	lea    (%r8,%rax,1),%rdx
    189e:	cmp    %r10,%rdx
    18a1:	jae    1920 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    18a3:	mov    (%rdi),%rcx
    18a6:	mov    0x8(%rdi),%rdx
    18aa:	mov    0x0(%rbp,%rax,4),%r13d
    18af:	sub    %rcx,%rdx
    18b2:	sar    $0x2,%rdx
    18b6:	imul   %r15d,%r13d
    18ba:	cmp    %rdx,%rax
    18bd:	jae    1940 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x120>
    18c3:	add    %r13d,(%rcx,%rax,4)
    18c7:	add    $0x1,%rax
    18cb:	cmp    %r11,%rax
    18ce:	jne    189a <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x7a>
    18d0:	mov    0x8(%rsp),%rcx
    18d5:	mov    0x10(%rsp),%r13
    18da:	add    %rsi,%r8
    18dd:	add    $0x1,%rcx
    18e1:	cmp    %r11,%rcx
    18e4:	jne    186d <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x4d>
    18e6:	mov    %rbx,%rdx
    18e9:	mov    0x18(%rsp),%rbx
    18ee:	mov    %rsi,%r10
    18f1:	add    %rsi,%r11
    18f4:	add    %rsi,%r12
    18f7:	sub    %rsi,%rdx
    18fa:	add    $0x1,%rbx
    18fe:	cmp    %rbx,%rsi
    1901:	jne    185c <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x3c>
    1907:	add    $0x28,%rsp
    190b:	pop    %rbx
    190c:	pop    %rbp
    190d:	pop    %r12
    190f:	pop    %r13
    1911:	pop    %r14
    1913:	pop    %r15
    1915:	ret
    1916:	cs nopw 0x0(%rax,%rax,1)
    1920:	lea    0x6dd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1927:	lea    0x712(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    192e:	mov    $0x47d,%esi
    1933:	lea    0x7de(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    193a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    193f:	nop
    1940:	lea    0x6bd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1947:	lea    0x7f2(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    194e:	mov    $0x46a,%esi
    1953:	lea    0x7be(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    195a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    195f:	nop
    1960:	ret
    1961:	cs nopw 0x0(%rax,%rax,1)
    196b:	nopl   0x0(%rax,%rax,1)
