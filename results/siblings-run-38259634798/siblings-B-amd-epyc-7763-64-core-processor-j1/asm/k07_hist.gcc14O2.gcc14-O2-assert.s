00000000000016c0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    16c0:	endbr64
    16c4:	mov    0x8(%rsi),%rax
    16c8:	mov    (%rsi),%r8
    16cb:	mov    %rax,%r9
    16ce:	sub    %r8,%r9
    16d1:	sar    $0x2,%r9
    16d5:	cmp    %r8,%rax
    16d8:	je     1740 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x80>
    16da:	mov    (%rdi),%rsi
    16dd:	mov    0x8(%rdi),%rcx
    16e1:	xor    %eax,%eax
    16e3:	sub    %rsi,%rcx
    16e6:	sar    $0x2,%rcx
    16ea:	jmp    170d <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x4d>
    16ec:	data16 cs nopw 0x0(%rax,%rax,1)
    16f7:	nopw   0x0(%rax,%rax,1)
    1700:	add    $0x1,%rax
    1704:	addl   $0x1,(%rsi,%rdx,4)
    1708:	cmp    %r9,%rax
    170b:	jae    1740 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x80>
    170d:	movzbl (%r8,%rax,4),%edx
    1712:	cmp    %rcx,%rdx
    1715:	jb     1700 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x40>
    1717:	sub    $0x8,%rsp
    171b:	lea    0x8e2(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1722:	lea    0x917(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    1729:	mov    $0x46a,%esi
    172e:	lea    0x9d3(%rip),%rdi        # 2108 <_IO_stdin_used+0x108>
    1735:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    173a:	nopw   0x0(%rax,%rax,1)
    1740:	ret
    1741:	cs nopw 0x0(%rax,%rax,1)
    174b:	nopl   0x0(%rax,%rax,1)
