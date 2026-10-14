0000000000001600 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    1600:	endbr64
    1604:	mov    0x8(%rdi),%rax
    1608:	mov    (%rdi),%r8
    160b:	mov    %rax,%r9
    160e:	sub    %r8,%r9
    1611:	sar    $0x2,%r9
    1615:	cmp    %r8,%rax
    1618:	je     1652 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x52>
    161a:	mov    (%rsi),%rdi
    161d:	mov    0x8(%rsi),%rcx
    1621:	xor    %eax,%eax
    1623:	sub    %rdi,%rcx
    1626:	sar    $0x2,%rcx
    162a:	mov    %rcx,%rsi
    162d:	shr    $1,%rsi
    1630:	lea    (%rax,%rax,1),%rdx
    1634:	cmp    %rcx,%rdx
    1637:	jae    1658 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    1639:	mov    (%rdi,%rax,8),%edx
    163c:	cmp    %rsi,%rax
    163f:	je     1658 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    1641:	add    0x4(%rdi,%rax,8),%edx
    1645:	mov    %edx,(%r8,%rax,4)
    1649:	add    $0x1,%rax
    164d:	cmp    %r9,%rax
    1650:	jb     1630 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x30>
    1652:	ret
    1653:	nopl   0x0(%rax,%rax,1)
    1658:	sub    $0x8,%rsp
    165c:	lea    0x9a1(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1663:	lea    0x9d6(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    166a:	mov    $0x47d,%esi
    166f:	lea    0xaa2(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1676:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    167b:	nopl   0x0(%rax,%rax,1)
