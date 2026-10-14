0000000000001700 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    1700:	endbr64
    1704:	mov    0x8(%rsi),%rax
    1708:	mov    (%rsi),%rsi
    170b:	mov    %rax,%r8
    170e:	sub    %rsi,%r8
    1711:	sar    $0x2,%r8
    1715:	cmp    %rsi,%rax
    1718:	je     1751 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x51>
    171a:	mov    (%rdi),%rcx
    171d:	xor    %eax,%eax
    171f:	nop
    1720:	data16 cs nopw 0x0(%rax,%rax,1)
    172b:	data16 cs nopw 0x0(%rax,%rax,1)
    1736:	cs nopw 0x0(%rax,%rax,1)
    1740:	movzbl (%rsi,%rax,4),%edx
    1744:	add    $0x1,%rax
    1748:	addl   $0x1,(%rcx,%rdx,4)
    174c:	cmp    %r8,%rax
    174f:	jb     1740 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x40>
    1751:	ret
