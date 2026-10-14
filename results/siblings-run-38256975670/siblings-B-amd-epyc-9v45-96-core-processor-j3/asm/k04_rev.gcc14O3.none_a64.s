0000000000001680 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    (%rsi),%r9
    1687:	mov    0x8(%rsi),%rdx
    168b:	sub    %r9,%rdx
    168e:	mov    %rdx,%r8
    1691:	sar    $0x2,%r8
    1695:	mov    %r8,%rsi
    1698:	lea    -0x1(%r8),%rcx
    169c:	je     17d0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x150>
    16a2:	mov    (%rdi),%r10
    16a5:	cmp    $0x4,%rdx
    16a9:	je     1780 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x100>
    16af:	lea    -0x8(%rdx),%r11
    16b3:	lea    -0x4(%r10,%rdx,1),%rax
    16b8:	lea    (%r9,%r11,1),%rdi
    16bc:	sub    %rdi,%rax
    16bf:	add    $0x8,%rax
    16c3:	cmp    $0x8,%rax
    16c7:	jbe    17c0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x140>
    16cd:	cmp    $0x2,%rcx
    16d1:	jbe    17d1 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x151>
    16d7:	shr    $0x2,%rsi
    16db:	sub    $0x10,%rdx
    16df:	xor    %eax,%eax
    16e1:	neg    %rsi
    16e4:	lea    (%r9,%rdx,1),%rdi
    16e8:	add    %r10,%rdx
    16eb:	shl    $0x4,%rsi
    16ef:	data16 cs nopw 0x0(%rax,%rax,1)
    16fa:	nopw   0x0(%rax,%rax,1)
    1700:	movdqu (%rdi,%rax,1),%xmm1
    1705:	pshufd $0x1b,%xmm1,%xmm0
    170a:	pslld  $0x1,%xmm0
    170f:	pshufd $0x1b,%xmm0,%xmm0
    1714:	movups %xmm0,(%rdx,%rax,1)
    1718:	sub    $0x10,%rax
    171c:	cmp    %rsi,%rax
    171f:	jne    1700 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x80>
    1721:	mov    %r8,%rax
    1724:	and    $0xfffffffffffffffc,%rax
    1728:	test   $0x3,%r8b
    172c:	je     17d0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x150>
    1732:	mov    %r8,%rsi
    1735:	sub    %rax,%rcx
    1738:	sub    %rax,%rsi
    173b:	cmp    $0x1,%rsi
    173f:	je     1770 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0xf0>
    1741:	neg    %rax
    1744:	lea    (%r11,%rax,4),%rax
    1748:	movq   (%r9,%rax,1),%xmm0
    174e:	pshufd $0xe1,%xmm0,%xmm0
    1753:	pslld  $0x1,%xmm0
    1758:	pshufd $0xe1,%xmm0,%xmm0
    175d:	movq   %xmm0,(%r10,%rax,1)
    1763:	test   $0x1,%sil
    1767:	je     17d0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x150>
    1769:	and    $0xfffffffffffffffe,%rsi
    176d:	sub    %rsi,%rcx
    1770:	mov    (%r9,%rcx,4),%eax
    1774:	add    %eax,%eax
    1776:	mov    %eax,(%r10,%rcx,4)
    177a:	ret
    177b:	nopl   0x0(%rax,%rax,1)
    1780:	xor    %ecx,%ecx
    1782:	data16 cs nopw 0x0(%rax,%rax,1)
    178d:	nopl   (%rax)
    1790:	data16 cs nopw 0x0(%rax,%rax,1)
    179b:	data16 cs nopw 0x0(%rax,%rax,1)
    17a6:	data16 cs nopw 0x0(%rax,%rax,1)
    17b1:	data16 cs nopw 0x0(%rax,%rax,1)
    17bc:	nopl   0x0(%rax)
    17c0:	mov    (%r9,%rcx,4),%eax
    17c4:	add    %eax,%eax
    17c6:	mov    %eax,(%r10,%rcx,4)
    17ca:	sub    $0x1,%rcx
    17ce:	jae    17c0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x140>
    17d0:	ret
    17d1:	xor    %eax,%eax
    17d3:	jmp    1741 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0xc1>
    17d8:	nopl   0x0(%rax,%rax,1)
