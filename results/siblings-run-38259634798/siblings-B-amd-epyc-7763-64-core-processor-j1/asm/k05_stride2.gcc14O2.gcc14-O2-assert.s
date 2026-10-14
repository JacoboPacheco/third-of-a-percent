00000000000015c0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_>:
    15c0:	endbr64
    15c4:	mov    0x8(%rdi),%rax
    15c8:	mov    (%rdi),%r8
    15cb:	mov    %rax,%r9
    15ce:	sub    %r8,%r9
    15d1:	sar    $0x2,%r9
    15d5:	cmp    %r8,%rax
    15d8:	je     1612 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x52>
    15da:	mov    (%rsi),%rdi
    15dd:	mov    0x8(%rsi),%rcx
    15e1:	xor    %eax,%eax
    15e3:	sub    %rdi,%rcx
    15e6:	sar    $0x2,%rcx
    15ea:	mov    %rcx,%rsi
    15ed:	shr    $1,%rsi
    15f0:	lea    (%rax,%rax,1),%rdx
    15f4:	cmp    %rcx,%rdx
    15f7:	jae    1618 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    15f9:	mov    (%rdi,%rax,8),%edx
    15fc:	cmp    %rsi,%rax
    15ff:	je     1618 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x58>
    1601:	add    0x4(%rdi,%rax,8),%edx
    1605:	mov    %edx,(%r8,%rax,4)
    1609:	add    $0x1,%rax
    160d:	cmp    %r9,%rax
    1610:	jb     15f0 <_Z16kern_k05_stride2RSt6vectorIiSaIiEERKS1_+0x30>
    1612:	ret
    1613:	nopl   0x0(%rax,%rax,1)
    1618:	sub    $0x8,%rsp
    161c:	lea    0x9e1(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1623:	lea    0xa16(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    162a:	mov    $0x47d,%esi
    162f:	lea    0xae2(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    1636:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    163b:	nopl   0x0(%rax,%rax,1)
