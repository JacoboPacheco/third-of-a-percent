00000000000015c0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    15c0:	endbr64
    15c4:	mov    0x8(%rdi),%rax
    15c8:	mov    (%rdi),%rdi
    15cb:	mov    %rax,%r8
    15ce:	sub    %rdi,%r8
    15d1:	sar    $0x2,%r8
    15d5:	cmp    %rdi,%rax
    15d8:	je     1613 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x53>
    15da:	mov    (%rsi),%rcx
    15dd:	xor    %eax,%eax
    15df:	nop
    15e0:	data16 cs nopw 0x0(%rax,%rax,1)
    15eb:	data16 cs nopw 0x0(%rax,%rax,1)
    15f6:	cs nopw 0x0(%rax,%rax,1)
    1600:	mov    0x4(%rcx,%rax,8),%edx
    1604:	add    (%rcx,%rax,8),%edx
    1607:	mov    %edx,(%rdi,%rax,4)
    160a:	add    $0x1,%rax
    160e:	cmp    %r8,%rax
    1611:	jb     1600 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x40>
    1613:	ret
    1614:	cs nopw 0x0(%rax,%rax,1)
    161e:	xchg   %ax,%ax
