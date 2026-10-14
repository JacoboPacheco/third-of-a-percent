0000000000001680 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    (%rsi),%r8
    1687:	mov    0x8(%rsi),%rax
    168b:	sub    %r8,%rax
    168e:	mov    %rax,%r9
    1691:	sar    $0x2,%r9
    1695:	cmp    $0x8,%rax
    1699:	jbe    1700 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    169b:	mov    (%rdi),%rsi
    169e:	mov    0x8(%rdi),%rcx
    16a2:	mov    $0x1,%eax
    16a7:	sub    %rsi,%rcx
    16aa:	sar    $0x2,%rcx
    16ae:	cmp    %rcx,%rax
    16b1:	jae    16d9 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x59>
    16b3:	mov    (%r8,%rax,4),%edx
    16b7:	add    -0x4(%r8,%rax,4),%edx
    16bc:	add    0x4(%r8,%rax,4),%edx
    16c1:	mov    %edx,(%rsi,%rax,4)
    16c4:	lea    0x1(%rax),%rdx
    16c8:	add    $0x2,%rax
    16cc:	cmp    %r9,%rax
    16cf:	jae    1700 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x80>
    16d1:	mov    %rdx,%rax
    16d4:	cmp    %rcx,%rax
    16d7:	jb     16b3 <_Z16kern_k03_stencilRSt6vectorIiSaIiEERKS1_+0x33>
    16d9:	sub    $0x8,%rsp
    16dd:	lea    0x920(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    16e4:	lea    0x955(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    16eb:	mov    $0x46a,%esi
    16f0:	lea    0xa09(%rip),%rdi        # 2100 <_IO_stdin_used+0x100>
    16f7:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    16fc:	nopl   0x0(%rax)
    1700:	ret
    1701:	cs nopw 0x0(%rax,%rax,1)
    170b:	nopl   0x0(%rax,%rax,1)
