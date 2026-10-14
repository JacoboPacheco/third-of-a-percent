00000000000015c0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE>:
    15c0:	endbr64
    15c4:	mov    0x8(%rdi),%rdx
    15c8:	mov    (%rdi),%rsi
    15cb:	mov    %rdx,%rax
    15ce:	sub    %rsi,%rax
    15d1:	mov    %rax,%rdi
    15d4:	sar    $0x2,%rdi
    15d8:	cmp    %rsi,%rdx
    15db:	je     16c0 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x100>
    15e1:	test   %rax,%rax
    15e4:	mov    $0x1,%ecx
    15e9:	cmovne %rdi,%rcx
    15ed:	cmp    $0xc,%rax
    15f1:	jbe    16c3 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x103>
    15f7:	mov    %rcx,%rdx
    15fa:	pxor   %xmm1,%xmm1
    15fe:	mov    %rsi,%rax
    1601:	shr    $0x2,%rdx
    1605:	pxor   %xmm4,%xmm4
    1609:	shl    $0x4,%rdx
    160d:	add    %rsi,%rdx
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
    166d:	psrldq $0x8,%xmm0
    1672:	paddq  %xmm0,%xmm1
    1676:	movq   %xmm1,%rax
    167b:	test   $0x3,%cl
    167e:	je     16c2 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x102>
    1680:	and    $0xfffffffffffffffc,%rcx
    1684:	mov    %rcx,%rdx
    1687:	movslq (%rsi,%rdx,4),%r8
    168b:	lea    0x0(,%rdx,4),%rcx
    1693:	add    %r8,%rax
    1696:	lea    0x1(%rdx),%r8
    169a:	cmp    %rdi,%r8
    169d:	jae    16c2 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x102>
    169f:	movslq 0x4(%rsi,%rcx,1),%r8
    16a4:	add    $0x2,%rdx
    16a8:	add    %r8,%rax
    16ab:	cmp    %rdi,%rdx
    16ae:	jae    16c2 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0x102>
    16b0:	movslq 0x8(%rsi,%rcx,1),%rdx
    16b5:	add    %rdx,%rax
    16b8:	ret
    16b9:	nopl   0x0(%rax)
    16c0:	xor    %eax,%eax
    16c2:	ret
    16c3:	xor    %edx,%edx
    16c5:	xor    %eax,%eax
    16c7:	jmp    1687 <_Z16kern_k01_sum_fwdRKSt6vectorIiSaIiEE+0xc7>
