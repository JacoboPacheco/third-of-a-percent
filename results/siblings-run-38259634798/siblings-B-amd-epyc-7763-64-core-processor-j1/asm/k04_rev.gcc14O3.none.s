0000000000001640 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    1640:	endbr64
    1644:	mov    (%rsi),%r9
    1647:	mov    0x8(%rsi),%rdx
    164b:	sub    %r9,%rdx
    164e:	mov    %rdx,%r8
    1651:	sar    $0x2,%r8
    1655:	mov    %r8,%rsi
    1658:	lea    -0x1(%r8),%rcx
    165c:	je     1760 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x120>
    1662:	mov    (%rdi),%r10
    1665:	cmp    $0x4,%rdx
    1669:	je     1740 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x100>
    166f:	lea    -0x8(%rdx),%r11
    1673:	lea    -0x4(%r10,%rdx,1),%rax
    1678:	lea    (%r9,%r11,1),%rdi
    167c:	sub    %rdi,%rax
    167f:	add    $0x8,%rax
    1683:	cmp    $0x8,%rax
    1687:	jbe    1750 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x110>
    168d:	cmp    $0x2,%rcx
    1691:	jbe    1761 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x121>
    1697:	shr    $0x2,%rsi
    169b:	sub    $0x10,%rdx
    169f:	xor    %eax,%eax
    16a1:	neg    %rsi
    16a4:	lea    (%r9,%rdx,1),%rdi
    16a8:	add    %r10,%rdx
    16ab:	shl    $0x4,%rsi
    16af:	data16 cs nopw 0x0(%rax,%rax,1)
    16ba:	nopw   0x0(%rax,%rax,1)
    16c0:	movdqu (%rdi,%rax,1),%xmm1
    16c5:	pshufd $0x1b,%xmm1,%xmm0
    16ca:	pslld  $0x1,%xmm0
    16cf:	pshufd $0x1b,%xmm0,%xmm0
    16d4:	movups %xmm0,(%rdx,%rax,1)
    16d8:	sub    $0x10,%rax
    16dc:	cmp    %rsi,%rax
    16df:	jne    16c0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x80>
    16e1:	mov    %r8,%rax
    16e4:	and    $0xfffffffffffffffc,%rax
    16e8:	test   $0x3,%r8b
    16ec:	je     1760 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x120>
    16ee:	mov    %r8,%rsi
    16f1:	sub    %rax,%rcx
    16f4:	sub    %rax,%rsi
    16f7:	cmp    $0x1,%rsi
    16fb:	je     172c <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0xec>
    16fd:	neg    %rax
    1700:	lea    (%r11,%rax,4),%rax
    1704:	movq   (%r9,%rax,1),%xmm0
    170a:	pshufd $0xe1,%xmm0,%xmm0
    170f:	pslld  $0x1,%xmm0
    1714:	pshufd $0xe1,%xmm0,%xmm0
    1719:	movq   %xmm0,(%r10,%rax,1)
    171f:	test   $0x1,%sil
    1723:	je     1760 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x120>
    1725:	and    $0xfffffffffffffffe,%rsi
    1729:	sub    %rsi,%rcx
    172c:	mov    (%r9,%rcx,4),%eax
    1730:	add    %eax,%eax
    1732:	mov    %eax,(%r10,%rcx,4)
    1736:	ret
    1737:	nopw   0x0(%rax,%rax,1)
    1740:	xor    %ecx,%ecx
    1742:	data16 cs nopw 0x0(%rax,%rax,1)
    174d:	nopl   (%rax)
    1750:	mov    (%r9,%rcx,4),%eax
    1754:	add    %eax,%eax
    1756:	mov    %eax,(%r10,%rcx,4)
    175a:	sub    $0x1,%rcx
    175e:	jae    1750 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x110>
    1760:	ret
    1761:	xor    %eax,%eax
    1763:	jmp    16fd <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0xbd>
    1765:	cs nopw 0x0(%rax,%rax,1)
    176f:	nop
