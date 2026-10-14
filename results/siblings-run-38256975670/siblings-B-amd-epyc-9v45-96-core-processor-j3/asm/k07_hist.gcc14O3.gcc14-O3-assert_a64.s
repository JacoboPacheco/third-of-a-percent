0000000000001720 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    1720:	endbr64
    1724:	mov    0x8(%rsi),%rax
    1728:	mov    (%rsi),%r8
    172b:	mov    %rax,%r9
    172e:	sub    %r8,%r9
    1731:	sar    $0x2,%r9
    1735:	cmp    %r8,%rax
    1738:	je     17a0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x80>
    173a:	mov    (%rdi),%rsi
    173d:	mov    0x8(%rdi),%rcx
    1741:	xor    %eax,%eax
    1743:	sub    %rsi,%rcx
    1746:	sar    $0x2,%rcx
    174a:	jmp    176d <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x4d>
    174c:	data16 cs nopw 0x0(%rax,%rax,1)
    1757:	nopw   0x0(%rax,%rax,1)
    1760:	add    $0x1,%rax
    1764:	addl   $0x1,(%rsi,%rdx,4)
    1768:	cmp    %r9,%rax
    176b:	jae    17a0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x80>
    176d:	movzbl (%r8,%rax,4),%edx
    1772:	cmp    %rcx,%rdx
    1775:	jb     1760 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x40>
    1777:	sub    $0x8,%rsp
    177b:	lea    0x882(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1782:	lea    0x8b7(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    1789:	mov    $0x46a,%esi
    178e:	lea    0x973(%rip),%rdi        # 2108 <_IO_stdin_used+0x108>
    1795:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    179a:	nopw   0x0(%rax,%rax,1)
    17a0:	ret
