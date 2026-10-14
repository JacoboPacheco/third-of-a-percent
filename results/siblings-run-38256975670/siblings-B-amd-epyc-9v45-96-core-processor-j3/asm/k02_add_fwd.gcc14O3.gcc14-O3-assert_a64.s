0000000000001790 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    1790:	endbr64
    1794:	mov    0x8(%rsi),%rax
    1798:	mov    (%rsi),%r9
    179b:	mov    %rax,%r10
    179e:	sub    %r9,%r10
    17a1:	sar    $0x2,%r10
    17a5:	cmp    %r9,%rax
    17a8:	je     1840 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    17ae:	sub    $0x8,%rsp
    17b2:	mov    (%rdx),%r11
    17b5:	mov    0x8(%rdx),%rsi
    17b9:	xor    %eax,%eax
    17bb:	sub    %r11,%rsi
    17be:	sar    $0x2,%rsi
    17c2:	mov    (%r9,%rax,4),%edx
    17c6:	cmp    %rax,%rsi
    17c9:	je     1800 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x70>
    17cb:	mov    (%r11,%rax,4),%ecx
    17cf:	mov    (%rdi),%r8
    17d2:	add    %edx,%ecx
    17d4:	mov    0x8(%rdi),%rdx
    17d8:	sub    %r8,%rdx
    17db:	sar    $0x2,%rdx
    17df:	cmp    %rdx,%rax
    17e2:	jae    1820 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x90>
    17e4:	mov    %ecx,(%r8,%rax,4)
    17e8:	add    $0x1,%rax
    17ec:	cmp    %r10,%rax
    17ef:	jb     17c2 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x32>
    17f1:	add    $0x8,%rsp
    17f5:	ret
    17f6:	cs nopw 0x0(%rax,%rax,1)
    1800:	lea    0x7fd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1807:	lea    0x832(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    180e:	mov    $0x47d,%esi
    1813:	lea    0x8fe(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    181a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    181f:	nop
    1820:	lea    0x7dd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1827:	lea    0x912(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    182e:	mov    $0x46a,%esi
    1833:	lea    0x8de(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    183a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    183f:	nop
    1840:	ret
    1841:	cs nopw 0x0(%rax,%rax,1)
    184b:	nopl   0x0(%rax,%rax,1)
