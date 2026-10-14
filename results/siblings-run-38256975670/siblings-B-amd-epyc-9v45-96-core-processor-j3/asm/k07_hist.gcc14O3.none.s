00000000000016a0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    16a0:	endbr64
    16a4:	mov    0x8(%rsi),%rax
    16a8:	mov    (%rsi),%rsi
    16ab:	mov    %rax,%r8
    16ae:	sub    %rsi,%r8
    16b1:	sar    $0x2,%r8
    16b5:	cmp    %rsi,%rax
    16b8:	je     16d1 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x31>
    16ba:	mov    (%rdi),%rcx
    16bd:	xor    %eax,%eax
    16bf:	nop
    16c0:	movzbl (%rsi,%rax,4),%edx
    16c4:	add    $0x1,%rax
    16c8:	addl   $0x1,(%rcx,%rdx,4)
    16cc:	cmp    %r8,%rax
    16cf:	jb     16c0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x20>
    16d1:	ret
