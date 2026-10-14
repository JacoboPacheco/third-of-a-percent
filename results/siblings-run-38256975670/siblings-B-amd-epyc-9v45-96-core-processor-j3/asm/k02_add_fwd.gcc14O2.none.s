00000000000015e0 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:
    15e0:	endbr64
    15e4:	mov    0x8(%rsi),%rax
    15e8:	mov    (%rsi),%rcx
    15eb:	mov    %rax,%rsi
    15ee:	sub    %rcx,%rsi
    15f1:	sar    $0x2,%rsi
    15f5:	cmp    %rcx,%rax
    15f8:	je     1633 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x53>
    15fa:	mov    (%rdx),%r8
    15fd:	mov    (%rdi),%rdi
    1600:	xor    %eax,%eax
    1602:	data16 cs nopw 0x0(%rax,%rax,1)
    160d:	data16 cs nopw 0x0(%rax,%rax,1)
    1618:	nopl   0x0(%rax,%rax,1)
    1620:	mov    (%r8,%rax,4),%edx
    1624:	add    (%rcx,%rax,4),%edx
    1627:	mov    %edx,(%rdi,%rax,4)
    162a:	add    $0x1,%rax
    162e:	cmp    %rsi,%rax
    1631:	jb     1620 <_Z16kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0x40>
    1633:	ret
    1634:	cs nopw 0x0(%rax,%rax,1)
    163e:	xchg   %ax,%ax
