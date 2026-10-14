0000000000001720 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    1720:	endbr64
    1724:	mov    0x8(%rsi),%r8
    1728:	mov    (%rsi),%rcx
    172b:	mov    %r8,%rax
    172e:	sub    %rcx,%rax
    1731:	mov    %rax,%r9
    1734:	sar    $0x2,%r9
    1738:	cmp    %rcx,%r8
    173b:	je     1832 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x112>
    1741:	mov    (%rdx),%rsi
    1744:	mov    (%rdi),%rdx
    1747:	cmp    $0x4,%rax
    174b:	jbe    1800 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xe0>
    1751:	lea    0x4(%rsi),%r8
    1755:	mov    %rdx,%rdi
    1758:	sub    %r8,%rdi
    175b:	cmp    $0x8,%rdi
    175f:	jbe    1800 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xe0>
    1765:	lea    0x4(%rcx),%r8
    1769:	mov    %rdx,%rdi
    176c:	sub    %r8,%rdi
    176f:	cmp    $0x8,%rdi
    1773:	jbe    1800 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xe0>
    1779:	test   %rax,%rax
    177c:	mov    $0x1,%r8d
    1782:	cmovne %r9,%r8
    1786:	cmp    $0xc,%rax
    178a:	jbe    1839 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x119>
    1790:	mov    %r8,%rdi
    1793:	xor    %eax,%eax
    1795:	shr    $0x2,%rdi
    1799:	shl    $0x4,%rdi
    179d:	nopl   (%rax)
    17a0:	movdqu (%rcx,%rax,1),%xmm0
    17a5:	movdqu (%rsi,%rax,1),%xmm2
    17aa:	paddd  %xmm2,%xmm0
    17ae:	movups %xmm0,(%rdx,%rax,1)
    17b2:	add    $0x10,%rax
    17b6:	cmp    %rdi,%rax
    17b9:	jne    17a0 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x80>
    17bb:	mov    %r8,%rax
    17be:	and    $0xfffffffffffffffc,%rax
    17c2:	test   $0x3,%r8b
    17c6:	je     1838 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x118>
    17c8:	sub    %rax,%r8
    17cb:	cmp    $0x1,%r8
    17cf:	je     17f1 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xd1>
    17d1:	movq   (%rcx,%rax,4),%xmm0
    17d6:	movq   (%rsi,%rax,4),%xmm1
    17db:	paddd  %xmm1,%xmm0
    17df:	movq   %xmm0,(%rdx,%rax,4)
    17e4:	test   $0x1,%r8b
    17e8:	je     1832 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x112>
    17ea:	and    $0xfffffffffffffffe,%r8
    17ee:	add    %r8,%rax
    17f1:	mov    (%rsi,%rax,4),%esi
    17f4:	add    (%rcx,%rax,4),%esi
    17f7:	mov    %esi,(%rdx,%rax,4)
    17fa:	ret
    17fb:	nopl   0x0(%rax,%rax,1)
    1800:	xor    %eax,%eax
    1802:	data16 cs nopw 0x0(%rax,%rax,1)
    180d:	data16 cs nopw 0x0(%rax,%rax,1)
    1818:	nopl   0x0(%rax,%rax,1)
    1820:	mov    (%rsi,%rax,4),%edi
    1823:	add    (%rcx,%rax,4),%edi
    1826:	mov    %edi,(%rdx,%rax,4)
    1829:	add    $0x1,%rax
    182d:	cmp    %r9,%rax
    1830:	jb     1820 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x100>
    1832:	ret
    1833:	nopl   0x0(%rax,%rax,1)
    1838:	ret
    1839:	xor    %eax,%eax
    183b:	jmp    17c8 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xa8>
    183d:	nopl   (%rax)
