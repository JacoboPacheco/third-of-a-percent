0000000000001770 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    1770:	endbr64
    1774:	mov    0x8(%rsi),%rax
    1778:	mov    (%rsi),%r9
    177b:	mov    %rax,%r10
    177e:	sub    %r9,%r10
    1781:	sar    $0x2,%r10
    1785:	cmp    %r9,%rax
    1788:	je     1820 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    178e:	sub    $0x8,%rsp
    1792:	mov    (%rdx),%r11
    1795:	mov    0x8(%rdx),%rsi
    1799:	xor    %eax,%eax
    179b:	sub    %r11,%rsi
    179e:	sar    $0x2,%rsi
    17a2:	mov    (%r9,%rax,4),%edx
    17a6:	cmp    %rax,%rsi
    17a9:	je     17e0 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x70>
    17ab:	mov    (%r11,%rax,4),%ecx
    17af:	mov    (%rdi),%r8
    17b2:	add    %edx,%ecx
    17b4:	mov    0x8(%rdi),%rdx
    17b8:	sub    %r8,%rdx
    17bb:	sar    $0x2,%rdx
    17bf:	cmp    %rdx,%rax
    17c2:	jae    1800 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x90>
    17c4:	mov    %ecx,(%r8,%rax,4)
    17c8:	add    $0x1,%rax
    17cc:	cmp    %r10,%rax
    17cf:	jb     17a2 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x32>
    17d1:	add    $0x8,%rsp
    17d5:	ret
    17d6:	cs nopw 0x0(%rax,%rax,1)
    17e0:	lea    0x81d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    17e7:	lea    0x852(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    17ee:	mov    $0x47d,%esi
    17f3:	lea    0x91e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    17fa:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    17ff:	nop
    1800:	lea    0x7fd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1807:	lea    0x932(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    180e:	mov    $0x46a,%esi
    1813:	lea    0x8fe(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    181a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    181f:	nop
    1820:	ret
    1821:	cs nopw 0x0(%rax,%rax,1)
    182b:	nopl   0x0(%rax,%rax,1)
