0000000000001580 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    1580:	endbr64
    1584:	mov    0x8(%rdi),%rax
    1588:	mov    (%rdi),%rdi
    158b:	mov    %rax,%r8
    158e:	sub    %rdi,%r8
    1591:	sar    $0x2,%r8
    1595:	cmp    %rdi,%rax
    1598:	je     15b3 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x33>
    159a:	mov    (%rsi),%rcx
    159d:	xor    %eax,%eax
    159f:	nop
    15a0:	mov    0x4(%rcx,%rax,8),%edx
    15a4:	add    (%rcx,%rax,8),%edx
    15a7:	mov    %edx,(%rdi,%rax,4)
    15aa:	add    $0x1,%rax
    15ae:	cmp    %r8,%rax
    15b1:	jb     15a0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x20>
    15b3:	ret
    15b4:	cs nopw 0x0(%rax,%rax,1)
    15be:	xchg   %ax,%ax
