00000000000018a0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    18a0:	endbr64
    18a4:	mov    0x8(%rdx),%rax
    18a8:	mov    (%rdx),%rcx
    18ab:	mov    %rax,%r8
    18ae:	sub    %rcx,%r8
    18b1:	sar    $0x2,%r8
    18b5:	cmp    %rcx,%rax
    18b8:	je     18f4 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x54>
    18ba:	mov    (%rsi),%r9
    18bd:	mov    (%rdi),%rsi
    18c0:	xor    %eax,%eax
    18c2:	data16 cs nopw 0x0(%rax,%rax,1)
    18cd:	data16 cs nopw 0x0(%rax,%rax,1)
    18d8:	nopl   0x0(%rax,%rax,1)
    18e0:	movslq (%rcx,%rax,4),%rdx
    18e4:	mov    (%r9,%rdx,4),%edx
    18e8:	mov    %edx,(%rsi,%rax,4)
    18eb:	add    $0x1,%rax
    18ef:	cmp    %r8,%rax
    18f2:	jb     18e0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x40>
    18f4:	ret
    18f5:	cs nopw 0x0(%rax,%rax,1)
    18ff:	nop
