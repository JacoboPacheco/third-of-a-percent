0000000000001680 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    1680:	endbr64
    1684:	mov    0x8(%rsi),%rax
    1688:	mov    (%rsi),%r9
    168b:	mov    %rax,%r10
    168e:	sub    %r9,%r10
    1691:	sar    $0x2,%r10
    1695:	cmp    %r9,%rax
    1698:	je     1730 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    169e:	sub    $0x8,%rsp
    16a2:	mov    (%rdx),%r11
    16a5:	mov    0x8(%rdx),%rsi
    16a9:	xor    %eax,%eax
    16ab:	sub    %r11,%rsi
    16ae:	sar    $0x2,%rsi
    16b2:	mov    (%r9,%rax,4),%edx
    16b6:	cmp    %rax,%rsi
    16b9:	je     16f0 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x70>
    16bb:	mov    (%r11,%rax,4),%ecx
    16bf:	mov    (%rdi),%r8
    16c2:	add    %edx,%ecx
    16c4:	mov    0x8(%rdi),%rdx
    16c8:	sub    %r8,%rdx
    16cb:	sar    $0x2,%rdx
    16cf:	cmp    %rdx,%rax
    16d2:	jae    1710 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x90>
    16d4:	mov    %ecx,(%r8,%rax,4)
    16d8:	add    $0x1,%rax
    16dc:	cmp    %r10,%rax
    16df:	jb     16b2 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x32>
    16e1:	add    $0x8,%rsp
    16e5:	ret
    16e6:	cs nopw 0x0(%rax,%rax,1)
    16f0:	lea    0x90d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    16f7:	lea    0x942(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    16fe:	mov    $0x47d,%esi
    1703:	lea    0xa0e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    170a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    170f:	nop
    1710:	lea    0x8ed(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1717:	lea    0xa22(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    171e:	mov    $0x46a,%esi
    1723:	lea    0x9ee(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    172a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    172f:	nop
    1730:	ret
    1731:	cs nopw 0x0(%rax,%rax,1)
    173b:	nopl   0x0(%rax,%rax,1)
