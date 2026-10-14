0000000000001580 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    1580:	endbr64
    1584:	mov    (%rsi),%rcx
    1587:	mov    0x8(%rsi),%rax
    158b:	sub    %rcx,%rax
    158e:	mov    %rax,%rsi
    1591:	sar    $0x2,%rsi
    1595:	cmp    $0x8,%rax
    1599:	jbe    15d8 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x58>
    159b:	mov    (%rdi),%rdi
    159e:	mov    $0x2,%eax
    15a3:	data16 cs nopw 0x0(%rax,%rax,1)
    15ae:	data16 cs nopw 0x0(%rax,%rax,1)
    15b9:	nopl   0x0(%rax)
    15c0:	mov    -0x4(%rcx,%rax,4),%edx
    15c4:	add    -0x8(%rcx,%rax,4),%edx
    15c8:	add    (%rcx,%rax,4),%edx
    15cb:	mov    %edx,-0x4(%rdi,%rax,4)
    15cf:	add    $0x1,%rax
    15d3:	cmp    %rsi,%rax
    15d6:	jb     15c0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x40>
    15d8:	ret
    15d9:	nopl   0x0(%rax)
