00000000000015c0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE>:
    15c0:	endbr64
    15c4:	mov    0x8(%rdi),%rax
    15c8:	mov    (%rdi),%rsi
    15cb:	mov    %rax,%rdi
    15ce:	sub    %rsi,%rdi
    15d1:	sar    $0x2,%rdi
    15d5:	cmp    %rsi,%rax
    15d8:	je     1618 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x58>
    15da:	xor    %eax,%eax
    15dc:	xor    %edx,%edx
    15de:	xchg   %ax,%ax
    15e0:	data16 cs nopw 0x0(%rax,%rax,1)
    15eb:	data16 cs nopw 0x0(%rax,%rax,1)
    15f6:	cs nopw 0x0(%rax,%rax,1)
    1600:	movslq (%rsi,%rax,4),%rcx
    1604:	add    $0x1,%rax
    1608:	add    %rcx,%rdx
    160b:	cmp    %rdi,%rax
    160e:	jb     1600 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x40>
    1610:	mov    %rdx,%rax
    1613:	ret
    1614:	nopl   0x0(%rax)
    1618:	xor    %edx,%edx
    161a:	mov    %rdx,%rax
    161d:	ret
    161e:	xchg   %ax,%ax
