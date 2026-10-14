0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1348 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x128>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdx),%rdx
    1237:	mov    (%rdi),%rsi
    123a:	cmp    $0x1,%rcx
    123e:	mov    %rcx,%rdi
    1241:	adc    $0x0,%rdi
    1245:	cmp    $0xc,%rcx
    1249:	jae    12e4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc4>
    124f:	xor    %r8d,%r8d
    1252:	mov    %rdi,%r10
    1255:	mov    %r8,%r9
    1258:	and    $0x3,%r10
    125c:	je     1284 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    125e:	mov    %r8,%r9
    1261:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1270:	mov    (%rdx,%r9,4),%r11d
    1274:	add    (%rax,%r9,4),%r11d
    1278:	mov    %r11d,(%rsi,%r9,4)
    127c:	inc    %r9
    127f:	dec    %r10
    1282:	jne    1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    1284:	sub    %rdi,%r8
    1287:	cmp    $0xfffffffffffffffc,%r8
    128b:	ja     1348 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x128>
    1291:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a0:	mov    (%rdx,%r9,4),%edi
    12a4:	add    (%rax,%r9,4),%edi
    12a8:	mov    %edi,(%rsi,%r9,4)
    12ac:	mov    0x4(%rdx,%r9,4),%edi
    12b1:	add    0x4(%rax,%r9,4),%edi
    12b6:	mov    %edi,0x4(%rsi,%r9,4)
    12bb:	mov    0x8(%rdx,%r9,4),%edi
    12c0:	add    0x8(%rax,%r9,4),%edi
    12c5:	mov    %edi,0x8(%rsi,%r9,4)
    12ca:	mov    0xc(%rdx,%r9,4),%edi
    12cf:	add    0xc(%rax,%r9,4),%edi
    12d4:	mov    %edi,0xc(%rsi,%r9,4)
    12d9:	add    $0x4,%r9
    12dd:	cmp    %r9,%rcx
    12e0:	jne    12a0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12e2:	jmp    1348 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x128>
    12e4:	mov    %rsi,%r9
    12e7:	sub    %rax,%r9
    12ea:	xor    %r8d,%r8d
    12ed:	cmp    $0x20,%r9
    12f1:	jb     1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    12f7:	mov    %rsi,%r9
    12fa:	sub    %rdx,%r9
    12fd:	cmp    $0x20,%r9
    1301:	jb     1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1307:	mov    %rdi,%r8
    130a:	and    $0xfffffffffffffffc,%r8
    130e:	xor    %r9d,%r9d
    1311:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1320:	movdqu (%rax,%r9,4),%xmm0
    1326:	movdqu (%rdx,%r9,4),%xmm1
    132c:	paddd  %xmm0,%xmm1
    1330:	movdqu %xmm1,(%rsi,%r9,4)
    1336:	add    $0x4,%r9
    133a:	cmp    %r9,%r8
    133d:	jne    1320 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    133f:	cmp    %r8,%rdi
    1342:	jne    1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1348:	ret
    1349:	nopl   0x0(%rax)
    1610:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1615:	lea    0x38(%rsp),%rsi
    161a:	mov    $0x1,%edi
    161f:	call   1070 <clock_gettime@plt>
    1624:	mov    0x38(%rsp),%rax
    1629:	mov    %rax,0x50(%rsp)
    162e:	mov    0x40(%rsp),%rax
    1633:	mov    %rax,0x48(%rsp)
    1638:	mov    %r15,0x8(%rsp)
    163d:	test   %r15,%r15
    1640:	jle    1673 <main+0x323>
    1642:	lea    0x68(%rsp),%r15
    1647:	lea    0x10(%rsp),%r12
    164c:	lea    0x80(%rsp),%rbx
    1654:	mov    0x8(%rsp),%r14
    1659:	nopl   0x0(%rax)
    1660:	mov    %r15,%rdi
    1663:	mov    %r12,%rsi
    1666:	mov    %rbx,%rdx
    1669:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    166e:	dec    %r14
    1671:	jne    1660 <main+0x310>
    1673:	movabs $0x14650fb0739d0383,%rbx
    167d:	lea    0x38(%rsp),%rsi
    1682:	mov    $0x1,%edi
    1687:	call   1070 <clock_gettime@plt>
    168c:	mov    0x38(%rsp),%r11
    1691:	mov    0x40(%rsp),%rax
    1696:	mov    0x58(%rsp),%rdx
    169b:	test   %rdx,%rdx
    169e:	je     16cb <main+0x37b>
    16a0:	movabs $0x100000001b3,%r10
    16aa:	mov    %ebp,%esi
    16ac:	and    $0x7,%esi
    16af:	cmp    $0x1c,%r13
    16b3:	mov    0x8(%rsp),%rcx
    16b8:	mov    0x30(%rsp),%r14
    16bd:	jae    16e1 <main+0x391>
    16bf:	mov    (%rsp),%r15
    16c3:	mov    %r15,%rdi
    16c6:	jmp    1764 <main+0x414>
    16cb:	mov    %rbx,%r8
    16ce:	mov    0x8(%rsp),%rcx
    16d3:	mov    0x30(%rsp),%r14
    16d8:	mov    (%rsp),%r15
    16dc:	jmp    1786 <main+0x436>
    16e1:	movabs $0x7ffffffffffffffc,%rdi
    16eb:	add    $0xfffffffffffffffc,%rdi
    16ef:	and    %rdi,%rbp
    16f2:	mov    (%rsp),%rdi
    16f6:	cs nopw 0x0(%rax,%rax,1)
    1700:	mov    (%rdi),%r8d
    1703:	mov    0x4(%rdi),%r9d
    1707:	xor    %rbx,%r8
    170a:	imul   %r10,%r8
    170e:	xor    %r8,%r9
    1711:	imul   %r10,%r9
    1715:	mov    0x8(%rdi),%r8d
    1719:	xor    %r9,%r8
    171c:	imul   %r10,%r8
    1720:	mov    0xc(%rdi),%r9d
    1724:	xor    %r8,%r9
    1727:	imul   %r10,%r9
    172b:	mov    0x10(%rdi),%r8d
    172f:	xor    %r9,%r8
    1732:	imul   %r10,%r8
    1736:	mov    0x14(%rdi),%r9d
    173a:	xor    %r8,%r9
    173d:	imul   %r10,%r9
    1741:	mov    0x18(%rdi),%r8d
    1745:	xor    %r9,%r8
    1748:	imul   %r10,%r8
    174c:	mov    0x1c(%rdi),%ebx
    174f:	xor    %r8,%rbx
    1752:	imul   %r10,%rbx
    1756:	add    $0x20,%rdi
    175a:	add    $0xfffffffffffffff8,%rbp
    175e:	jne    1700 <main+0x3b0>
    1760:	mov    (%rsp),%r15
    1764:	mov    %rbx,%r8
    1767:	test   %rsi,%rsi
    176a:	je     1786 <main+0x436>
    176c:	xor    %r9d,%r9d
    176f:	nop
    1770:	mov    (%rdi,%r9,4),%r8d
    1774:	xor    %rbx,%r8
    1777:	imul   %r10,%r8
    177b:	inc    %r9
    177e:	mov    %r8,%rbx
    1781:	cmp    %r9,%rsi
    1784:	jne    1770 <main+0x420>
    1786:	sub    0x48(%rsp),%rax
    178b:	sub    0x50(%rsp),%r11
    1790:	imul   $0x3b9aca00,%r11,%rsi
    1797:	add    %rax,%rsi
    179a:	movq   %rsi,%xmm1
    179f:	punpckldq 0x869(%rip),%xmm1        # 2010 <_IO_stdin_used+0x10>
    17a7:	subpd  0x871(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    17af:	movapd %xmm1,%xmm0
    17b3:	unpckhpd %xmm1,%xmm0
    17b7:	addsd  %xmm1,%xmm0
    17bb:	xorps  %xmm1,%xmm1
    17be:	cvtsi2sd %rcx,%xmm1
    17c3:	divsd  %xmm1,%xmm0
    17c7:	lea    0x88f(%rip),%rdi        # 205d <_IO_stdin_used+0x5d>
    17ce:	mov    $0x2,%esi
    17d3:	mov    $0x1,%al
    17d5:	call   1030 <printf@plt>
    17da:	mov    %r15,%rdi
    17dd:	call   10a0 <_ZdlPv@plt>
    17e2:	mov    %r14,%rdi
    17e5:	call   10a0 <_ZdlPv@plt>
    17ea:	mov    0x60(%rsp),%rdi
    17ef:	call   10a0 <_ZdlPv@plt>
    17f4:	xor    %eax,%eax
    17f6:	add    $0x98,%rsp
    17fd:	pop    %rbx
    17fe:	pop    %r12
    1800:	pop    %r13
    1802:	pop    %r14
    1804:	pop    %r15
    1806:	pop    %rbp
    1807:	ret
    1808:	mov    0x27c9(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    180f:	mov    (%rax),%rdi
    1812:	mov    (%rbx),%rdx
    1815:	lea    0x814(%rip),%rsi        # 2030 <_IO_stdin_used+0x30>
    181c:	xor    %eax,%eax
    181e:	call   1110 <fprintf@plt>
    1823:	mov    $0x2,%edi
    1828:	call   1090 <exit@plt>
    182d:	mov    0x27a4(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    1834:	mov    (%rax),%rcx
    1837:	lea    0x809(%rip),%rdi        # 2047 <_IO_stdin_used+0x47>
    183e:	mov    $0xe,%esi
    1843:	mov    $0x1,%edx
    1848:	call   1100 <fwrite@plt>
    184d:	mov    $0x2,%edi
    1852:	call   1090 <exit@plt>
    1857:	lea    0x10(%rsp),%rdi
    185c:	call   18a0 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8ne180100Ev>
    1861:	mov    %rax,%r14
    1864:	mov    %r12,%rdi
    1867:	call   10a0 <_ZdlPv@plt>
    186c:	mov    %rbx,%rdi
    186f:	jmp    188b <main+0x53b>
    1871:	mov    %rax,%r14
    1874:	mov    %rbx,%rdi
    1877:	jmp    188b <main+0x53b>
    1879:	mov    %rax,%r14
    187c:	mov    0x10(%rsp),%rdi
    1881:	test   %rdi,%rdi
    1884:	je     1890 <main+0x540>
    1886:	mov    %rdi,0x18(%rsp)
    188b:	call   10a0 <_ZdlPv@plt>
    1890:	mov    %r14,%rdi
    1893:	call   10c0 <_Unwind_Resume@plt>
    1898:	nopl   0x0(%rax,%rax,1)
