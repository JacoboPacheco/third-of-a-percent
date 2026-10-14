0000000000001680 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    (%rsi),%r8
    1687:	mov    0x8(%rsi),%rdx
    168b:	sub    %r8,%rdx
    168e:	sar    $0x2,%rdx
    1692:	je     16f0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    1694:	mov    (%rdi),%rsi
    1697:	mov    0x8(%rdi),%rcx
    169b:	lea    -0x1(%rdx),%rax
    169f:	mov    (%r8,%rax,4),%edi
    16a3:	sub    %rsi,%rcx
    16a6:	sar    $0x2,%rcx
    16aa:	lea    (%rdi,%rdi,1),%edx
    16ad:	cmp    %rcx,%rax
    16b0:	jae    16cd <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x4d>
    16b2:	mov    %edx,(%rsi,%rax,4)
    16b5:	lea    -0x1(%rax),%rdx
    16b9:	test   %rax,%rax
    16bc:	je     16f0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x70>
    16be:	mov    %rdx,%rax
    16c1:	mov    (%r8,%rax,4),%edi
    16c5:	lea    (%rdi,%rdi,1),%edx
    16c8:	cmp    %rcx,%rax
    16cb:	jb     16b2 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x32>
    16cd:	sub    $0x8,%rsp
    16d1:	lea    0x92c(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    16d8:	lea    0x961(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    16df:	mov    $0x46a,%esi
    16e4:	lea    0xa15(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    16eb:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    16f0:	ret
    16f1:	cs nopw 0x0(%rax,%rax,1)
    16fb:	nopl   0x0(%rax,%rax,1)
