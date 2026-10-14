00000000000016a0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    16a0:	endbr64
    16a4:	mov    (%rsi),%r8
    16a7:	mov    0x8(%rsi),%rdx
    16ab:	sub    %r8,%rdx
    16ae:	sar    $0x2,%rdx
    16b2:	je     1710 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    16b4:	mov    (%rdi),%rsi
    16b7:	mov    0x8(%rdi),%rcx
    16bb:	lea    -0x1(%rdx),%rax
    16bf:	mov    (%r8,%rax,4),%edi
    16c3:	sub    %rsi,%rcx
    16c6:	sar    $0x2,%rcx
    16ca:	lea    (%rdi,%rdi,1),%edx
    16cd:	cmp    %rcx,%rax
    16d0:	jae    16ed <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x4d>
    16d2:	mov    %edx,(%rsi,%rax,4)
    16d5:	lea    -0x1(%rax),%rdx
    16d9:	test   %rax,%rax
    16dc:	je     1710 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    16de:	mov    %rdx,%rax
    16e1:	mov    (%r8,%rax,4),%edi
    16e5:	lea    (%rdi,%rdi,1),%edx
    16e8:	cmp    %rcx,%rax
    16eb:	jb     16d2 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x32>
    16ed:	sub    $0x8,%rsp
    16f1:	lea    0x90c(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    16f8:	lea    0x941(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    16ff:	mov    $0x46a,%esi
    1704:	lea    0x9f5(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    170b:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1710:	ret
    1711:	cs nopw 0x0(%rax,%rax,1)
    171b:	nopl   0x0(%rax,%rax,1)
