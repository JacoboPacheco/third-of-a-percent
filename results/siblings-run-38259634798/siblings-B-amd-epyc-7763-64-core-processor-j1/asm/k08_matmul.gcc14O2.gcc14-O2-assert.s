00000000000017e0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    17e0:	endbr64
    17e4:	test   %rcx,%rcx
    17e7:	je     1920 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x140>
    17ed:	push   %r15
    17ef:	mov    %rdx,%r9
    17f2:	mov    %rcx,%r11
    17f5:	xor    %edx,%edx
    17f7:	push   %r14
    17f9:	mov    %rcx,%r10
    17fc:	push   %r13
    17fe:	push   %r12
    1800:	xor    %r12d,%r12d
    1803:	push   %rbp
    1804:	push   %rbx
    1805:	xor    %ebx,%ebx
    1807:	sub    $0x28,%rsp
    180b:	mov    (%rsi),%r13
    180e:	mov    0x8(%rsi),%rax
    1812:	sub    %r13,%rax
    1815:	sar    $0x2,%rax
    1819:	mov    %rax,%r14
    181c:	mov    %rbx,0x18(%rsp)
    1821:	mov    %rdx,%r8
    1824:	mov    %r12,%rcx
    1827:	mov    %rdx,%rbx
    182a:	mov    %r10,%rsi
    182d:	cmp    %r14,%rcx
    1830:	jae    18e0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    1836:	mov    (%r9),%rax
    1839:	mov    0x8(%r9),%r10
    183d:	mov    %rcx,0x8(%rsp)
    1842:	mov    %r13,0x10(%rsp)
    1847:	mov    0x0(%r13,%rcx,4),%r15d
    184c:	sub    %rax,%r10
    184f:	lea    (%rax,%r8,4),%rbp
    1853:	mov    %r12,%rax
    1856:	sar    $0x2,%r10
    185a:	lea    (%r8,%rax,1),%rdx
    185e:	cmp    %r10,%rdx
    1861:	jae    18e0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    1863:	mov    (%rdi),%rcx
    1866:	mov    0x8(%rdi),%rdx
    186a:	mov    0x0(%rbp,%rax,4),%r13d
    186f:	sub    %rcx,%rdx
    1872:	sar    $0x2,%rdx
    1876:	imul   %r15d,%r13d
    187a:	cmp    %rdx,%rax
    187d:	jae    1900 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x120>
    1883:	add    %r13d,(%rcx,%rax,4)
    1887:	add    $0x1,%rax
    188b:	cmp    %r11,%rax
    188e:	jne    185a <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x7a>
    1890:	mov    0x8(%rsp),%rcx
    1895:	mov    0x10(%rsp),%r13
    189a:	add    %rsi,%r8
    189d:	add    $0x1,%rcx
    18a1:	cmp    %r11,%rcx
    18a4:	jne    182d <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x4d>
    18a6:	mov    %rbx,%rdx
    18a9:	mov    0x18(%rsp),%rbx
    18ae:	mov    %rsi,%r10
    18b1:	add    %rsi,%r11
    18b4:	add    %rsi,%r12
    18b7:	sub    %rsi,%rdx
    18ba:	add    $0x1,%rbx
    18be:	cmp    %rbx,%rsi
    18c1:	jne    181c <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x3c>
    18c7:	add    $0x28,%rsp
    18cb:	pop    %rbx
    18cc:	pop    %rbp
    18cd:	pop    %r12
    18cf:	pop    %r13
    18d1:	pop    %r14
    18d3:	pop    %r15
    18d5:	ret
    18d6:	cs nopw 0x0(%rax,%rax,1)
    18e0:	lea    0x71d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    18e7:	lea    0x752(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    18ee:	mov    $0x47d,%esi
    18f3:	lea    0x81e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    18fa:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    18ff:	nop
    1900:	lea    0x6fd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1907:	lea    0x832(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    190e:	mov    $0x46a,%esi
    1913:	lea    0x7fe(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    191a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    191f:	nop
    1920:	ret
    1921:	cs nopw 0x0(%rax,%rax,1)
    192b:	nopl   0x0(%rax,%rax,1)
