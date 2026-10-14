0000000000001270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1270:	mov    (%rsi),%rax
    1273:	mov    0x8(%rsi),%rcx
    1277:	sub    %rax,%rcx
    127a:	je     13b1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1280:	sar    $0x2,%rcx
    1284:	mov    (%rdx),%rdx
    1287:	mov    (%rdi),%rsi
    128a:	cmp    $0x1,%rcx
    128e:	mov    %rcx,%rdi
    1291:	adc    $0x0,%rdi
    1295:	cmp    $0xc,%rcx
    1299:	jae    1334 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    129f:	xor    %r8d,%r8d
    12a2:	mov    %rdi,%r10
    12a5:	mov    %r8,%r9
    12a8:	and    $0x3,%r10
    12ac:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    12ae:	mov    %r8,%r9
    12b1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    (%rdx,%r9,4),%r11d
    12c4:	add    (%rax,%r9,4),%r11d
    12c8:	mov    %r11d,(%rsi,%r9,4)
    12cc:	inc    %r9
    12cf:	dec    %r10
    12d2:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    12d4:	sub    %rdi,%r8
    12d7:	cmp    $0xfffffffffffffffc,%r8
    12db:	ja     13b1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	mov    (%rdx,%r9,4),%edi
    12f4:	add    (%rax,%r9,4),%edi
    12f8:	mov    %edi,(%rsi,%r9,4)
    12fc:	mov    0x4(%rdx,%r9,4),%edi
    1301:	add    0x4(%rax,%r9,4),%edi
    1306:	mov    %edi,0x4(%rsi,%r9,4)
    130b:	mov    0x8(%rdx,%r9,4),%edi
    1310:	add    0x8(%rax,%r9,4),%edi
    1315:	mov    %edi,0x8(%rsi,%r9,4)
    131a:	mov    0xc(%rdx,%r9,4),%edi
    131f:	add    0xc(%rax,%r9,4),%edi
    1324:	mov    %edi,0xc(%rsi,%r9,4)
    1329:	add    $0x4,%r9
    132d:	cmp    %r9,%rcx
    1330:	jne    12f0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    1332:	jmp    13b1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
    1334:	mov    %rsi,%r9
    1337:	sub    %rax,%r9
    133a:	xor    %r8d,%r8d
    133d:	cmp    $0x20,%r9
    1341:	jb     12a2 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1347:	mov    %rsi,%r9
    134a:	sub    %rdx,%r9
    134d:	cmp    $0x20,%r9
    1351:	jb     12a2 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1357:	mov    %rdi,%r8
    135a:	and    $0xfffffffffffffff8,%r8
    135e:	xor    %r9d,%r9d
    1361:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1370:	movdqu (%rax,%r9,4),%xmm0
    1376:	movdqu 0x10(%rax,%r9,4),%xmm1
    137d:	movdqu (%rdx,%r9,4),%xmm2
    1383:	paddd  %xmm0,%xmm2
    1387:	movdqu 0x10(%rdx,%r9,4),%xmm0
    138e:	paddd  %xmm1,%xmm0
    1392:	movdqu %xmm2,(%rsi,%r9,4)
    1398:	movdqu %xmm0,0x10(%rsi,%r9,4)
    139f:	add    $0x8,%r9
    13a3:	cmp    %r9,%r8
    13a6:	jne    1370 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    13a8:	cmp    %r8,%rdi
    13ab:	jne    12a2 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    13b1:	ret
    13b2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    16a2:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    16a7:	lea    0x40(%rsp),%rsi
    16ac:	mov    $0x1,%edi
    16b1:	call   1080 <clock_gettime@plt>
    16b6:	mov    0x40(%rsp),%r14
    16bb:	mov    0x48(%rsp),%rbp
    16c0:	cmpq   $0x0,0x18(%rsp)
    16c6:	jle    16f3 <_Z17k02_original_mainiPPc+0x333>
    16c8:	mov    %rsp,%r15
    16cb:	lea    0x50(%rsp),%r12
    16d0:	lea    0x20(%rsp),%r13
    16d5:	mov    0x18(%rsp),%rbx
    16da:	nopw   0x0(%rax,%rax,1)
    16e0:	mov    %r15,%rdi
    16e3:	mov    %r12,%rsi
    16e6:	mov    %r13,%rdx
    16e9:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    16ee:	dec    %rbx
    16f1:	jne    16e0 <_Z17k02_original_mainiPPc+0x320>
    16f3:	movabs $0x14650fb0739d0383,%r15
    16fd:	lea    0x40(%rsp),%rsi
    1702:	mov    $0x1,%edi
    1707:	call   1080 <clock_gettime@plt>
    170c:	mov    0x40(%rsp),%rax
    1711:	sub    %r14,%rax
    1714:	mov    0x48(%rsp),%rcx
    1719:	sub    %rbp,%rcx
    171c:	imul   $0x3b9aca00,%rax,%rax
    1723:	add    %rcx,%rax
    1726:	mov    (%rsp),%r9
    172a:	mov    0x8(%rsp),%rdi
    172f:	cmp    %rdi,%r9
    1732:	je     1768 <_Z17k02_original_mainiPPc+0x3a8>
    1734:	movabs $0x100000001b3,%rsi
    173e:	mov    0x70(%rsp),%rdx
    1743:	mov    0x18(%rsp),%rcx
    1748:	nopl   0x0(%rax,%rax,1)
    1750:	mov    (%r9),%r8d
    1753:	xor    %r15,%r8
    1756:	imul   %rsi,%r8
    175a:	add    $0x4,%r9
    175e:	mov    %r8,%r15
    1761:	cmp    %rdi,%r9
    1764:	jne    1750 <_Z17k02_original_mainiPPc+0x390>
    1766:	jmp    1775 <_Z17k02_original_mainiPPc+0x3b5>
    1768:	mov    %r15,%r8
    176b:	mov    0x70(%rsp),%rdx
    1770:	mov    0x18(%rsp),%rcx
    1775:	movq   %rax,%xmm1
    177a:	punpckldq 0x188e(%rip),%xmm1        # 3010 <_IO_stdin_used+0x10>
    1782:	subpd  0x1896(%rip),%xmm1        # 3020 <_IO_stdin_used+0x20>
    178a:	movapd %xmm1,%xmm0
    178e:	unpckhpd %xmm1,%xmm0
    1792:	addsd  %xmm1,%xmm0
    1796:	xorps  %xmm1,%xmm1
    1799:	cvtsi2sd %rcx,%xmm1
    179e:	divsd  %xmm1,%xmm0
    17a2:	lea    0x191f(%rip),%rdi        # 30c8 <_IO_stdin_used+0xc8>
    17a9:	mov    $0x2,%esi
    17ae:	mov    $0x1,%al
    17b0:	call   1030 <printf@plt>
    17b5:	mov    (%rsp),%rdi
    17b9:	test   %rdi,%rdi
    17bc:	je     17e8 <_Z17k02_original_mainiPPc+0x428>
    17be:	mov    %rdi,0x8(%rsp)
    17c3:	cmpb   $0x1,0x3906(%rip)        # 50d0 <_ZL7g_arena>
    17ca:	jne    17e3 <_Z17k02_original_mainiPPc+0x423>
    17cc:	mov    0x3925(%rip),%rax        # 50f8 <_ZL5g_end>
    17d3:	cmp    %rdi,%rax
    17d6:	jbe    17e3 <_Z17k02_original_mainiPPc+0x423>
    17d8:	add    $0xfffffffffc000000,%rax
    17de:	cmp    %rdi,%rax
    17e1:	jbe    17e8 <_Z17k02_original_mainiPPc+0x428>
    17e3:	call   10c0 <free@plt>
    17e8:	mov    0x20(%rsp),%rdi
    17ed:	test   %rdi,%rdi
    17f0:	je     181c <_Z17k02_original_mainiPPc+0x45c>
    17f2:	mov    %rdi,0x28(%rsp)
    17f7:	cmpb   $0x1,0x38d2(%rip)        # 50d0 <_ZL7g_arena>
    17fe:	jne    1817 <_Z17k02_original_mainiPPc+0x457>
    1800:	mov    0x38f1(%rip),%rax        # 50f8 <_ZL5g_end>
    1807:	cmp    %rdi,%rax
    180a:	jbe    1817 <_Z17k02_original_mainiPPc+0x457>
    180c:	add    $0xfffffffffc000000,%rax
    1812:	cmp    %rdi,%rax
    1815:	jbe    181c <_Z17k02_original_mainiPPc+0x45c>
    1817:	call   10c0 <free@plt>
    181c:	mov    0x50(%rsp),%rdi
    1821:	test   %rdi,%rdi
    1824:	je     1850 <_Z17k02_original_mainiPPc+0x490>
    1826:	mov    %rdi,0x58(%rsp)
    182b:	cmpb   $0x1,0x389e(%rip)        # 50d0 <_ZL7g_arena>
    1832:	jne    184b <_Z17k02_original_mainiPPc+0x48b>
    1834:	mov    0x38bd(%rip),%rax        # 50f8 <_ZL5g_end>
    183b:	cmp    %rdi,%rax
    183e:	jbe    184b <_Z17k02_original_mainiPPc+0x48b>
    1840:	add    $0xfffffffffc000000,%rax
    1846:	cmp    %rdi,%rax
    1849:	jbe    1850 <_Z17k02_original_mainiPPc+0x490>
    184b:	call   10c0 <free@plt>
    1850:	xor    %eax,%eax
    1852:	add    $0x78,%rsp
    1856:	pop    %rbx
    1857:	pop    %r12
    1859:	pop    %r13
    185b:	pop    %r14
    185d:	pop    %r15
    185f:	pop    %rbp
    1860:	ret
    1861:	mov    0x3768(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    1868:	mov    (%rax),%rdi
    186b:	mov    (%r14),%rdx
    186e:	lea    0x1826(%rip),%rsi        # 309b <_IO_stdin_used+0x9b>
    1875:	xor    %eax,%eax
    1877:	call   1160 <fprintf@plt>
    187c:	mov    $0x2,%edi
    1881:	call   1090 <exit@plt>
    1886:	mov    0x3743(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    188d:	mov    (%rax),%rcx
    1890:	lea    0x181b(%rip),%rdi        # 30b2 <_IO_stdin_used+0xb2>
    1897:	mov    $0xe,%esi
    189c:	mov    $0x1,%edx
    18a1:	call   1150 <fwrite@plt>
    18a6:	mov    $0x2,%edi
    18ab:	call   1090 <exit@plt>
    18b0:	lea    0x50(%rsp),%rdi
    18b5:	call   2080 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8ne180100Ev>
    18ba:	mov    %rax,%rbx
    18bd:	lea    0x40(%rsp),%rdi
    18c2:	call   2030 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8ne180100Ev>
    18c7:	lea    0x20(%rsp),%rdi
    18cc:	call   1ff0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8ne180100Ev>
    18d1:	jmp    18de <_Z17k02_original_mainiPPc+0x51e>
    18d3:	mov    %rax,%rbx
    18d6:	mov    %rsp,%rdi
    18d9:	call   2030 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8ne180100Ev>
    18de:	lea    0x50(%rsp),%rdi
    18e3:	call   1ff0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8ne180100Ev>
    18e8:	mov    %rbx,%rdi
    18eb:	call   10e0 <_Unwind_Resume@plt>
    18f0:	mov    %rax,%rbx
    18f3:	lea    0x20(%rsp),%rdi
    18f8:	call   2030 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8ne180100Ev>
    18fd:	mov    %rbx,%rdi
    1900:	call   10e0 <_Unwind_Resume@plt>
    1905:	data16 cs nopw 0x0(%rax,%rax,1)
    1d62:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1d67:	lea    0x40(%rsp),%rsi
    1d6c:	mov    $0x1,%edi
    1d71:	call   1080 <clock_gettime@plt>
    1d76:	mov    0x40(%rsp),%r14
    1d7b:	mov    0x48(%rsp),%rbp
    1d80:	cmpq   $0x0,0x68(%rsp)
    1d86:	jle    1db3 <main+0x3a3>
    1d88:	mov    %rsp,%r15
    1d8b:	lea    0x50(%rsp),%r12
    1d90:	lea    0x20(%rsp),%r13
    1d95:	mov    0x68(%rsp),%rbx
    1d9a:	nopw   0x0(%rax,%rax,1)
    1da0:	mov    %r15,%rdi
    1da3:	mov    %r12,%rsi
    1da6:	mov    %r13,%rdx
    1da9:	call   1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1dae:	dec    %rbx
    1db1:	jne    1da0 <main+0x390>
    1db3:	movabs $0x14650fb0739d0383,%r15
    1dbd:	lea    0x40(%rsp),%rsi
    1dc2:	mov    $0x1,%edi
    1dc7:	call   1080 <clock_gettime@plt>
    1dcc:	mov    0x40(%rsp),%rax
    1dd1:	sub    %r14,%rax
    1dd4:	mov    0x48(%rsp),%rcx
    1dd9:	sub    %rbp,%rcx
    1ddc:	imul   $0x3b9aca00,%rax,%rax
    1de3:	add    %rcx,%rax
    1de6:	movq   %rax,%xmm1
    1deb:	punpckldq 0x121d(%rip),%xmm1        # 3010 <_IO_stdin_used+0x10>
    1df3:	subpd  0x1225(%rip),%xmm1        # 3020 <_IO_stdin_used+0x20>
    1dfb:	movapd %xmm1,%xmm0
    1dff:	unpckhpd %xmm1,%xmm0
    1e03:	addsd  %xmm1,%xmm0
    1e07:	mov    0x68(%rsp),%rcx
    1e0c:	xorps  %xmm1,%xmm1
    1e0f:	cvtsi2sd %rcx,%xmm1
    1e14:	divsd  %xmm1,%xmm0
    1e18:	mov    (%rsp),%r10
    1e1c:	mov    0x8(%rsp),%rax
    1e21:	cmp    %rax,%r10
    1e24:	je     1e58 <main+0x448>
    1e26:	movabs $0x100000001b3,%rdi
    1e30:	mov    %r10,%rsi
    1e33:	mov    0x70(%rsp),%rdx
    1e38:	nopl   0x0(%rax,%rax,1)
    1e40:	mov    (%rsi),%r8d
    1e43:	xor    %r15,%r8
    1e46:	imul   %rdi,%r8
    1e4a:	add    $0x4,%rsi
    1e4e:	mov    %r8,%r15
    1e51:	cmp    %rax,%rsi
    1e54:	jne    1e40 <main+0x430>
    1e56:	jmp    1e60 <main+0x450>
    1e58:	mov    %r15,%r8
    1e5b:	mov    0x70(%rsp),%rdx
    1e60:	mov    0x50(%rsp),%r9
    1e65:	and    $0xfff,%r9d
    1e6c:	mov    0x20(%rsp),%r11
    1e71:	and    $0xfff,%r11d
    1e78:	and    $0xfff,%r10d
    1e7f:	lea    0x11d1(%rip),%rdi        # 3057 <_IO_stdin_used+0x57>
    1e86:	mov    $0x2,%esi
    1e8b:	mov    $0x1,%al
    1e8d:	push   %r10
    1e8f:	push   %r11
    1e91:	call   1030 <printf@plt>
    1e96:	add    $0x10,%rsp
    1e9a:	mov    (%rsp),%rdi
    1e9e:	test   %rdi,%rdi
    1ea1:	je     1ecd <main+0x4bd>
    1ea3:	mov    %rdi,0x8(%rsp)
    1ea8:	cmpb   $0x1,0x3221(%rip)        # 50d0 <_ZL7g_arena>
    1eaf:	jne    1ec8 <main+0x4b8>
    1eb1:	mov    0x3240(%rip),%rax        # 50f8 <_ZL5g_end>
    1eb8:	cmp    %rdi,%rax
    1ebb:	jbe    1ec8 <main+0x4b8>
    1ebd:	add    $0xfffffffffc000000,%rax
    1ec3:	cmp    %rdi,%rax
    1ec6:	jbe    1ecd <main+0x4bd>
    1ec8:	call   10c0 <free@plt>
    1ecd:	mov    0x20(%rsp),%rdi
    1ed2:	test   %rdi,%rdi
    1ed5:	je     1f01 <main+0x4f1>
    1ed7:	mov    %rdi,0x28(%rsp)
    1edc:	cmpb   $0x1,0x31ed(%rip)        # 50d0 <_ZL7g_arena>
    1ee3:	jne    1efc <main+0x4ec>
    1ee5:	mov    0x320c(%rip),%rax        # 50f8 <_ZL5g_end>
    1eec:	cmp    %rdi,%rax
    1eef:	jbe    1efc <main+0x4ec>
    1ef1:	add    $0xfffffffffc000000,%rax
    1ef7:	cmp    %rdi,%rax
    1efa:	jbe    1f01 <main+0x4f1>
    1efc:	call   10c0 <free@plt>
    1f01:	mov    0x50(%rsp),%rdi
    1f06:	test   %rdi,%rdi
    1f09:	je     1f35 <main+0x525>
    1f0b:	mov    %rdi,0x58(%rsp)
    1f10:	cmpb   $0x1,0x31b9(%rip)        # 50d0 <_ZL7g_arena>
    1f17:	jne    1f30 <main+0x520>
    1f19:	mov    0x31d8(%rip),%rax        # 50f8 <_ZL5g_end>
    1f20:	cmp    %rdi,%rax
    1f23:	jbe    1f30 <main+0x520>
    1f25:	add    $0xfffffffffc000000,%rax
    1f2b:	cmp    %rdi,%rax
    1f2e:	jbe    1f35 <main+0x525>
    1f30:	call   10c0 <free@plt>
    1f35:	xor    %eax,%eax
    1f37:	add    $0x78,%rsp
    1f3b:	pop    %rbx
    1f3c:	pop    %r12
    1f3e:	pop    %r13
    1f40:	pop    %r14
    1f42:	pop    %r15
    1f44:	pop    %rbp
    1f45:	ret
    1f46:	mov    0x3083(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    1f4d:	mov    (%rax),%rdi
    1f50:	mov    (%r14),%rdx
    1f53:	lea    0x1141(%rip),%rsi        # 309b <_IO_stdin_used+0x9b>
    1f5a:	xor    %eax,%eax
    1f5c:	call   1160 <fprintf@plt>
    1f61:	mov    $0x2,%edi
    1f66:	call   1090 <exit@plt>
    1f6b:	mov    0x305e(%rip),%rax        # 4fd0 <stderr@GLIBC_2.2.5>
    1f72:	mov    (%rax),%rcx
    1f75:	lea    0x1136(%rip),%rdi        # 30b2 <_IO_stdin_used+0xb2>
    1f7c:	mov    $0xe,%esi
    1f81:	mov    $0x1,%edx
    1f86:	call   1150 <fwrite@plt>
    1f8b:	mov    $0x2,%edi
    1f90:	call   1090 <exit@plt>
    1f95:	lea    0x50(%rsp),%rdi
    1f9a:	call   2080 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8ne180100Ev>
    1f9f:	mov    %rax,%rbx
    1fa2:	lea    0x40(%rsp),%rdi
    1fa7:	call   2030 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8ne180100Ev>
    1fac:	lea    0x20(%rsp),%rdi
    1fb1:	call   1ff0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8ne180100Ev>
    1fb6:	jmp    1fc3 <main+0x5b3>
    1fb8:	mov    %rax,%rbx
    1fbb:	mov    %rsp,%rdi
    1fbe:	call   2030 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8ne180100Ev>
    1fc3:	lea    0x50(%rsp),%rdi
    1fc8:	call   1ff0 <_ZNSt3__16vectorIiNS_9allocatorIiEEED2B8ne180100Ev>
    1fcd:	mov    %rbx,%rdi
    1fd0:	call   10e0 <_Unwind_Resume@plt>
    1fd5:	mov    %rax,%rbx
    1fd8:	lea    0x20(%rsp),%rdi
    1fdd:	call   2030 <_ZNSt3__128__exception_guard_exceptionsINS_6vectorIiNS_9allocatorIiEEE16__destroy_vectorEED2B8ne180100Ev>
    1fe2:	mov    %rbx,%rdi
    1fe5:	call   10e0 <_Unwind_Resume@plt>
    1fea:	nopw   0x0(%rax,%rax,1)
