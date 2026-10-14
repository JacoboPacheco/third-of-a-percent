00000000000015c0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    15c0:	endbr64
    15c4:	mov    (%rsi),%r8
    15c7:	mov    0x8(%rsi),%rdx
    15cb:	sub    %r8,%rdx
    15ce:	sar    $0x2,%rdx
    15d2:	je     1630 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    15d4:	mov    (%rdi),%rsi
    15d7:	mov    0x8(%rdi),%rcx
    15db:	lea    -0x1(%rdx),%rax
    15df:	mov    (%r8,%rax,4),%edi
    15e3:	sub    %rsi,%rcx
    15e6:	sar    $0x2,%rcx
    15ea:	lea    (%rdi,%rdi,1),%edx
    15ed:	cmp    %rcx,%rax
    15f0:	jae    160d <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x4d>
    15f2:	mov    %edx,(%rsi,%rax,4)
    15f5:	lea    -0x1(%rax),%rdx
    15f9:	test   %rax,%rax
    15fc:	je     1630 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    15fe:	mov    %rdx,%rax
    1601:	mov    (%r8,%rax,4),%edi
    1605:	lea    (%rdi,%rdi,1),%edx
    1608:	cmp    %rcx,%rax
    160b:	jb     15f2 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x32>
    160d:	sub    $0x8,%rsp
    1611:	lea    0x9ec(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1618:	lea    0xa21(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    161f:	mov    $0x46a,%esi
    1624:	lea    0xad5(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    162b:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    1630:	ret
    1631:	cs nopw 0x0(%rax,%rax,1)
    163b:	nopl   0x0(%rax,%rax,1)
