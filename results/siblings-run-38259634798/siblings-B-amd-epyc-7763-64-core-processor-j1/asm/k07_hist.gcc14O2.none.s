0000000000001640 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    1640:	endbr64
    1644:	mov    0x8(%rsi),%rax
    1648:	mov    (%rsi),%rsi
    164b:	mov    %rax,%r8
    164e:	sub    %rsi,%r8
    1651:	sar    $0x2,%r8
    1655:	cmp    %rsi,%rax
    1658:	je     1671 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x31>
    165a:	mov    (%rdi),%rcx
    165d:	xor    %eax,%eax
    165f:	nop
    1660:	movzbl (%rsi,%rax,4),%edx
    1664:	add    $0x1,%rax
    1668:	addl   $0x1,(%rcx,%rdx,4)
    166c:	cmp    %r8,%rax
    166f:	jb     1660 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x20>
    1671:	ret
    1672:	cs nopw 0x0(%rax,%rax,1)
    167c:	nopl   0x0(%rax)
