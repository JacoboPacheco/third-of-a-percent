00000000000016c0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    16c0:	endbr64
    16c4:	mov    0x8(%rdx),%rax
    16c8:	mov    (%rdx),%rcx
    16cb:	mov    %rax,%r8
    16ce:	sub    %rcx,%r8
    16d1:	sar    $0x2,%r8
    16d5:	cmp    %rcx,%rax
    16d8:	je     1714 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x54>
    16da:	mov    (%rsi),%r9
    16dd:	mov    (%rdi),%rsi
    16e0:	xor    %eax,%eax
    16e2:	data16 cs nopw 0x0(%rax,%rax,1)
    16ed:	data16 cs nopw 0x0(%rax,%rax,1)
    16f8:	nopl   0x0(%rax,%rax,1)
    1700:	movslq (%rcx,%rax,4),%rdx
    1704:	mov    (%r9,%rdx,4),%edx
    1708:	mov    %edx,(%rsi,%rax,4)
    170b:	add    $0x1,%rax
    170f:	cmp    %r8,%rax
    1712:	jb     1700 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x40>
    1714:	ret
    1715:	cs nopw 0x0(%rax,%rax,1)
    171f:	nop
