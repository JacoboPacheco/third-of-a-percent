0000000000001580 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    1580:	endbr64
    1584:	mov    (%rsi),%rcx
    1587:	mov    0x8(%rsi),%rdx
    158b:	sub    %rcx,%rdx
    158e:	sar    $0x2,%rdx
    1592:	lea    -0x1(%rdx),%rax
    1596:	je     15af <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x2f>
    1598:	mov    (%rdi),%rsi
    159b:	nopl   0x0(%rax,%rax,1)
    15a0:	mov    (%rcx,%rax,4),%edi
    15a3:	lea    (%rdi,%rdi,1),%edx
    15a6:	mov    %edx,(%rsi,%rax,4)
    15a9:	sub    $0x1,%rax
    15ad:	jae    15a0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x20>
    15af:	ret
