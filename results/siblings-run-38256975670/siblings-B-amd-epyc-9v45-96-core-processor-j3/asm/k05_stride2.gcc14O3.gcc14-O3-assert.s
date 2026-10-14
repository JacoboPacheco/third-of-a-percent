0000000000001680 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    0x8(%rdi),%rax
    1688:	mov    (%rdi),%r8
    168b:	mov    %rax,%r9
    168e:	sub    %r8,%r9
    1691:	sar    $0x2,%r9
    1695:	cmp    %r8,%rax
    1698:	je     16d2 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x52>
    169a:	mov    (%rsi),%rdi
    169d:	mov    0x8(%rsi),%rcx
    16a1:	xor    %eax,%eax
    16a3:	sub    %rdi,%rcx
    16a6:	sar    $0x2,%rcx
    16aa:	mov    %rcx,%rsi
    16ad:	shr    $1,%rsi
    16b0:	lea    (%rax,%rax,1),%rdx
    16b4:	cmp    %rcx,%rdx
    16b7:	jae    16d8 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    16b9:	mov    (%rdi,%rax,8),%edx
    16bc:	cmp    %rax,%rsi
    16bf:	je     16d8 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    16c1:	add    0x4(%rdi,%rax,8),%edx
    16c5:	mov    %edx,(%r8,%rax,4)
    16c9:	add    $0x1,%rax
    16cd:	cmp    %r9,%rax
    16d0:	jb     16b0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x30>
    16d2:	ret
    16d3:	nopl   0x0(%rax,%rax,1)
    16d8:	sub    $0x8,%rsp
    16dc:	lea    0x921(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    16e3:	lea    0x956(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    16ea:	mov    $0x47d,%esi
    16ef:	lea    0xa22(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    16f6:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    16fb:	nopl   0x0(%rax,%rax,1)
