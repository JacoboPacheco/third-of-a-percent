0000000000001600 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    1600:	endbr64
    1604:	mov    (%rsi),%r8
    1607:	mov    0x8(%rsi),%rax
    160b:	sub    %r8,%rax
    160e:	mov    %rax,%r9
    1611:	sar    $0x2,%r9
    1615:	cmp    $0x8,%rax
    1619:	jbe    1680 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    161b:	mov    (%rdi),%rsi
    161e:	mov    0x8(%rdi),%rcx
    1622:	mov    $0x1,%eax
    1627:	sub    %rsi,%rcx
    162a:	sar    $0x2,%rcx
    162e:	cmp    %rcx,%rax
    1631:	jae    1659 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x59>
    1633:	mov    (%r8,%rax,4),%edx
    1637:	add    -0x4(%r8,%rax,4),%edx
    163c:	add    0x4(%r8,%rax,4),%edx
    1641:	mov    %edx,(%rsi,%rax,4)
    1644:	lea    0x1(%rax),%rdx
    1648:	add    $0x2,%rax
    164c:	cmp    %r9,%rax
    164f:	jae    1680 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    1651:	mov    %rdx,%rax
    1654:	cmp    %rcx,%rax
    1657:	jb     1633 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x33>
    1659:	sub    $0x8,%rsp
    165d:	lea    0x9a0(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1664:	lea    0x9d5(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    166b:	mov    $0x46a,%esi
    1670:	lea    0xa89(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    1677:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    167c:	nopl   0x0(%rax)
    1680:	ret
    1681:	cs nopw 0x0(%rax,%rax,1)
    168b:	nopl   0x0(%rax,%rax,1)
