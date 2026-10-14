00000000000015c0 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_>:
    15c0:	endbr64
    15c4:	mov    (%rsi),%rcx
    15c7:	mov    0x8(%rsi),%rdx
    15cb:	sub    %rcx,%rdx
    15ce:	sar    $0x2,%rdx
    15d2:	lea    -0x1(%rdx),%rax
    15d6:	je     160f <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x4f>
    15d8:	mov    (%rdi),%rsi
    15db:	nopl   0x0(%rax,%rax,1)
    15e0:	data16 cs nopw 0x0(%rax,%rax,1)
    15eb:	data16 cs nopw 0x0(%rax,%rax,1)
    15f6:	cs nopw 0x0(%rax,%rax,1)
    1600:	mov    (%rcx,%rax,4),%edi
    1603:	lea    (%rdi,%rdi,1),%edx
    1606:	mov    %edx,(%rsi,%rax,4)
    1609:	sub    $0x1,%rax
    160d:	jae    1600 <_Z12kern_k04_revRSt6vectorIiSaIiEERKS1_+0x40>
    160f:	ret
