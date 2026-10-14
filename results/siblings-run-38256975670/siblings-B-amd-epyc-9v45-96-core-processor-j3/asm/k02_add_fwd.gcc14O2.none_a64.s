0000000000001640 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    1640:	endbr64
    1644:	mov    0x8(%rsi),%rax
    1648:	mov    (%rsi),%rcx
    164b:	mov    %rax,%rsi
    164e:	sub    %rcx,%rsi
    1651:	sar    $0x2,%rsi
    1655:	cmp    %rcx,%rax
    1658:	je     1693 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x53>
    165a:	mov    (%rdx),%r8
    165d:	mov    (%rdi),%rdi
    1660:	xor    %eax,%eax
    1662:	data16 cs nopw 0x0(%rax,%rax,1)
    166d:	data16 cs nopw 0x0(%rax,%rax,1)
    1678:	nopl   0x0(%rax,%rax,1)
    1680:	mov    (%r8,%rax,4),%edx
    1684:	add    (%rcx,%rax,4),%edx
    1687:	mov    %edx,(%rdi,%rax,4)
    168a:	add    $0x1,%rax
    168e:	cmp    %rsi,%rax
    1691:	jb     1680 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x40>
    1693:	ret
    1694:	cs nopw 0x0(%rax,%rax,1)
    169e:	xchg   %ax,%ax
