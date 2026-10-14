0000000000001900 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m>:
    1900:	endbr64
    1904:	test   %rcx,%rcx
    1907:	je     1b32 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x232>
    190d:	push   %r15
    190f:	lea    -0x1(%rcx),%rax
    1913:	mov    %rcx,%r11
    1916:	push   %r14
    1918:	mov    %rcx,%r14
    191b:	push   %r13
    191d:	and    $0xfffffffffffffffc,%r14
    1921:	xor    %r13d,%r13d
    1924:	push   %r12
    1926:	lea    0x0(,%rcx,4),%r12
    192e:	push   %rbp
    192f:	push   %rbx
    1930:	mov    (%rdi),%rbp
    1933:	mov    %r13,%rbx
    1936:	xor    %edi,%edi
    1938:	mov    (%rsi),%r15
    193b:	mov    %rcx,%rsi
    193e:	mov    (%rdx),%r10
    1941:	shr    $0x2,%rsi
    1945:	mov    %rbp,%rdx
    1948:	mov    %rax,-0x18(%rsp)
    194d:	lea    0x1(%r14),%rax
    1951:	add    %r12,%r15
    1954:	shl    $0x4,%rsi
    1958:	mov    %rax,-0x40(%rsp)
    195d:	lea    0x2(%r14),%rax
    1961:	mov    %rax,-0x38(%rsp)
    1966:	mov    %rcx,%rax
    1969:	and    $0x3,%eax
    196c:	mov    %rax,-0x48(%rsp)
    1971:	data16 cs nopw 0x0(%rax,%rax,1)
    197c:	nopl   0x0(%rax)
    1980:	lea    0x0(%rbp,%rbx,4),%rcx
    1985:	mov    %rdi,-0x10(%rsp)
    198a:	mov    %r15,%r8
    198d:	mov    %r10,%rax
    1990:	mov    %rcx,-0x20(%rsp)
    1995:	mov    -0x40(%rsp),%rcx
    199a:	sub    %r12,%r8
    199d:	xor    %r9d,%r9d
    19a0:	add    %rbx,%rcx
    19a3:	lea    0x0(%rbp,%rcx,4),%rcx
    19a8:	mov    %rcx,-0x30(%rsp)
    19ad:	mov    -0x38(%rsp),%rcx
    19b2:	add    %rbx,%rcx
    19b5:	lea    0x0(%rbp,%rcx,4),%rcx
    19ba:	mov    %rcx,-0x28(%rsp)
    19bf:	cmpq   $0x2,-0x18(%rsp)
    19c5:	mov    (%r8),%edi
    19c8:	jbe    1ac3 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x1c3>
    19ce:	lea    0x4(%rax),%r13
    19d2:	mov    %rdx,%rcx
    19d5:	sub    %r13,%rcx
    19d8:	cmp    $0x8,%rcx
    19dc:	jbe    1ac3 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x1c3>
    19e2:	movd   %edi,%xmm4
    19e6:	xor    %ecx,%ecx
    19e8:	pshufd $0x0,%xmm4,%xmm2
    19ed:	movdqa %xmm2,%xmm3
    19f1:	psrlq  $0x20,%xmm3
    19f6:	cs nopw 0x0(%rax,%rax,1)
    1a00:	movdqu (%rax,%rcx,1),%xmm0
    1a05:	movdqa %xmm0,%xmm1
    1a09:	psrlq  $0x20,%xmm0
    1a0e:	pmuludq %xmm2,%xmm1
    1a12:	pmuludq %xmm3,%xmm0
    1a16:	pshufd $0x8,%xmm1,%xmm1
    1a1b:	pshufd $0x8,%xmm0,%xmm0
    1a20:	punpckldq %xmm0,%xmm1
    1a24:	movdqu (%rdx,%rcx,1),%xmm0
    1a29:	paddd  %xmm1,%xmm0
    1a2d:	movups %xmm0,(%rdx,%rcx,1)
    1a31:	add    $0x10,%rcx
    1a35:	cmp    %rsi,%rcx
    1a38:	jne    1a00 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x100>
    1a3a:	cmpq   $0x0,-0x48(%rsp)
    1a40:	je     1a9d <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x19d>
    1a42:	lea    (%r14,%rbx,1),%rcx
    1a46:	lea    (%r14,%r9,1),%r13
    1a4a:	mov    %rcx,-0x50(%rsp)
    1a4f:	mov    (%r10,%r13,4),%ecx
    1a53:	imul   %edi,%ecx
    1a56:	mov    %ecx,%r13d
    1a59:	mov    -0x50(%rsp),%rcx
    1a5e:	add    %r13d,0x0(%rbp,%rcx,4)
    1a63:	mov    -0x40(%rsp),%rcx
    1a68:	cmp    %r11,%rcx
    1a6b:	jae    1a9d <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x19d>
    1a6d:	add    %r9,%rcx
    1a70:	mov    (%r10,%rcx,4),%r13d
    1a74:	imul   %edi,%r13d
    1a78:	mov    %r13d,%ecx
    1a7b:	mov    -0x30(%rsp),%r13
    1a80:	add    %ecx,0x0(%r13)
    1a84:	mov    -0x38(%rsp),%rcx
    1a89:	cmp    %r11,%rcx
    1a8c:	jae    1a9d <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x19d>
    1a8e:	add    %r9,%rcx
    1a91:	imul   (%r10,%rcx,4),%edi
    1a96:	mov    -0x28(%rsp),%rcx
    1a9b:	add    %edi,(%rcx)
    1a9d:	add    $0x4,%r8
    1aa1:	add    %r12,%rax
    1aa4:	add    %r11,%r9
    1aa7:	cmp    %r15,%r8
    1aaa:	je     1b0c <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x20c>
    1aac:	lea    0x4(%rax),%r13
    1ab0:	mov    %rdx,%rcx
    1ab3:	mov    (%r8),%edi
    1ab6:	sub    %r13,%rcx
    1ab9:	cmp    $0x8,%rcx
    1abd:	ja     19e2 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0xe2>
    1ac3:	mov    %r8,-0x50(%rsp)
    1ac8:	mov    -0x20(%rsp),%rcx
    1acd:	lea    (%rax,%r12,1),%r13
    1ad1:	data16 cs nopw 0x0(%rax,%rax,1)
    1adc:	nopl   0x0(%rax)
    1ae0:	mov    (%rax),%r8d
    1ae3:	add    $0x4,%rax
    1ae7:	imul   %edi,%r8d
    1aeb:	add    %r8d,(%rcx)
    1aee:	add    $0x4,%rcx
    1af2:	cmp    %r13,%rax
    1af5:	jne    1ae0 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x1e0>
    1af7:	mov    -0x50(%rsp),%r8
    1afc:	add    %r11,%r9
    1aff:	add    $0x4,%r8
    1b03:	cmp    %r15,%r8
    1b06:	jne    19bf <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0xbf>
    1b0c:	mov    -0x10(%rsp),%rdi
    1b11:	add    %r12,%r15
    1b14:	add    %r12,%rdx
    1b17:	add    %r11,%rbx
    1b1a:	add    $0x1,%rdi
    1b1e:	cmp    %rdi,%r11
    1b21:	jne    1980 <_Z15kern_k08_matmulRSt6vectorIiSaIiEERKS1_S4_m+0x80>
    1b27:	pop    %rbx
    1b28:	pop    %rbp
    1b29:	pop    %r12
    1b2b:	pop    %r13
    1b2d:	pop    %r14
    1b2f:	pop    %r15
    1b31:	ret
    1b32:	ret
    1b33:	cs nopw 0x0(%rax,%rax,1)
    1b3d:	nopl   (%rax)
