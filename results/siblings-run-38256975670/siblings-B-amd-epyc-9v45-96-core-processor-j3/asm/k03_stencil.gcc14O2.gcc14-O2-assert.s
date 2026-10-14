00000000000015c0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    15c0:	endbr64
    15c4:	mov    (%rsi),%r8
    15c7:	mov    0x8(%rsi),%rax
    15cb:	sub    %r8,%rax
    15ce:	mov    %rax,%r9
    15d1:	sar    $0x2,%r9
    15d5:	cmp    $0x8,%rax
    15d9:	jbe    1640 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    15db:	mov    (%rdi),%rsi
    15de:	mov    0x8(%rdi),%rcx
    15e2:	mov    $0x1,%eax
    15e7:	sub    %rsi,%rcx
    15ea:	sar    $0x2,%rcx
    15ee:	cmp    %rcx,%rax
    15f1:	jae    1619 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x59>
    15f3:	mov    (%r8,%rax,4),%edx
    15f7:	add    -0x4(%r8,%rax,4),%edx
    15fc:	add    0x4(%r8,%rax,4),%edx
    1601:	mov    %edx,(%rsi,%rax,4)
    1604:	lea    0x1(%rax),%rdx
    1608:	add    $0x2,%rax
    160c:	cmp    %r9,%rax
    160f:	jae    1640 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    1611:	mov    %rdx,%rax
    1614:	cmp    %rcx,%rax
    1617:	jb     15f3 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x33>
    1619:	sub    $0x8,%rsp
    161d:	lea    0x9e0(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1624:	lea    0xa15(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    162b:	mov    $0x46a,%esi
    1630:	lea    0xac9(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    1637:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    163c:	nopl   0x0(%rax)
    1640:	ret
    1641:	cs nopw 0x0(%rax,%rax,1)
    164b:	nopl   0x0(%rax,%rax,1)
