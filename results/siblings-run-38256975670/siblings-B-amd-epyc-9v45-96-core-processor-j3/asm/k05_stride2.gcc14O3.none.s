0000000000001640 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    1640:	endbr64
    1644:	mov    0x8(%rdi),%rdx
    1648:	mov    (%rdi),%rcx
    164b:	mov    %rdx,%rax
    164e:	sub    %rcx,%rax
    1651:	mov    %rax,%rdi
    1654:	sar    $0x2,%rdi
    1658:	cmp    %rcx,%rdx
    165b:	je     17b3 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x173>
    1661:	mov    (%rsi),%rdx
    1664:	cmp    $0xc,%rax
    1668:	jbe    1780 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x140>
    166e:	test   %rax,%rax
    1671:	lea    0x0(,%rdi,8),%rsi
    1679:	mov    $0x8,%r8d
    167f:	cmove  %r8,%rsi
    1683:	setne  %r9b
    1687:	add    %rdx,%rsi
    168a:	cmp    %rsi,%rcx
    168d:	jae    16a7 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x67>
    168f:	test   %rax,%rax
    1692:	mov    $0x4,%esi
    1697:	cmove  %rsi,%rax
    169b:	add    %rcx,%rax
    169e:	cmp    %rax,%rdx
    16a1:	jb     1780 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x140>
    16a7:	test   %r9b,%r9b
    16aa:	mov    $0x1,%r8d
    16b0:	cmovne %rdi,%r8
    16b4:	xor    %eax,%eax
    16b6:	mov    %r8,%rsi
    16b9:	shr    $0x2,%rsi
    16bd:	shl    $0x4,%rsi
    16c1:	data16 cs nopw 0x0(%rax,%rax,1)
    16cc:	data16 cs nopw 0x0(%rax,%rax,1)
    16d7:	data16 cs nopw 0x0(%rax,%rax,1)
    16e2:	data16 cs nopw 0x0(%rax,%rax,1)
    16ed:	data16 cs nopw 0x0(%rax,%rax,1)
    16f8:	nopl   0x0(%rax,%rax,1)
    1700:	movdqu (%rdx,%rax,2),%xmm0
    1705:	movdqu 0x10(%rdx,%rax,2),%xmm2
    170b:	movdqa %xmm0,%xmm1
    170f:	shufps $0xdd,%xmm2,%xmm0
    1713:	shufps $0x88,%xmm2,%xmm1
    1717:	paddd  %xmm1,%xmm0
    171b:	movups %xmm0,(%rcx,%rax,1)
    171f:	add    $0x10,%rax
    1723:	cmp    %rax,%rsi
    1726:	jne    1700 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0xc0>
    1728:	mov    %r8,%rax
    172b:	and    $0xfffffffffffffffc,%rax
    172f:	and    $0x3,%r8d
    1733:	je     17b3 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x173>
    1735:	mov    (%rdx,%rax,8),%esi
    1738:	add    0x4(%rdx,%rax,8),%esi
    173c:	lea    0x0(,%rax,8),%r8
    1744:	lea    0x0(,%rax,4),%r9
    174c:	mov    %esi,(%rcx,%rax,4)
    174f:	lea    0x1(%rax),%rsi
    1753:	cmp    %rdi,%rsi
    1756:	jae    17b3 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x173>
    1758:	mov    0xc(%rdx,%r8,1),%esi
    175d:	add    $0x2,%rax
    1761:	add    0x8(%rdx,%r8,1),%esi
    1766:	mov    %esi,0x4(%rcx,%r9,1)
    176b:	cmp    %rdi,%rax
    176e:	jae    17b3 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x173>
    1770:	mov    0x14(%rdx,%r8,1),%eax
    1775:	add    0x10(%rdx,%r8,1),%eax
    177a:	mov    %eax,0x8(%rcx,%r9,1)
    177f:	ret
    1780:	xor    %eax,%eax
    1782:	data16 cs nopw 0x0(%rax,%rax,1)
    178d:	data16 cs nopw 0x0(%rax,%rax,1)
    1798:	nopl   0x0(%rax,%rax,1)
    17a0:	mov    0x4(%rdx,%rax,8),%esi
    17a4:	add    (%rdx,%rax,8),%esi
    17a7:	mov    %esi,(%rcx,%rax,4)
    17aa:	add    $0x1,%rax
    17ae:	cmp    %rdi,%rax
    17b1:	jb     17a0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x160>
    17b3:	ret
    17b4:	cs nopw 0x0(%rax,%rax,1)
    17be:	xchg   %ax,%ax
