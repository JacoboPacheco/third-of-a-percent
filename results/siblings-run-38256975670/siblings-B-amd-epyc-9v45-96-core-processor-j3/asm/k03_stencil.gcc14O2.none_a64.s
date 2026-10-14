00000000000015c0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    15c0:	endbr64
    15c4:	mov    (%rsi),%rcx
    15c7:	mov    0x8(%rsi),%rax
    15cb:	sub    %rcx,%rax
    15ce:	mov    %rax,%rsi
    15d1:	sar    $0x2,%rsi
    15d5:	cmp    $0x8,%rax
    15d9:	jbe    1618 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x58>
    15db:	mov    (%rdi),%rdi
    15de:	mov    $0x2,%eax
    15e3:	data16 cs nopw 0x0(%rax,%rax,1)
    15ee:	data16 cs nopw 0x0(%rax,%rax,1)
    15f9:	nopl   0x0(%rax)
    1600:	mov    -0x4(%rcx,%rax,4),%edx
    1604:	add    -0x8(%rcx,%rax,4),%edx
    1608:	add    (%rcx,%rax,4),%edx
    160b:	mov    %edx,-0x4(%rdi,%rax,4)
    160f:	add    $0x1,%rax
    1613:	cmp    %rsi,%rax
    1616:	jb     1600 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x40>
    1618:	ret
    1619:	nopl   0x0(%rax)
