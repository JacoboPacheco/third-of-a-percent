00000000000016a0 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    16a0:	endbr64
    16a4:	mov    (%rsi),%r8
    16a7:	mov    0x8(%rsi),%rax
    16ab:	sub    %r8,%rax
    16ae:	mov    %rax,%r9
    16b1:	sar    $0x2,%r9
    16b5:	cmp    $0x8,%rax
    16b9:	jbe    1720 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    16bb:	mov    (%rdi),%rsi
    16be:	mov    0x8(%rdi),%rcx
    16c2:	mov    $0x1,%eax
    16c7:	sub    %rsi,%rcx
    16ca:	sar    $0x2,%rcx
    16ce:	cmp    %rcx,%rax
    16d1:	jae    16f9 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x59>
    16d3:	mov    (%r8,%rax,4),%edx
    16d7:	add    -0x4(%r8,%rax,4),%edx
    16dc:	add    0x4(%r8,%rax,4),%edx
    16e1:	mov    %edx,(%rsi,%rax,4)
    16e4:	lea    0x1(%rax),%rdx
    16e8:	add    $0x2,%rax
    16ec:	cmp    %r9,%rax
    16ef:	jae    1720 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    16f1:	mov    %rdx,%rax
    16f4:	cmp    %rcx,%rax
    16f7:	jb     16d3 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x33>
    16f9:	sub    $0x8,%rsp
    16fd:	lea    0x900(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1704:	lea    0x935(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    170b:	mov    $0x46a,%esi
    1710:	lea    0x9e9(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    1717:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    171c:	nopl   0x0(%rax)
    1720:	ret
    1721:	cs nopw 0x0(%rax,%rax,1)
    172b:	nopl   0x0(%rax,%rax,1)
