00000000000016a0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    16a0:	endbr64
    16a4:	mov    0x8(%rdi),%rax
    16a8:	mov    (%rdi),%r8
    16ab:	mov    %rax,%r9
    16ae:	sub    %r8,%r9
    16b1:	sar    $0x2,%r9
    16b5:	cmp    %r8,%rax
    16b8:	je     16f2 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x52>
    16ba:	mov    (%rsi),%rdi
    16bd:	mov    0x8(%rsi),%rcx
    16c1:	xor    %eax,%eax
    16c3:	sub    %rdi,%rcx
    16c6:	sar    $0x2,%rcx
    16ca:	mov    %rcx,%rsi
    16cd:	shr    $1,%rsi
    16d0:	lea    (%rax,%rax,1),%rdx
    16d4:	cmp    %rcx,%rdx
    16d7:	jae    16f8 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    16d9:	mov    (%rdi,%rax,8),%edx
    16dc:	cmp    %rax,%rsi
    16df:	je     16f8 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    16e1:	add    0x4(%rdi,%rax,8),%edx
    16e5:	mov    %edx,(%r8,%rax,4)
    16e9:	add    $0x1,%rax
    16ed:	cmp    %r9,%rax
    16f0:	jb     16d0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x30>
    16f2:	ret
    16f3:	nopl   0x0(%rax,%rax,1)
    16f8:	sub    $0x8,%rsp
    16fc:	lea    0x901(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1703:	lea    0x936(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    170a:	mov    $0x47d,%esi
    170f:	lea    0xa02(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1716:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    171b:	nopl   0x0(%rax,%rax,1)
