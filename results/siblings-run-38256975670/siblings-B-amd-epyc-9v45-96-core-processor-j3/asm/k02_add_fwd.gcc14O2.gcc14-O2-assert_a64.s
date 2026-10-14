00000000000016a0 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    16a0:	endbr64
    16a4:	mov    0x8(%rsi),%rax
    16a8:	mov    (%rsi),%r9
    16ab:	mov    %rax,%r10
    16ae:	sub    %r9,%r10
    16b1:	sar    $0x2,%r10
    16b5:	cmp    %r9,%rax
    16b8:	je     1750 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    16be:	sub    $0x8,%rsp
    16c2:	mov    (%rdx),%r11
    16c5:	mov    0x8(%rdx),%rsi
    16c9:	xor    %eax,%eax
    16cb:	sub    %r11,%rsi
    16ce:	sar    $0x2,%rsi
    16d2:	mov    (%r9,%rax,4),%edx
    16d6:	cmp    %rax,%rsi
    16d9:	je     1710 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x70>
    16db:	mov    (%r11,%rax,4),%ecx
    16df:	mov    (%rdi),%r8
    16e2:	add    %edx,%ecx
    16e4:	mov    0x8(%rdi),%rdx
    16e8:	sub    %r8,%rdx
    16eb:	sar    $0x2,%rdx
    16ef:	cmp    %rdx,%rax
    16f2:	jae    1730 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x90>
    16f4:	mov    %ecx,(%r8,%rax,4)
    16f8:	add    $0x1,%rax
    16fc:	cmp    %r10,%rax
    16ff:	jb     16d2 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x32>
    1701:	add    $0x8,%rsp
    1705:	ret
    1706:	cs nopw 0x0(%rax,%rax,1)
    1710:	lea    0x8ed(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1717:	lea    0x922(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    171e:	mov    $0x47d,%esi
    1723:	lea    0x9ee(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    172a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    172f:	nop
    1730:	lea    0x8cd(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1737:	lea    0xa02(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    173e:	mov    $0x46a,%esi
    1743:	lea    0x9ce(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    174a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    174f:	nop
    1750:	ret
    1751:	cs nopw 0x0(%rax,%rax,1)
    175b:	nopl   0x0(%rax,%rax,1)
