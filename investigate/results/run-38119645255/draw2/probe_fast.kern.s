0000000000001270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1270:	mov    (%rsi),%r8
    1273:	mov    0x8(%rsi),%rax
    1277:	sub    %r8,%rax
    127a:	je     135e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1280:	sar    $0x2,%rax
    1284:	mov    (%rdx),%rsi
    1287:	mov    0x8(%rdx),%rcx
    128b:	sub    %rsi,%rcx
    128e:	sar    $0x2,%rcx
    1292:	mov    (%rdi),%r9
    1295:	mov    0x8(%rdi),%rdx
    1299:	sub    %r9,%rdx
    129c:	sar    $0x2,%rdx
    12a0:	cmp    $0x1,%rax
    12a4:	adc    $0x0,%rax
    12a8:	lea    -0x1(%rax),%r10
    12ac:	cmp    %rdx,%r10
    12af:	cmovae %rdx,%r10
    12b3:	cmp    %rcx,%r10
    12b6:	cmovae %rcx,%r10
    12ba:	cmp    $0x7,%r10
    12be:	ja     12c4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    12c0:	xor    %edi,%edi
    12c2:	jmp    131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12c4:	mov    %r9,%r11
    12c7:	sub    %r8,%r11
    12ca:	xor    %edi,%edi
    12cc:	cmp    $0x10,%r11
    12d0:	jb     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12d2:	mov    %r9,%r11
    12d5:	sub    %rsi,%r11
    12d8:	cmp    $0x10,%r11
    12dc:	jb     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    12de:	inc    %r10
    12e1:	mov    %r10d,%edi
    12e4:	and    $0x3,%edi
    12e7:	mov    $0x4,%r11d
    12ed:	cmovne %rdi,%r11
    12f1:	mov    %r10,%rdi
    12f4:	sub    %r11,%rdi
    12f7:	xor    %r10d,%r10d
    12fa:	nopw   0x0(%rax,%rax,1)
    1300:	movdqu (%r8,%r10,4),%xmm0
    1306:	movdqu (%rsi,%r10,4),%xmm1
    130c:	paddd  %xmm0,%xmm1
    1310:	movdqu %xmm1,(%r9,%r10,4)
    1316:	add    $0x4,%r10
    131a:	cmp    %r10,%rdi
    131d:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    131f:	sub    %rdi,%rdx
    1322:	sub    %rdi,%rcx
    1325:	sub    %rdi,%rax
    1328:	lea    (%r8,%rdi,4),%r8
    132c:	lea    (%rsi,%rdi,4),%rsi
    1330:	lea    (%r9,%rdi,4),%rdi
    1334:	xor    %r9d,%r9d
    1337:	nopw   0x0(%rax,%rax,1)
    1340:	cmp    %r9,%rcx
    1343:	je     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    1345:	cmp    %r9,%rdx
    1348:	je     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    134a:	mov    (%rsi,%r9,4),%r10d
    134e:	add    (%r8,%r9,4),%r10d
    1352:	mov    %r10d,(%rdi,%r9,4)
    1356:	inc    %r9
    1359:	cmp    %r9,%rax
    135c:	jne    1340 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    135e:	ret
    135f:	ud2
    1361:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1652:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1657:	lea    0x40(%rsp),%rsi
    165c:	mov    $0x1,%edi
    1661:	call   1080 <clock_gettime@plt>
    1666:	mov    0x40(%rsp),%r14
    166b:	mov    0x48(%rsp),%rbp
    1670:	cmpq   $0x0,0x18(%rsp)
    1676:	jle    16a3 <_Z17k02_original_mainiPPc+0x333>
    1678:	mov    %rsp,%r15
    167b:	lea    0x50(%rsp),%r12
    1680:	lea    0x20(%rsp),%r13
    1685:	mov    0x18(%rsp),%rbx
    168a:	nopw   0x0(%rax,%rax,1)
    1690:	mov    %r15,%rdi
    1693:	mov    %r12,%rsi
    1696:	mov    %r13,%rdx
    1699:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    169e:	dec    %rbx
    16a1:	jne    1690 <_Z17k02_original_mainiPPc+0x320>
    16a3:	movabs $0x14650fb0739d0383,%r15
    16ad:	lea    0x40(%rsp),%rsi
    16b2:	mov    $0x1,%edi
    16b7:	call   1080 <clock_gettime@plt>
    16bc:	mov    0x40(%rsp),%rax
    16c1:	sub    %r14,%rax
    16c4:	mov    0x48(%rsp),%rcx
    16c9:	sub    %rbp,%rcx
    16cc:	imul   $0x3b9aca00,%rax,%rax
    16d3:	add    %rcx,%rax
    16d6:	mov    (%rsp),%r9
    16da:	mov    0x8(%rsp),%rdi
    16df:	cmp    %rdi,%r9
    16e2:	je     1718 <_Z17k02_original_mainiPPc+0x3a8>
    16e4:	movabs $0x100000001b3,%rsi
    16ee:	mov    0x70(%rsp),%rdx
    16f3:	mov    0x18(%rsp),%rcx
    16f8:	nopl   0x0(%rax,%rax,1)
    1700:	mov    (%r9),%r8d
    1703:	xor    %r15,%r8
    1706:	imul   %rsi,%r8
    170a:	add    $0x4,%r9
    170e:	mov    %r8,%r15
    1711:	cmp    %rdi,%r9
    1714:	jne    1700 <_Z17k02_original_mainiPPc+0x390>
    1716:	jmp    1725 <_Z17k02_original_mainiPPc+0x3b5>
    1718:	mov    %r15,%r8
    171b:	mov    0x70(%rsp),%rdx
    1720:	mov    0x18(%rsp),%rcx
    1725:	movq   %rax,%xmm1
    172a:	punpckldq 0x18de(%rip),%xmm1        # 3010 <_IO_stdin_used+0x10>
    1732:	subpd  0x18e6(%rip),%xmm1        # 3020 <_IO_stdin_used+0x20>
    173a:	movapd %xmm1,%xmm0
    173e:	unpckhpd %xmm1,%xmm0
    1742:	addsd  %xmm1,%xmm0
    1746:	xorps  %xmm1,%xmm1
    1749:	cvtsi2sd %rcx,%xmm1
    174e:	divsd  %xmm1,%xmm0
    1752:	lea    0x196f(%rip),%rdi        # 30c8 <_IO_stdin_used+0xc8>
    1759:	mov    $0x4,%esi
    175e:	mov    $0x1,%al
    1760:	call   1030 <printf@plt>
    1765:	mov    (%rsp),%rdi
    1769:	test   %rdi,%rdi
    176c:	je     1798 <_Z17k02_original_mainiPPc+0x428>
    176e:	mov    %rdi,0x8(%rsp)
    1773:	cmpb   $0x1,0x3956(%rip)        # 50d0 <_ZL7g_arena>
    177a:	jne    1793 <_Z17k02_original_mainiPPc+0x423>
    177c:	mov    0x3975(%rip),%rax        # 50f8 <_ZL5g_end>
    1783:	cmp    %rdi,%rax
    1786:	jbe    1793 <_Z17k02_original_mainiPPc+0x423>
    1788:	add    $0xfffffffffc000000,%rax
    178e:	cmp    %rdi,%rax
    1791:	jbe    1798 <_Z17k02_original_mainiPPc+0x428>
    1793:	call   10c0 <free@plt>
    1798:	mov    0x20(%rsp),%rdi
    179d:	test   %rdi,%rdi
    17a0:	je     17cc <_Z17k02_original_mainiPPc+0x45c>
    17a2:	mov    %rdi,0x28(%rsp)
    17a7:	cmpb   $0x1,0x3922(%rip)        # 50d0 <_ZL7g_arena>
    17ae:	jne    17c7 <_Z17k02_original_mainiPPc+0x457>
    17b0:	mov    0x3941(%rip),%rax        # 50f8 <_ZL5g_end>
    17b7:	cmp    %rdi,%rax
    17ba:	jbe    17c7 <_Z17k02_original_mainiPPc+0x457>
    17bc:	add    $0xfffffffffc000000,%rax
    17c2:	cmp    %rdi,%rax
    17c5:	jbe    17cc <_Z17k02_original_mainiPPc+0x45c>
    17c7:	call   10c0 <free@plt>
    17cc:	mov    0x50(%rsp),%rdi
    17d1:	test   %rdi,%rdi
    17d4:	je     1800 <_Z17k02_original_mainiPPc+0x490>
    17d6:	mov    %rdi,0x58(%rsp)
    17db:	cmpb   $0x1,0x38ee(%rip)        # 50d0 <_ZL7g_arena>
    17e2:	jne    17fb <_Z17k02_original_mainiPPc+0x48b>
    17e4:	mov    0x390d(%rip),%rax        # 50f8 <_ZL5g_end>
    17eb:	cmp    %rdi,%rax
    17ee:	jbe    17fb <_Z17k02_original_mainiPPc+0x48b>
    17f0:	add    $0xfffffffffc000000,%rax
    17f6:	cmp    %rdi,%rax
    17f9:	jbe    1800 <_Z17k02_original_mainiPPc+0x490>
    17fb:	call   10c0 <free@plt>
    1800:	xor    %eax,%eax
    1802:	add    $0x78,%rsp
    1806:	pop    %rbx
    1807:	pop    %r12
    1809:	pop    %r13
    180b:	pop    %r14
    180d:	pop    %r15
    180f:	pop    %rbp
    1810:	ret
    1811:	mov    0x37b8(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    1818:	mov    (%rax),%rdi
    181b:	mov    (%r14),%rdx
    181e:	lea    0x1876(%rip),%rsi        # 309b <_IO_stdin_used+0x9b>
    1825:	xor    %eax,%eax
    1827:	call   1160 <fprintf@plt>
    182c:	mov    $0x2,%edi
    1831:	call   1090 <exit@plt>
    1836:	mov    0x3793(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    183d:	mov    (%rax),%rcx
    1840:	lea    0x186b(%rip),%rdi        # 30b2 <_IO_stdin_used+0xb2>
    1847:	mov    $0xe,%esi
    184c:	mov    $0x1,%edx
    1851:	call   1150 <fwrite@plt>
    1856:	mov    $0x2,%edi
    185b:	call   1090 <exit@plt>
    1860:	lea    0x50(%rsp),%rdi
    1865:	call   2030 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8fe180100Ev>
    186a:	mov    %rax,%rbx
    186d:	lea    0x40(%rsp),%rdi
    1872:	call   1fe0 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8fe180100Ev>
    1877:	lea    0x20(%rsp),%rdi
    187c:	call   1fa0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8fe180100Ev>
    1881:	jmp    188e <_Z17k02_original_mainiPPc+0x51e>
    1883:	mov    %rax,%rbx
    1886:	mov    %rsp,%rdi
    1889:	call   1fe0 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8fe180100Ev>
    188e:	lea    0x50(%rsp),%rdi
    1893:	call   1fa0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8fe180100Ev>
    1898:	mov    %rbx,%rdi
    189b:	call   10e0 <_Unwind_Resume@plt>
    18a0:	mov    %rax,%rbx
    18a3:	lea    0x20(%rsp),%rdi
    18a8:	call   1fe0 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8fe180100Ev>
    18ad:	mov    %rbx,%rdi
    18b0:	call   10e0 <_Unwind_Resume@plt>
    18b5:	data16 cs nopw 0x0(%rax,%rax,1)
    1d12:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1d17:	lea    0x40(%rsp),%rsi
    1d1c:	mov    $0x1,%edi
    1d21:	call   1080 <clock_gettime@plt>
    1d26:	mov    0x40(%rsp),%r14
    1d2b:	mov    0x48(%rsp),%rbp
    1d30:	cmpq   $0x0,0x68(%rsp)
    1d36:	jle    1d63 <main+0x3a3>
    1d38:	mov    %rsp,%r15
    1d3b:	lea    0x50(%rsp),%r12
    1d40:	lea    0x20(%rsp),%r13
    1d45:	mov    0x68(%rsp),%rbx
    1d4a:	nopw   0x0(%rax,%rax,1)
    1d50:	mov    %r15,%rdi
    1d53:	mov    %r12,%rsi
    1d56:	mov    %r13,%rdx
    1d59:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1d5e:	dec    %rbx
    1d61:	jne    1d50 <main+0x390>
    1d63:	movabs $0x14650fb0739d0383,%r15
    1d6d:	lea    0x40(%rsp),%rsi
    1d72:	mov    $0x1,%edi
    1d77:	call   1080 <clock_gettime@plt>
    1d7c:	mov    0x40(%rsp),%rax
    1d81:	sub    %r14,%rax
    1d84:	mov    0x48(%rsp),%rcx
    1d89:	sub    %rbp,%rcx
    1d8c:	imul   $0x3b9aca00,%rax,%rax
    1d93:	add    %rcx,%rax
    1d96:	movq   %rax,%xmm1
    1d9b:	punpckldq 0x126d(%rip),%xmm1        # 3010 <_IO_stdin_used+0x10>
    1da3:	subpd  0x1275(%rip),%xmm1        # 3020 <_IO_stdin_used+0x20>
    1dab:	movapd %xmm1,%xmm0
    1daf:	unpckhpd %xmm1,%xmm0
    1db3:	addsd  %xmm1,%xmm0
    1db7:	mov    0x68(%rsp),%rcx
    1dbc:	xorps  %xmm1,%xmm1
    1dbf:	cvtsi2sd %rcx,%xmm1
    1dc4:	divsd  %xmm1,%xmm0
    1dc8:	mov    (%rsp),%r10
    1dcc:	mov    0x8(%rsp),%rax
    1dd1:	cmp    %rax,%r10
    1dd4:	je     1e08 <main+0x448>
    1dd6:	movabs $0x100000001b3,%rdi
    1de0:	mov    %r10,%rsi
    1de3:	mov    0x70(%rsp),%rdx
    1de8:	nopl   0x0(%rax,%rax,1)
    1df0:	mov    (%rsi),%r8d
    1df3:	xor    %r15,%r8
    1df6:	imul   %rdi,%r8
    1dfa:	add    $0x4,%rsi
    1dfe:	mov    %r8,%r15
    1e01:	cmp    %rax,%rsi
    1e04:	jne    1df0 <main+0x430>
    1e06:	jmp    1e10 <main+0x450>
    1e08:	mov    %r15,%r8
    1e0b:	mov    0x70(%rsp),%rdx
    1e10:	mov    0x50(%rsp),%r9
    1e15:	and    $0xfff,%r9d
    1e1c:	mov    0x20(%rsp),%r11
    1e21:	and    $0xfff,%r11d
    1e28:	and    $0xfff,%r10d
    1e2f:	lea    0x1221(%rip),%rdi        # 3057 <_IO_stdin_used+0x57>
    1e36:	mov    $0x4,%esi
    1e3b:	mov    $0x1,%al
    1e3d:	push   %r10
    1e3f:	push   %r11
    1e41:	call   1030 <printf@plt>
    1e46:	add    $0x10,%rsp
    1e4a:	mov    (%rsp),%rdi
    1e4e:	test   %rdi,%rdi
    1e51:	je     1e7d <main+0x4bd>
    1e53:	mov    %rdi,0x8(%rsp)
    1e58:	cmpb   $0x1,0x3271(%rip)        # 50d0 <_ZL7g_arena>
    1e5f:	jne    1e78 <main+0x4b8>
    1e61:	mov    0x3290(%rip),%rax        # 50f8 <_ZL5g_end>
    1e68:	cmp    %rdi,%rax
    1e6b:	jbe    1e78 <main+0x4b8>
    1e6d:	add    $0xfffffffffc000000,%rax
    1e73:	cmp    %rdi,%rax
    1e76:	jbe    1e7d <main+0x4bd>
    1e78:	call   10c0 <free@plt>
    1e7d:	mov    0x20(%rsp),%rdi
    1e82:	test   %rdi,%rdi
    1e85:	je     1eb1 <main+0x4f1>
    1e87:	mov    %rdi,0x28(%rsp)
    1e8c:	cmpb   $0x1,0x323d(%rip)        # 50d0 <_ZL7g_arena>
    1e93:	jne    1eac <main+0x4ec>
    1e95:	mov    0x325c(%rip),%rax        # 50f8 <_ZL5g_end>
    1e9c:	cmp    %rdi,%rax
    1e9f:	jbe    1eac <main+0x4ec>
    1ea1:	add    $0xfffffffffc000000,%rax
    1ea7:	cmp    %rdi,%rax
    1eaa:	jbe    1eb1 <main+0x4f1>
    1eac:	call   10c0 <free@plt>
    1eb1:	mov    0x50(%rsp),%rdi
    1eb6:	test   %rdi,%rdi
    1eb9:	je     1ee5 <main+0x525>
    1ebb:	mov    %rdi,0x58(%rsp)
    1ec0:	cmpb   $0x1,0x3209(%rip)        # 50d0 <_ZL7g_arena>
    1ec7:	jne    1ee0 <main+0x520>
    1ec9:	mov    0x3228(%rip),%rax        # 50f8 <_ZL5g_end>
    1ed0:	cmp    %rdi,%rax
    1ed3:	jbe    1ee0 <main+0x520>
    1ed5:	add    $0xfffffffffc000000,%rax
    1edb:	cmp    %rdi,%rax
    1ede:	jbe    1ee5 <main+0x525>
    1ee0:	call   10c0 <free@plt>
    1ee5:	xor    %eax,%eax
    1ee7:	add    $0x78,%rsp
    1eeb:	pop    %rbx
    1eec:	pop    %r12
    1eee:	pop    %r13
    1ef0:	pop    %r14
    1ef2:	pop    %r15
    1ef4:	pop    %rbp
    1ef5:	ret
    1ef6:	mov    0x30d3(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    1efd:	mov    (%rax),%rdi
    1f00:	mov    (%r14),%rdx
    1f03:	lea    0x1191(%rip),%rsi        # 309b <_IO_stdin_used+0x9b>
    1f0a:	xor    %eax,%eax
    1f0c:	call   1160 <fprintf@plt>
    1f11:	mov    $0x2,%edi
    1f16:	call   1090 <exit@plt>
    1f1b:	mov    0x30ae(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    1f22:	mov    (%rax),%rcx
    1f25:	lea    0x1186(%rip),%rdi        # 30b2 <_IO_stdin_used+0xb2>
    1f2c:	mov    $0xe,%esi
    1f31:	mov    $0x1,%edx
    1f36:	call   1150 <fwrite@plt>
    1f3b:	mov    $0x2,%edi
    1f40:	call   1090 <exit@plt>
    1f45:	lea    0x50(%rsp),%rdi
    1f4a:	call   2030 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8fe180100Ev>
    1f4f:	mov    %rax,%rbx
    1f52:	lea    0x40(%rsp),%rdi
    1f57:	call   1fe0 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8fe180100Ev>
    1f5c:	lea    0x20(%rsp),%rdi
    1f61:	call   1fa0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8fe180100Ev>
    1f66:	jmp    1f73 <main+0x5b3>
    1f68:	mov    %rax,%rbx
    1f6b:	mov    %rsp,%rdi
    1f6e:	call   1fe0 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8fe180100Ev>
    1f73:	lea    0x50(%rsp),%rdi
    1f78:	call   1fa0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8fe180100Ev>
    1f7d:	mov    %rbx,%rdi
    1f80:	call   10e0 <_Unwind_Resume@plt>
    1f85:	mov    %rax,%rbx
    1f88:	lea    0x20(%rsp),%rdi
    1f8d:	call   1fe0 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8fe180100Ev>
    1f92:	mov    %rbx,%rdi
    1f95:	call   10e0 <_Unwind_Resume@plt>
    1f9a:	nopw   0x0(%rax,%rax,1)
