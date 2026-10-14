0000000000001640 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    1640:	endbr64
    1644:	mov    (%rsi),%rdx
    1647:	mov    0x8(%rsi),%rax
    164b:	sub    %rdx,%rax
    164e:	mov    %rax,%r8
    1651:	sar    $0x2,%r8
    1655:	cmp    $0x8,%rax
    1659:	jbe    1778 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x138>
    165f:	mov    (%rdi),%rcx
    1662:	cmp    $0xc,%rax
    1666:	jbe    1758 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x118>
    166c:	mov    %rcx,%rax
    166f:	sub    %rdx,%rax
    1672:	cmp    $0x10,%rax
    1676:	jbe    1758 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x118>
    167c:	mov    $0x3,%eax
    1681:	cmp    %rax,%r8
    1684:	cmovb  %rax,%r8
    1688:	lea    -0x3(%r8),%rax
    168c:	lea    -0x2(%r8),%rdi
    1690:	cmp    $0x2,%rax
    1694:	jbe    1781 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x141>
    169a:	mov    %rdi,%rsi
    169d:	xor    %eax,%eax
    169f:	shr    $0x2,%rsi
    16a3:	shl    $0x4,%rsi
    16a7:	data16 cs nopw 0x0(%rax,%rax,1)
    16b2:	data16 cs nopw 0x0(%rax,%rax,1)
    16bd:	nopl   (%rax)
    16c0:	movdqu (%rdx,%rax,1),%xmm0
    16c5:	movdqu 0x4(%rdx,%rax,1),%xmm2
    16cb:	movdqu 0x8(%rdx,%rax,1),%xmm3
    16d1:	paddd  %xmm2,%xmm0
    16d5:	paddd  %xmm3,%xmm0
    16d9:	movups %xmm0,0x4(%rcx,%rax,1)
    16de:	add    $0x10,%rax
    16e2:	cmp    %rax,%rsi
    16e5:	jne    16c0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    16e7:	mov    %rdi,%rax
    16ea:	and    $0xfffffffffffffffc,%rax
    16ee:	and    $0x3,%edi
    16f1:	lea    0x1(%rax),%rsi
    16f5:	lea    0x2(%rax),%r9
    16f9:	je     1780 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x140>
    16ff:	sub    %rax,%r8
    1702:	lea    -0x2(%r8),%rdi
    1706:	cmp    $0x3,%r8
    170a:	je     1746 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x106>
    170c:	lea    0x0(,%rax,4),%r8
    1714:	movq   (%rdx,%rax,4),%xmm0
    1719:	movq   0x4(%rdx,%r8,1),%xmm1
    1720:	paddd  %xmm1,%xmm0
    1724:	movq   0x8(%rdx,%r8,1),%xmm1
    172b:	paddd  %xmm1,%xmm0
    172f:	movq   %xmm0,0x4(%rcx,%r8,1)
    1736:	test   $0x1,%dil
    173a:	je     1778 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x138>
    173c:	and    $0xfffffffffffffffe,%rdi
    1740:	add    %rdi,%rsi
    1743:	add    %rdi,%r9
    1746:	mov    (%rdx,%rsi,4),%eax
    1749:	add    -0x4(%rdx,%rsi,4),%eax
    174d:	add    (%rdx,%r9,4),%eax
    1751:	mov    %eax,(%rcx,%rsi,4)
    1754:	ret
    1755:	nopl   (%rax)
    1758:	mov    $0x2,%eax
    175d:	nopl   (%rax)
    1760:	mov    -0x8(%rdx,%rax,4),%esi
    1764:	add    -0x4(%rdx,%rax,4),%esi
    1768:	add    (%rdx,%rax,4),%esi
    176b:	mov    %esi,-0x4(%rcx,%rax,4)
    176f:	add    $0x1,%rax
    1773:	cmp    %r8,%rax
    1776:	jb     1760 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x120>
    1778:	ret
    1779:	nopl   0x0(%rax)
    1780:	ret
    1781:	xor    %eax,%eax
    1783:	mov    $0x1,%esi
    1788:	mov    $0x2,%r9d
    178e:	jmp    16ff <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0xbf>
    1793:	cs nopw 0x0(%rax,%rax,1)
    179d:	nopl   (%rax)
