0000000000001600 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    1600:	endbr64
    1604:	mov    (%rsi),%r8
    1607:	mov    0x8(%rsi),%rdx
    160b:	sub    %r8,%rdx
    160e:	sar    $0x2,%rdx
    1612:	je     1670 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    1614:	mov    (%rdi),%rsi
    1617:	mov    0x8(%rdi),%rcx
    161b:	lea    -0x1(%rdx),%rax
    161f:	mov    (%r8,%rax,4),%edi
    1623:	sub    %rsi,%rcx
    1626:	sar    $0x2,%rcx
    162a:	lea    (%rdi,%rdi,1),%edx
    162d:	cmp    %rcx,%rax
    1630:	jae    164d <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x4d>
    1632:	mov    %edx,(%rsi,%rax,4)
    1635:	lea    -0x1(%rax),%rdx
    1639:	test   %rax,%rax
    163c:	je     1670 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    163e:	mov    %rdx,%rax
    1641:	mov    (%r8,%rax,4),%edi
    1645:	lea    (%rdi,%rdi,1),%edx
    1648:	cmp    %rcx,%rax
    164b:	jb     1632 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x32>
    164d:	sub    $0x8,%rsp
    1651:	lea    0x9ac(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1658:	lea    0x9e1(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    165f:	mov    $0x46a,%esi
    1664:	lea    0xa95(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    166b:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1670:	ret
    1671:	cs nopw 0x0(%rax,%rax,1)
    167b:	nopl   0x0(%rax,%rax,1)
