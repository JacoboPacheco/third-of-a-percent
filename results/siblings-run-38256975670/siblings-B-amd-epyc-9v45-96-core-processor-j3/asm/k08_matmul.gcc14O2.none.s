00000000000017a0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    17a0:	endbr64
    17a4:	test   %rcx,%rcx
    17a7:	je     1834 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x94>
    17ad:	push   %r12
    17af:	lea    0x0(,%rcx,4),%r9
    17b7:	push   %rbp
    17b8:	mov    %rcx,%rbp
    17bb:	push   %rbx
    17bc:	mov    (%rsi),%r10
    17bf:	xor    %ebx,%ebx
    17c1:	mov    (%rdx),%r12
    17c4:	mov    (%rdi),%r11
    17c7:	add    %r9,%r10
    17ca:	add    %r9,%r12
    17cd:	nopl   (%rax)
    17d0:	mov    %r10,%r8
    17d3:	mov    %r12,%rsi
    17d6:	sub    %r9,%r8
    17d9:	nopl   0x0(%rax)
    17e0:	mov    %rsi,%rdx
    17e3:	mov    (%r8),%edi
    17e6:	mov    %r11,%rax
    17e9:	sub    %r9,%rdx
    17ec:	data16 cs nopw 0x0(%rax,%rax,1)
    17f7:	nopw   0x0(%rax,%rax,1)
    1800:	mov    (%rdx),%ecx
    1802:	add    $0x4,%rdx
    1806:	imul   %edi,%ecx
    1809:	add    %ecx,(%rax)
    180b:	add    $0x4,%rax
    180f:	cmp    %rdx,%rsi
    1812:	jne    1800 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x60>
    1814:	add    $0x4,%r8
    1818:	add    %r9,%rsi
    181b:	cmp    %r8,%r10
    181e:	jne    17e0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x40>
    1820:	add    $0x1,%rbx
    1824:	add    %r9,%r10
    1827:	add    %r9,%r11
    182a:	cmp    %rbx,%rbp
    182d:	jne    17d0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x30>
    182f:	pop    %rbx
    1830:	pop    %rbp
    1831:	pop    %r12
    1833:	ret
    1834:	ret
    1835:	cs nopw 0x0(%rax,%rax,1)
    183f:	nop
