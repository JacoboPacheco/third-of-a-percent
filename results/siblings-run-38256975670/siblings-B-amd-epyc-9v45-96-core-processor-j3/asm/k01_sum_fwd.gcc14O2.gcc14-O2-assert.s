0000000000001580 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE>:
    1580:	endbr64
    1584:	mov    0x8(%rdi),%rax
    1588:	mov    (%rdi),%rsi
    158b:	mov    %rax,%rdi
    158e:	sub    %rsi,%rdi
    1591:	sar    $0x2,%rdi
    1595:	cmp    %rsi,%rax
    1598:	je     15b8 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x38>
    159a:	xor    %eax,%eax
    159c:	xor    %edx,%edx
    159e:	xchg   %ax,%ax
    15a0:	movslq (%rsi,%rax,4),%rcx
    15a4:	add    $0x1,%rax
    15a8:	add    %rcx,%rdx
    15ab:	cmp    %rdi,%rax
    15ae:	jb     15a0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x20>
    15b0:	mov    %rdx,%rax
    15b3:	ret
    15b4:	nopl   0x0(%rax)
    15b8:	xor    %edx,%edx
    15ba:	mov    %rdx,%rax
    15bd:	ret
    15be:	xchg   %ax,%ax
