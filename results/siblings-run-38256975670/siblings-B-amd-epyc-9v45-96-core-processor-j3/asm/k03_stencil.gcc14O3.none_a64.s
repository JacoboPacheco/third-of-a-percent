0000000000001680 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    (%rsi),%rdx
    1687:	mov    0x8(%rsi),%rax
    168b:	sub    %rdx,%rax
    168e:	mov    %rax,%r8
    1691:	sar    $0x2,%r8
    1695:	cmp    $0x8,%rax
    1699:	jbe    17d8 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x158>
    169f:	mov    (%rdi),%rcx
    16a2:	cmp    $0xc,%rax
    16a6:	jbe    1798 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x118>
    16ac:	mov    %rcx,%rax
    16af:	sub    %rdx,%rax
    16b2:	cmp    $0x10,%rax
    16b6:	jbe    1798 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x118>
    16bc:	mov    $0x3,%eax
    16c1:	cmp    %rax,%r8
    16c4:	cmovb  %rax,%r8
    16c8:	lea    -0x3(%r8),%rax
    16cc:	lea    -0x2(%r8),%rdi
    16d0:	cmp    $0x2,%rax
    16d4:	jbe    17e1 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x161>
    16da:	mov    %rdi,%rsi
    16dd:	xor    %eax,%eax
    16df:	shr    $0x2,%rsi
    16e3:	shl    $0x4,%rsi
    16e7:	data16 cs nopw 0x0(%rax,%rax,1)
    16f2:	data16 cs nopw 0x0(%rax,%rax,1)
    16fd:	nopl   (%rax)
    1700:	movdqu (%rdx,%rax,1),%xmm0
    1705:	movdqu 0x4(%rdx,%rax,1),%xmm2
    170b:	movdqu 0x8(%rdx,%rax,1),%xmm3
    1711:	paddd  %xmm2,%xmm0
    1715:	paddd  %xmm3,%xmm0
    1719:	movups %xmm0,0x4(%rcx,%rax,1)
    171e:	add    $0x10,%rax
    1722:	cmp    %rax,%rsi
    1725:	jne    1700 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    1727:	mov    %rdi,%rax
    172a:	and    $0xfffffffffffffffc,%rax
    172e:	and    $0x3,%edi
    1731:	lea    0x1(%rax),%rsi
    1735:	lea    0x2(%rax),%r9
    1739:	je     17e0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x160>
    173f:	sub    %rax,%r8
    1742:	lea    -0x2(%r8),%rdi
    1746:	cmp    $0x3,%r8
    174a:	je     1786 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x106>
    174c:	lea    0x0(,%rax,4),%r8
    1754:	movq   (%rdx,%rax,4),%xmm0
    1759:	movq   0x4(%rdx,%r8,1),%xmm1
    1760:	paddd  %xmm1,%xmm0
    1764:	movq   0x8(%rdx,%r8,1),%xmm1
    176b:	paddd  %xmm1,%xmm0
    176f:	movq   %xmm0,0x4(%rcx,%r8,1)
    1776:	test   $0x1,%dil
    177a:	je     17d8 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x158>
    177c:	and    $0xfffffffffffffffe,%rdi
    1780:	add    %rdi,%rsi
    1783:	add    %rdi,%r9
    1786:	mov    (%rdx,%rsi,4),%eax
    1789:	add    -0x4(%rdx,%rsi,4),%eax
    178d:	add    (%rdx,%r9,4),%eax
    1791:	mov    %eax,(%rcx,%rsi,4)
    1794:	ret
    1795:	nopl   (%rax)
    1798:	mov    $0x2,%eax
    179d:	nopl   (%rax)
    17a0:	data16 cs nopw 0x0(%rax,%rax,1)
    17ab:	data16 cs nopw 0x0(%rax,%rax,1)
    17b6:	cs nopw 0x0(%rax,%rax,1)
    17c0:	mov    -0x8(%rdx,%rax,4),%esi
    17c4:	add    -0x4(%rdx,%rax,4),%esi
    17c8:	add    (%rdx,%rax,4),%esi
    17cb:	mov    %esi,-0x4(%rcx,%rax,4)
    17cf:	add    $0x1,%rax
    17d3:	cmp    %r8,%rax
    17d6:	jb     17c0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x140>
    17d8:	ret
    17d9:	nopl   0x0(%rax)
    17e0:	ret
    17e1:	xor    %eax,%eax
    17e3:	mov    $0x1,%esi
    17e8:	mov    $0x2,%r9d
    17ee:	jmp    173f <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0xbf>
    17f3:	cs nopw 0x0(%rax,%rax,1)
    17fd:	nopl   (%rax)
