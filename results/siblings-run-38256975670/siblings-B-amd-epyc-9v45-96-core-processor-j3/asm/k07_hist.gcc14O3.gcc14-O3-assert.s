00000000000016e0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    16e0:	endbr64
    16e4:	mov    0x8(%rsi),%rax
    16e8:	mov    (%rsi),%r8
    16eb:	mov    %rax,%r9
    16ee:	sub    %r8,%r9
    16f1:	sar    $0x2,%r9
    16f5:	cmp    %r8,%rax
    16f8:	je     1760 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x80>
    16fa:	mov    (%rdi),%rsi
    16fd:	mov    0x8(%rdi),%rcx
    1701:	xor    %eax,%eax
    1703:	sub    %rsi,%rcx
    1706:	sar    $0x2,%rcx
    170a:	jmp    172d <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x4d>
    170c:	data16 cs nopw 0x0(%rax,%rax,1)
    1717:	nopw   0x0(%rax,%rax,1)
    1720:	add    $0x1,%rax
    1724:	addl   $0x1,(%rsi,%rdx,4)
    1728:	cmp    %r9,%rax
    172b:	jae    1760 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x80>
    172d:	movzbl (%r8,%rax,4),%edx
    1732:	cmp    %rcx,%rdx
    1735:	jb     1720 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x40>
    1737:	sub    $0x8,%rsp
    173b:	lea    0x8c2(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1742:	lea    0x8f7(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    1749:	mov    $0x46a,%esi
    174e:	lea    0x9b3(%rip),%rdi        # 2108 <_IO_stdin_used+0x108>
    1755:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    175a:	nopw   0x0(%rax,%rax,1)
    1760:	ret
