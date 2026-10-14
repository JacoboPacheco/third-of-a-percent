0000000000001740 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    1740:	endbr64
    1744:	mov    0x8(%rsi),%r8
    1748:	mov    (%rsi),%rcx
    174b:	mov    %r8,%rax
    174e:	sub    %rcx,%rax
    1751:	mov    %rax,%r9
    1754:	sar    $0x2,%r9
    1758:	cmp    %rcx,%r8
    175b:	je     1852 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x112>
    1761:	mov    (%rdx),%rsi
    1764:	mov    (%rdi),%rdx
    1767:	cmp    $0x4,%rax
    176b:	jbe    1820 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xe0>
    1771:	lea    0x4(%rsi),%r8
    1775:	mov    %rdx,%rdi
    1778:	sub    %r8,%rdi
    177b:	cmp    $0x8,%rdi
    177f:	jbe    1820 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xe0>
    1785:	lea    0x4(%rcx),%r8
    1789:	mov    %rdx,%rdi
    178c:	sub    %r8,%rdi
    178f:	cmp    $0x8,%rdi
    1793:	jbe    1820 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xe0>
    1799:	test   %rax,%rax
    179c:	mov    $0x1,%r8d
    17a2:	cmovne %r9,%r8
    17a6:	cmp    $0xc,%rax
    17aa:	jbe    1859 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x119>
    17b0:	mov    %r8,%rdi
    17b3:	xor    %eax,%eax
    17b5:	shr    $0x2,%rdi
    17b9:	shl    $0x4,%rdi
    17bd:	nopl   (%rax)
    17c0:	movdqu (%rcx,%rax,1),%xmm0
    17c5:	movdqu (%rsi,%rax,1),%xmm2
    17ca:	paddd  %xmm2,%xmm0
    17ce:	movups %xmm0,(%rdx,%rax,1)
    17d2:	add    $0x10,%rax
    17d6:	cmp    %rdi,%rax
    17d9:	jne    17c0 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x80>
    17db:	mov    %r8,%rax
    17de:	and    $0xfffffffffffffffc,%rax
    17e2:	test   $0x3,%r8b
    17e6:	je     1858 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x118>
    17e8:	sub    %rax,%r8
    17eb:	cmp    $0x1,%r8
    17ef:	je     1811 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xd1>
    17f1:	movq   (%rcx,%rax,4),%xmm0
    17f6:	movq   (%rsi,%rax,4),%xmm1
    17fb:	paddd  %xmm1,%xmm0
    17ff:	movq   %xmm0,(%rdx,%rax,4)
    1804:	test   $0x1,%r8b
    1808:	je     1852 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x112>
    180a:	and    $0xfffffffffffffffe,%r8
    180e:	add    %r8,%rax
    1811:	mov    (%rsi,%rax,4),%esi
    1814:	add    (%rcx,%rax,4),%esi
    1817:	mov    %esi,(%rdx,%rax,4)
    181a:	ret
    181b:	nopl   0x0(%rax,%rax,1)
    1820:	xor    %eax,%eax
    1822:	data16 cs nopw 0x0(%rax,%rax,1)
    182d:	data16 cs nopw 0x0(%rax,%rax,1)
    1838:	nopl   0x0(%rax,%rax,1)
    1840:	mov    (%rsi,%rax,4),%edi
    1843:	add    (%rcx,%rax,4),%edi
    1846:	mov    %edi,(%rdx,%rax,4)
    1849:	add    $0x1,%rax
    184d:	cmp    %r9,%rax
    1850:	jb     1840 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x100>
    1852:	ret
    1853:	nopl   0x0(%rax,%rax,1)
    1858:	ret
    1859:	xor    %eax,%eax
    185b:	jmp    17e8 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xa8>
    185d:	nopl   (%rax)
