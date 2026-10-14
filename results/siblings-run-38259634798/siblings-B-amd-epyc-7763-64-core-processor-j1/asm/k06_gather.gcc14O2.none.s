0000000000001680 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    1680:	endbr64
    1684:	mov    0x8(%rdx),%rax
    1688:	mov    (%rdx),%rcx
    168b:	mov    %rax,%r8
    168e:	sub    %rcx,%r8
    1691:	sar    $0x2,%r8
    1695:	cmp    %rcx,%rax
    1698:	je     16d4 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x54>
    169a:	mov    (%rsi),%r9
    169d:	mov    (%rdi),%rsi
    16a0:	xor    %eax,%eax
    16a2:	data16 cs nopw 0x0(%rax,%rax,1)
    16ad:	data16 cs nopw 0x0(%rax,%rax,1)
    16b8:	nopl   0x0(%rax,%rax,1)
    16c0:	movslq (%rcx,%rax,4),%rdx
    16c4:	mov    (%r9,%rdx,4),%edx
    16c8:	mov    %edx,(%rsi,%rax,4)
    16cb:	add    $0x1,%rax
    16cf:	cmp    %r8,%rax
    16d2:	jb     16c0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x40>
    16d4:	ret
    16d5:	cs nopw 0x0(%rax,%rax,1)
    16df:	nop
