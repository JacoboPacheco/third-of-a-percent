0000000000001750 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    1750:	endbr64
    1754:	mov    0x8(%rdx),%rax
    1758:	mov    (%rdx),%r8
    175b:	mov    %rax,%r9
    175e:	sub    %r8,%r9
    1761:	sar    $0x2,%r9
    1765:	cmp    %r8,%rax
    1768:	je     1800 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    176e:	sub    $0x8,%rsp
    1772:	mov    (%rsi),%r11
    1775:	mov    0x8(%rsi),%rsi
    1779:	mov    %rdi,%rcx
    177c:	xor    %eax,%eax
    177e:	sub    %r11,%rsi
    1781:	sar    $0x2,%rsi
    1785:	movslq (%r8,%rax,4),%rdx
    1789:	cmp    %rsi,%rdx
    178c:	jae    17c0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x70>
    178e:	mov    (%r11,%rdx,4),%r10d
    1792:	mov    (%rcx),%rdi
    1795:	mov    0x8(%rcx),%rdx
    1799:	sub    %rdi,%rdx
    179c:	sar    $0x2,%rdx
    17a0:	cmp    %rdx,%rax
    17a3:	jae    17e0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x90>
    17a5:	mov    %r10d,(%rdi,%rax,4)
    17a9:	add    $0x1,%rax
    17ad:	cmp    %r9,%rax
    17b0:	jb     1785 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x35>
    17b2:	add    $0x8,%rsp
    17b6:	ret
    17b7:	nopw   0x0(%rax,%rax,1)
    17c0:	lea    0x83d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    17c7:	lea    0x872(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    17ce:	mov    $0x47d,%esi
    17d3:	lea    0x93e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    17da:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    17df:	nop
    17e0:	lea    0x81d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    17e7:	lea    0x952(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    17ee:	mov    $0x46a,%esi
    17f3:	lea    0x91e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    17fa:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    17ff:	nop
    1800:	ret
    1801:	cs nopw 0x0(%rax,%rax,1)
    180b:	nopl   0x0(%rax,%rax,1)
