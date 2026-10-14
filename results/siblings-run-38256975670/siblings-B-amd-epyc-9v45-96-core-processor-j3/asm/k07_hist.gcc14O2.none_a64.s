0000000000001680 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_>:
    1680:	endbr64
    1684:	mov    0x8(%rsi),%rax
    1688:	mov    (%rsi),%rsi
    168b:	mov    %rax,%r8
    168e:	sub    %rsi,%r8
    1691:	sar    $0x2,%r8
    1695:	cmp    %rsi,%rax
    1698:	je     16d1 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x51>
    169a:	mov    (%rdi),%rcx
    169d:	xor    %eax,%eax
    169f:	nop
    16a0:	data16 cs nopw 0x0(%rax,%rax,1)
    16ab:	data16 cs nopw 0x0(%rax,%rax,1)
    16b6:	cs nopw 0x0(%rax,%rax,1)
    16c0:	movzbl (%rsi,%rax,4),%edx
    16c4:	add    $0x1,%rax
    16c8:	addl   $0x1,(%rcx,%rdx,4)
    16cc:	cmp    %r8,%rax
    16cf:	jb     16c0 <_Z13kern_k07_histRSt6vectorIiSaIiEERKS1_+0x40>
    16d1:	ret
    16d2:	cs nopw 0x0(%rax,%rax,1)
    16dc:	nopl   0x0(%rax)
