0000000000001680 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    0x8(%rdi),%rdx
    1688:	mov    (%rdi),%rcx
    168b:	mov    %rdx,%rax
    168e:	sub    %rcx,%rax
    1691:	mov    %rax,%rdi
    1694:	sar    $0x2,%rdi
    1698:	cmp    %rcx,%rdx
    169b:	je     1813 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x193>
    16a1:	mov    (%rsi),%rdx
    16a4:	cmp    $0xc,%rax
    16a8:	jbe    17c8 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x148>
    16ae:	test   %rax,%rax
    16b1:	lea    0x0(,%rdi,8),%rsi
    16b9:	mov    $0x8,%r8d
    16bf:	cmove  %r8,%rsi
    16c3:	setne  %r9b
    16c7:	add    %rdx,%rsi
    16ca:	cmp    %rsi,%rcx
    16cd:	jae    16e7 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x67>
    16cf:	test   %rax,%rax
    16d2:	mov    $0x4,%esi
    16d7:	cmove  %rsi,%rax
    16db:	add    %rcx,%rax
    16de:	cmp    %rax,%rdx
    16e1:	jb     17c8 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x148>
    16e7:	test   %r9b,%r9b
    16ea:	mov    $0x1,%r8d
    16f0:	cmovne %rdi,%r8
    16f4:	xor    %eax,%eax
    16f6:	mov    %r8,%rsi
    16f9:	shr    $0x2,%rsi
    16fd:	shl    $0x4,%rsi
    1701:	data16 cs nopw 0x0(%rax,%rax,1)
    170c:	data16 cs nopw 0x0(%rax,%rax,1)
    1717:	data16 cs nopw 0x0(%rax,%rax,1)
    1722:	data16 cs nopw 0x0(%rax,%rax,1)
    172d:	data16 cs nopw 0x0(%rax,%rax,1)
    1738:	nopl   0x0(%rax,%rax,1)
    1740:	movdqu (%rdx,%rax,2),%xmm0
    1745:	movdqu 0x10(%rdx,%rax,2),%xmm2
    174b:	movdqa %xmm0,%xmm1
    174f:	shufps $0xdd,%xmm2,%xmm0
    1753:	shufps $0x88,%xmm2,%xmm1
    1757:	paddd  %xmm1,%xmm0
    175b:	movups %xmm0,(%rcx,%rax,1)
    175f:	add    $0x10,%rax
    1763:	cmp    %rax,%rsi
    1766:	jne    1740 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0xc0>
    1768:	mov    %r8,%rax
    176b:	and    $0xfffffffffffffffc,%rax
    176f:	and    $0x3,%r8d
    1773:	je     1813 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x193>
    1779:	mov    (%rdx,%rax,8),%esi
    177c:	add    0x4(%rdx,%rax,8),%esi
    1780:	lea    0x0(,%rax,8),%r8
    1788:	lea    0x0(,%rax,4),%r9
    1790:	mov    %esi,(%rcx,%rax,4)
    1793:	lea    0x1(%rax),%rsi
    1797:	cmp    %rdi,%rsi
    179a:	jae    1813 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x193>
    179c:	mov    0xc(%rdx,%r8,1),%esi
    17a1:	add    $0x2,%rax
    17a5:	add    0x8(%rdx,%r8,1),%esi
    17aa:	mov    %esi,0x4(%rcx,%r9,1)
    17af:	cmp    %rdi,%rax
    17b2:	jae    1813 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x193>
    17b4:	mov    0x14(%rdx,%r8,1),%eax
    17b9:	add    0x10(%rdx,%r8,1),%eax
    17be:	mov    %eax,0x8(%rcx,%r9,1)
    17c3:	ret
    17c4:	nopl   0x0(%rax)
    17c8:	xor    %eax,%eax
    17ca:	data16 cs nopw 0x0(%rax,%rax,1)
    17d5:	data16 cs nopw 0x0(%rax,%rax,1)
    17e0:	data16 cs nopw 0x0(%rax,%rax,1)
    17eb:	data16 cs nopw 0x0(%rax,%rax,1)
    17f6:	cs nopw 0x0(%rax,%rax,1)
    1800:	mov    0x4(%rdx,%rax,8),%esi
    1804:	add    (%rdx,%rax,8),%esi
    1807:	mov    %esi,(%rcx,%rax,4)
    180a:	add    $0x1,%rax
    180e:	cmp    %rdi,%rax
    1811:	jb     1800 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x180>
    1813:	ret
    1814:	cs nopw 0x0(%rax,%rax,1)
    181e:	xchg   %ax,%ax
