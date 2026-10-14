0000000000001800 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    1800:	endbr64
    1804:	test   %rcx,%rcx
    1807:	je     18f8 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0xf8>
    180d:	push   %r12
    180f:	lea    0x0(,%rcx,4),%r9
    1817:	push   %rbp
    1818:	mov    %rcx,%rbp
    181b:	push   %rbx
    181c:	mov    (%rsi),%r10
    181f:	xor    %ebx,%ebx
    1821:	mov    (%rdx),%r12
    1824:	mov    (%rdi),%r11
    1827:	add    %r9,%r10
    182a:	add    %r9,%r12
    182d:	data16 cs nopw 0x0(%rax,%rax,1)
    1838:	nopl   0x0(%rax,%rax,1)
    1840:	mov    %r10,%r8
    1843:	mov    %r12,%rsi
    1846:	sub    %r9,%r8
    1849:	data16 cs nopw 0x0(%rax,%rax,1)
    1854:	data16 cs nopw 0x0(%rax,%rax,1)
    185f:	data16 cs nopw 0x0(%rax,%rax,1)
    186a:	data16 cs nopw 0x0(%rax,%rax,1)
    1875:	data16 cs nopw 0x0(%rax,%rax,1)
    1880:	mov    %rsi,%rdx
    1883:	mov    (%r8),%edi
    1886:	mov    %r11,%rax
    1889:	sub    %r9,%rdx
    188c:	data16 cs nopw 0x0(%rax,%rax,1)
    1897:	nopw   0x0(%rax,%rax,1)
    18a0:	data16 cs nopw 0x0(%rax,%rax,1)
    18ab:	data16 cs nopw 0x0(%rax,%rax,1)
    18b6:	cs nopw 0x0(%rax,%rax,1)
    18c0:	mov    (%rdx),%ecx
    18c2:	add    $0x4,%rdx
    18c6:	imul   %edi,%ecx
    18c9:	add    %ecx,(%rax)
    18cb:	add    $0x4,%rax
    18cf:	cmp    %rdx,%rsi
    18d2:	jne    18c0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0xc0>
    18d4:	add    $0x4,%r8
    18d8:	add    %r9,%rsi
    18db:	cmp    %r8,%r10
    18de:	jne    1880 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x80>
    18e0:	add    $0x1,%rbx
    18e4:	add    %r9,%r10
    18e7:	add    %r9,%r11
    18ea:	cmp    %rbx,%rbp
    18ed:	jne    1840 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x40>
    18f3:	pop    %rbx
    18f4:	pop    %rbp
    18f5:	pop    %r12
    18f7:	ret
    18f8:	ret
    18f9:	nopl   0x0(%rax)
