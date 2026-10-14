00000000000018c0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    18c0:	endbr64
    18c4:	mov    0x8(%rdx),%rax
    18c8:	mov    (%rdx),%rcx
    18cb:	mov    %rax,%r8
    18ce:	sub    %rcx,%r8
    18d1:	sar    $0x2,%r8
    18d5:	cmp    %rcx,%rax
    18d8:	je     1914 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x54>
    18da:	mov    (%rsi),%r9
    18dd:	mov    (%rdi),%rsi
    18e0:	xor    %eax,%eax
    18e2:	data16 cs nopw 0x0(%rax,%rax,1)
    18ed:	data16 cs nopw 0x0(%rax,%rax,1)
    18f8:	nopl   0x0(%rax,%rax,1)
    1900:	movslq (%rcx,%rax,4),%rdx
    1904:	mov    (%r9,%rdx,4),%edx
    1908:	mov    %edx,(%rsi,%rax,4)
    190b:	add    $0x1,%rax
    190f:	cmp    %r8,%rax
    1912:	jb     1900 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x40>
    1914:	ret
    1915:	cs nopw 0x0(%rax,%rax,1)
    191f:	nop
