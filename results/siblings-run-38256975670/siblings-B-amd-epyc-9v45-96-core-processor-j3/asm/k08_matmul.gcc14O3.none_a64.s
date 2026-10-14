0000000000001940 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    1940:	endbr64
    1944:	test   %rcx,%rcx
    1947:	je     1b92 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x252>
    194d:	push   %r15
    194f:	lea    -0x1(%rcx),%rax
    1953:	mov    %rcx,%r11
    1956:	push   %r14
    1958:	mov    %rcx,%r14
    195b:	push   %r13
    195d:	and    $0xfffffffffffffffc,%r14
    1961:	xor    %r13d,%r13d
    1964:	push   %r12
    1966:	lea    0x0(,%rcx,4),%r12
    196e:	push   %rbp
    196f:	push   %rbx
    1970:	mov    (%rdi),%rbp
    1973:	mov    %r13,%rbx
    1976:	xor    %edi,%edi
    1978:	mov    (%rsi),%r15
    197b:	mov    %rcx,%rsi
    197e:	mov    (%rdx),%r10
    1981:	shr    $0x2,%rsi
    1985:	mov    %rbp,%rdx
    1988:	mov    %rax,-0x18(%rsp)
    198d:	lea    0x1(%r14),%rax
    1991:	add    %r12,%r15
    1994:	shl    $0x4,%rsi
    1998:	mov    %rax,-0x40(%rsp)
    199d:	lea    0x2(%r14),%rax
    19a1:	mov    %rax,-0x38(%rsp)
    19a6:	mov    %rcx,%rax
    19a9:	and    $0x3,%eax
    19ac:	mov    %rax,-0x48(%rsp)
    19b1:	data16 cs nopw 0x0(%rax,%rax,1)
    19bc:	nopl   0x0(%rax)
    19c0:	lea    0x0(%rbp,%rbx,4),%rcx
    19c5:	mov    %rdi,-0x10(%rsp)
    19ca:	mov    %r15,%r8
    19cd:	mov    %r10,%rax
    19d0:	mov    %rcx,-0x20(%rsp)
    19d5:	mov    -0x40(%rsp),%rcx
    19da:	sub    %r12,%r8
    19dd:	xor    %r9d,%r9d
    19e0:	add    %rbx,%rcx
    19e3:	lea    0x0(%rbp,%rcx,4),%rcx
    19e8:	mov    %rcx,-0x30(%rsp)
    19ed:	mov    -0x38(%rsp),%rcx
    19f2:	add    %rbx,%rcx
    19f5:	lea    0x0(%rbp,%rcx,4),%rcx
    19fa:	mov    %rcx,-0x28(%rsp)
    19ff:	cmpq   $0x2,-0x18(%rsp)
    1a05:	mov    (%r8),%edi
    1a08:	jbe    1b07 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x1c7>
    1a0e:	lea    0x4(%rax),%r13
    1a12:	mov    %rdx,%rcx
    1a15:	sub    %r13,%rcx
    1a18:	cmp    $0x8,%rcx
    1a1c:	jbe    1b07 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x1c7>
    1a22:	movd   %edi,%xmm4
    1a26:	xor    %ecx,%ecx
    1a28:	pshufd $0x0,%xmm4,%xmm2
    1a2d:	movdqa %xmm2,%xmm3
    1a31:	psrlq  $0x20,%xmm3
    1a36:	cs nopw 0x0(%rax,%rax,1)
    1a40:	movdqu (%rax,%rcx,1),%xmm0
    1a45:	movdqa %xmm0,%xmm1
    1a49:	psrlq  $0x20,%xmm0
    1a4e:	pmuludq %xmm2,%xmm1
    1a52:	pmuludq %xmm3,%xmm0
    1a56:	pshufd $0x8,%xmm1,%xmm1
    1a5b:	pshufd $0x8,%xmm0,%xmm0
    1a60:	punpckldq %xmm0,%xmm1
    1a64:	movdqu (%rdx,%rcx,1),%xmm0
    1a69:	paddd  %xmm1,%xmm0
    1a6d:	movups %xmm0,(%rdx,%rcx,1)
    1a71:	add    $0x10,%rcx
    1a75:	cmp    %rsi,%rcx
    1a78:	jne    1a40 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    1a7a:	cmpq   $0x0,-0x48(%rsp)
    1a80:	je     1add <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x19d>
    1a82:	lea    (%r14,%rbx,1),%rcx
    1a86:	lea    (%r14,%r9,1),%r13
    1a8a:	mov    %rcx,-0x50(%rsp)
    1a8f:	mov    (%r10,%r13,4),%ecx
    1a93:	imul   %edi,%ecx
    1a96:	mov    %ecx,%r13d
    1a99:	mov    -0x50(%rsp),%rcx
    1a9e:	add    %r13d,0x0(%rbp,%rcx,4)
    1aa3:	mov    -0x40(%rsp),%rcx
    1aa8:	cmp    %r11,%rcx
    1aab:	jae    1add <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x19d>
    1aad:	add    %r9,%rcx
    1ab0:	mov    (%r10,%rcx,4),%r13d
    1ab4:	imul   %edi,%r13d
    1ab8:	mov    %r13d,%ecx
    1abb:	mov    -0x30(%rsp),%r13
    1ac0:	add    %ecx,0x0(%r13)
    1ac4:	mov    -0x38(%rsp),%rcx
    1ac9:	cmp    %r11,%rcx
    1acc:	jae    1add <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x19d>
    1ace:	add    %r9,%rcx
    1ad1:	imul   (%r10,%rcx,4),%edi
    1ad6:	mov    -0x28(%rsp),%rcx
    1adb:	add    %edi,(%rcx)
    1add:	add    $0x4,%r8
    1ae1:	add    %r12,%rax
    1ae4:	add    %r11,%r9
    1ae7:	cmp    %r15,%r8
    1aea:	je     1b6c <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x22c>
    1af0:	lea    0x4(%rax),%r13
    1af4:	mov    %rdx,%rcx
    1af7:	mov    (%r8),%edi
    1afa:	sub    %r13,%rcx
    1afd:	cmp    $0x8,%rcx
    1b01:	ja     1a22 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0xe2>
    1b07:	mov    %r8,-0x50(%rsp)
    1b0c:	mov    -0x20(%rsp),%rcx
    1b11:	lea    (%rax,%r12,1),%r13
    1b15:	data16 cs nopw 0x0(%rax,%rax,1)
    1b20:	data16 cs nopw 0x0(%rax,%rax,1)
    1b2b:	data16 cs nopw 0x0(%rax,%rax,1)
    1b36:	cs nopw 0x0(%rax,%rax,1)
    1b40:	mov    (%rax),%r8d
    1b43:	add    $0x4,%rax
    1b47:	imul   %edi,%r8d
    1b4b:	add    %r8d,(%rcx)
    1b4e:	add    $0x4,%rcx
    1b52:	cmp    %r13,%rax
    1b55:	jne    1b40 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x200>
    1b57:	mov    -0x50(%rsp),%r8
    1b5c:	add    %r11,%r9
    1b5f:	add    $0x4,%r8
    1b63:	cmp    %r15,%r8
    1b66:	jne    19ff <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0xbf>
    1b6c:	mov    -0x10(%rsp),%rdi
    1b71:	add    %r12,%r15
    1b74:	add    %r12,%rdx
    1b77:	add    %r11,%rbx
    1b7a:	add    $0x1,%rdi
    1b7e:	cmp    %rdi,%r11
    1b81:	jne    19c0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x80>
    1b87:	pop    %rbx
    1b88:	pop    %rbp
    1b89:	pop    %r12
    1b8b:	pop    %r13
    1b8d:	pop    %r14
    1b8f:	pop    %r15
    1b91:	ret
    1b92:	ret
    1b93:	cs nopw 0x0(%rax,%rax,1)
    1b9d:	nopl   (%rax)
