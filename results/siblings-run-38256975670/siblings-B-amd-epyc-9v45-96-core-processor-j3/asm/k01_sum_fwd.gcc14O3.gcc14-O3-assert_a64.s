00000000000015c0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE>:
    15c0:	endbr64
    15c4:	mov    0x8(%rdi),%rdx
    15c8:	mov    (%rdi),%rcx
    15cb:	mov    %rdx,%rax
    15ce:	sub    %rcx,%rax
    15d1:	mov    %rax,%rdi
    15d4:	sar    $0x2,%rdi
    15d8:	cmp    %rcx,%rdx
    15db:	je     16c0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x100>
    15e1:	test   %rax,%rax
    15e4:	mov    $0x1,%esi
    15e9:	cmovne %rdi,%rsi
    15ed:	cmp    $0xc,%rax
    15f1:	jbe    16d0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x110>
    15f7:	mov    %rsi,%rdx
    15fa:	pxor   %xmm1,%xmm1
    15fe:	mov    %rcx,%rax
    1601:	shr    $0x2,%rdx
    1605:	pxor   %xmm4,%xmm4
    1609:	shl    $0x4,%rdx
    160d:	add    %rcx,%rdx
    1610:	data16 cs nopw 0x0(%rax,%rax,1)
    161b:	data16 cs nopw 0x0(%rax,%rax,1)
    1626:	data16 cs nopw 0x0(%rax,%rax,1)
    1631:	data16 cs nopw 0x0(%rax,%rax,1)
    163c:	nopl   0x0(%rax)
    1640:	movdqu (%rax),%xmm0
    1644:	movdqa %xmm4,%xmm2
    1648:	add    $0x10,%rax
    164c:	pcmpgtd %xmm0,%xmm2
    1650:	movdqa %xmm0,%xmm3
    1654:	punpckldq %xmm2,%xmm3
    1658:	punpckhdq %xmm2,%xmm0
    165c:	paddq  %xmm3,%xmm1
    1660:	paddq  %xmm0,%xmm1
    1664:	cmp    %rax,%rdx
    1667:	jne    1640 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x80>
    1669:	movdqa %xmm1,%xmm0
    166d:	mov    %rsi,%rdx
    1670:	psrldq $0x8,%xmm0
    1675:	and    $0xfffffffffffffffc,%rdx
    1679:	and    $0x3,%esi
    167c:	paddq  %xmm0,%xmm1
    1680:	movq   %xmm1,%rax
    1685:	je     16c8 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x108>
    1687:	movslq (%rcx,%rdx,4),%r8
    168b:	lea    0x0(,%rdx,4),%rsi
    1693:	add    %r8,%rax
    1696:	lea    0x1(%rdx),%r8
    169a:	cmp    %rdi,%r8
    169d:	jae    16c2 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x102>
    169f:	movslq 0x4(%rcx,%rsi,1),%r8
    16a4:	add    $0x2,%rdx
    16a8:	add    %r8,%rax
    16ab:	cmp    %rdi,%rdx
    16ae:	jae    16c2 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x102>
    16b0:	movslq 0x8(%rcx,%rsi,1),%rdx
    16b5:	add    %rdx,%rax
    16b8:	ret
    16b9:	nopl   0x0(%rax)
    16c0:	xor    %eax,%eax
    16c2:	ret
    16c3:	nopl   0x0(%rax,%rax,1)
    16c8:	ret
    16c9:	nopl   0x0(%rax)
    16d0:	xor    %edx,%edx
    16d2:	xor    %eax,%eax
    16d4:	jmp    1687 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0xc7>
