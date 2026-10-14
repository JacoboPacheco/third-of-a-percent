0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%r8
    1223:	mov    0x8(%rsi),%rax
    1227:	sub    %r8,%rax
    122a:	je     130e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xee>
    1230:	sar    $0x2,%rax
    1234:	mov    (%rdx),%rsi
    1237:	mov    0x8(%rdx),%rcx
    123b:	sub    %rsi,%rcx
    123e:	sar    $0x2,%rcx
    1242:	mov    (%rdi),%r9
    1245:	mov    0x8(%rdi),%rdx
    1249:	sub    %r9,%rdx
    124c:	sar    $0x2,%rdx
    1250:	cmp    $0x1,%rax
    1254:	adc    $0x0,%rax
    1258:	lea    -0x1(%rax),%r10
    125c:	cmp    %rdx,%r10
    125f:	cmovae %rdx,%r10
    1263:	cmp    %rcx,%r10
    1266:	cmovae %rcx,%r10
    126a:	cmp    $0x7,%r10
    126e:	ja     1274 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    1270:	xor    %edi,%edi
    1272:	jmp    12cf <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1274:	mov    %r9,%r11
    1277:	sub    %r8,%r11
    127a:	xor    %edi,%edi
    127c:	cmp    $0x10,%r11
    1280:	jb     12cf <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    1282:	mov    %r9,%r11
    1285:	sub    %rsi,%r11
    1288:	cmp    $0x10,%r11
    128c:	jb     12cf <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xaf>
    128e:	inc    %r10
    1291:	mov    %r10d,%edi
    1294:	and    $0x3,%edi
    1297:	mov    $0x4,%r11d
    129d:	cmovne %rdi,%r11
    12a1:	mov    %r10,%rdi
    12a4:	sub    %r11,%rdi
    12a7:	xor    %r10d,%r10d
    12aa:	nopw   0x0(%rax,%rax,1)
    12b0:	movdqu (%r8,%r10,4),%xmm0
    12b6:	movdqu (%rsi,%r10,4),%xmm1
    12bc:	paddd  %xmm0,%xmm1
    12c0:	movdqu %xmm1,(%r9,%r10,4)
    12c6:	add    $0x4,%r10
    12ca:	cmp    %r10,%rdi
    12cd:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12cf:	sub    %rdi,%rdx
    12d2:	sub    %rdi,%rcx
    12d5:	sub    %rdi,%rax
    12d8:	lea    (%r8,%rdi,4),%r8
    12dc:	lea    (%rsi,%rdi,4),%rsi
    12e0:	lea    (%r9,%rdi,4),%rdi
    12e4:	xor    %r9d,%r9d
    12e7:	nopw   0x0(%rax,%rax,1)
    12f0:	cmp    %r9,%rcx
    12f3:	je     130f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    12f5:	cmp    %r9,%rdx
    12f8:	je     130f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xef>
    12fa:	mov    (%rsi,%r9,4),%r10d
    12fe:	add    (%r8,%r9,4),%r10d
    1302:	mov    %r10d,(%rdi,%r9,4)
    1306:	inc    %r9
    1309:	cmp    %r9,%rax
    130c:	jne    12f0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    130e:	ret
    130f:	ud2
    1311:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    15e0:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    15e5:	lea    0x38(%rsp),%rsi
    15ea:	mov    $0x1,%edi
    15ef:	call   1070 <clock_gettime@plt>
    15f4:	mov    0x38(%rsp),%rax
    15f9:	mov    %rax,0x50(%rsp)
    15fe:	mov    0x40(%rsp),%rax
    1603:	mov    %rax,0x48(%rsp)
    1608:	mov    %r15,0x8(%rsp)
    160d:	test   %r15,%r15
    1610:	jle    1643 <main+0x323>
    1612:	lea    0x68(%rsp),%r15
    1617:	lea    0x10(%rsp),%r12
    161c:	lea    0x80(%rsp),%rbx
    1624:	mov    0x8(%rsp),%r14
    1629:	nopl   0x0(%rax)
    1630:	mov    %r15,%rdi
    1633:	mov    %r12,%rsi
    1636:	mov    %rbx,%rdx
    1639:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    163e:	dec    %r14
    1641:	jne    1630 <main+0x310>
    1643:	movabs $0x14650fb0739d0383,%rbx
    164d:	lea    0x38(%rsp),%rsi
    1652:	mov    $0x1,%edi
    1657:	call   1070 <clock_gettime@plt>
    165c:	mov    0x38(%rsp),%r11
    1661:	mov    0x40(%rsp),%rax
    1666:	mov    0x58(%rsp),%rdx
    166b:	test   %rdx,%rdx
    166e:	je     169b <main+0x37b>
    1670:	movabs $0x100000001b3,%r10
    167a:	mov    %ebp,%esi
    167c:	and    $0x7,%esi
    167f:	cmp    $0x1c,%r13
    1683:	mov    0x8(%rsp),%rcx
    1688:	mov    0x30(%rsp),%r14
    168d:	jae    16b1 <main+0x391>
    168f:	mov    (%rsp),%r15
    1693:	mov    %r15,%rdi
    1696:	jmp    1734 <main+0x414>
    169b:	mov    %rbx,%r8
    169e:	mov    0x8(%rsp),%rcx
    16a3:	mov    0x30(%rsp),%r14
    16a8:	mov    (%rsp),%r15
    16ac:	jmp    1756 <main+0x436>
    16b1:	movabs $0x7ffffffffffffffc,%rdi
    16bb:	add    $0xfffffffffffffffc,%rdi
    16bf:	and    %rdi,%rbp
    16c2:	mov    (%rsp),%rdi
    16c6:	cs nopw 0x0(%rax,%rax,1)
    16d0:	mov    (%rdi),%r8d
    16d3:	mov    0x4(%rdi),%r9d
    16d7:	xor    %rbx,%r8
    16da:	imul   %r10,%r8
    16de:	xor    %r8,%r9
    16e1:	imul   %r10,%r9
    16e5:	mov    0x8(%rdi),%r8d
    16e9:	xor    %r9,%r8
    16ec:	imul   %r10,%r8
    16f0:	mov    0xc(%rdi),%r9d
    16f4:	xor    %r8,%r9
    16f7:	imul   %r10,%r9
    16fb:	mov    0x10(%rdi),%r8d
    16ff:	xor    %r9,%r8
    1702:	imul   %r10,%r8
    1706:	mov    0x14(%rdi),%r9d
    170a:	xor    %r8,%r9
    170d:	imul   %r10,%r9
    1711:	mov    0x18(%rdi),%r8d
    1715:	xor    %r9,%r8
    1718:	imul   %r10,%r8
    171c:	mov    0x1c(%rdi),%ebx
    171f:	xor    %r8,%rbx
    1722:	imul   %r10,%rbx
    1726:	add    $0x20,%rdi
    172a:	add    $0xfffffffffffffff8,%rbp
    172e:	jne    16d0 <main+0x3b0>
    1730:	mov    (%rsp),%r15
    1734:	mov    %rbx,%r8
    1737:	test   %rsi,%rsi
    173a:	je     1756 <main+0x436>
    173c:	xor    %r9d,%r9d
    173f:	nop
    1740:	mov    (%rdi,%r9,4),%r8d
    1744:	xor    %rbx,%r8
    1747:	imul   %r10,%r8
    174b:	inc    %r9
    174e:	mov    %r8,%rbx
    1751:	cmp    %r9,%rsi
    1754:	jne    1740 <main+0x420>
    1756:	sub    0x48(%rsp),%rax
    175b:	sub    0x50(%rsp),%r11
    1760:	imul   $0x3b9aca00,%r11,%rsi
    1767:	add    %rax,%rsi
    176a:	movq   %rsi,%xmm1
    176f:	punpckldq 0x899(%rip),%xmm1        # 2010 <_IO_stdin_used+0x10>
    1777:	subpd  0x8a1(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    177f:	movapd %xmm1,%xmm0
    1783:	unpckhpd %xmm1,%xmm0
    1787:	addsd  %xmm1,%xmm0
    178b:	xorps  %xmm1,%xmm1
    178e:	cvtsi2sd %rcx,%xmm1
    1793:	divsd  %xmm1,%xmm0
    1797:	lea    0x8bf(%rip),%rdi        # 205d <_IO_stdin_used+0x5d>
    179e:	mov    $0x4,%esi
    17a3:	mov    $0x1,%al
    17a5:	call   1030 <printf@plt>
    17aa:	mov    %r15,%rdi
    17ad:	call   10a0 <_ZdlPv@plt>
    17b2:	mov    %r14,%rdi
    17b5:	call   10a0 <_ZdlPv@plt>
    17ba:	mov    0x60(%rsp),%rdi
    17bf:	call   10a0 <_ZdlPv@plt>
    17c4:	xor    %eax,%eax
    17c6:	add    $0x98,%rsp
    17cd:	pop    %rbx
    17ce:	pop    %r12
    17d0:	pop    %r13
    17d2:	pop    %r14
    17d4:	pop    %r15
    17d6:	pop    %rbp
    17d7:	ret
    17d8:	mov    0x27f9(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    17df:	mov    (%rax),%rdi
    17e2:	mov    (%rbx),%rdx
    17e5:	lea    0x844(%rip),%rsi        # 2030 <_IO_stdin_used+0x30>
    17ec:	xor    %eax,%eax
    17ee:	call   1110 <fprintf@plt>
    17f3:	mov    $0x2,%edi
    17f8:	call   1090 <exit@plt>
    17fd:	mov    0x27d4(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    1804:	mov    (%rax),%rcx
    1807:	lea    0x839(%rip),%rdi        # 2047 <_IO_stdin_used+0x47>
    180e:	mov    $0xe,%esi
    1813:	mov    $0x1,%edx
    1818:	call   1100 <fwrite@plt>
    181d:	mov    $0x2,%edi
    1822:	call   1090 <exit@plt>
    1827:	lea    0x10(%rsp),%rdi
    182c:	call   1870 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8fe180100Ev>
    1831:	mov    %rax,%r14
    1834:	mov    %r12,%rdi
    1837:	call   10a0 <_ZdlPv@plt>
    183c:	mov    %rbx,%rdi
    183f:	jmp    185b <main+0x53b>
    1841:	mov    %rax,%r14
    1844:	mov    %rbx,%rdi
    1847:	jmp    185b <main+0x53b>
    1849:	mov    %rax,%r14
    184c:	mov    0x10(%rsp),%rdi
    1851:	test   %rdi,%rdi
    1854:	je     1860 <main+0x540>
    1856:	mov    %rdi,0x18(%rsp)
    185b:	call   10a0 <_ZdlPv@plt>
    1860:	mov    %r14,%rdi
    1863:	call   10c0 <_Unwind_Resume@plt>
    1868:	nopl   0x0(%rax,%rax,1)
