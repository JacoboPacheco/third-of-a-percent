0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%r8
    1223:	mov    0x8(%rsi),%rax
    1227:	sub    %r8,%rax
    122a:	je     131e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xfe>
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
    1272:	jmp    12e8 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc8>
    1274:	mov    %r9,%r11
    1277:	sub    %r8,%r11
    127a:	xor    %edi,%edi
    127c:	cmp    $0x20,%r11
    1280:	jb     12e8 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc8>
    1282:	mov    %r9,%r11
    1285:	sub    %rsi,%r11
    1288:	cmp    $0x20,%r11
    128c:	jb     12e8 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc8>
    128e:	inc    %r10
    1291:	mov    %r10d,%edi
    1294:	and    $0x7,%edi
    1297:	mov    $0x8,%r11d
    129d:	cmovne %rdi,%r11
    12a1:	mov    %r10,%rdi
    12a4:	sub    %r11,%rdi
    12a7:	xor    %r10d,%r10d
    12aa:	nopw   0x0(%rax,%rax,1)
    12b0:	movdqu (%r8,%r10,4),%xmm0
    12b6:	movdqu 0x10(%r8,%r10,4),%xmm1
    12bd:	movdqu (%rsi,%r10,4),%xmm2
    12c3:	paddd  %xmm0,%xmm2
    12c7:	movdqu 0x10(%rsi,%r10,4),%xmm0
    12ce:	paddd  %xmm1,%xmm0
    12d2:	movdqu %xmm2,(%r9,%r10,4)
    12d8:	movdqu %xmm0,0x10(%r9,%r10,4)
    12df:	add    $0x8,%r10
    12e3:	cmp    %r10,%rdi
    12e6:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12e8:	sub    %rdi,%rdx
    12eb:	sub    %rdi,%rcx
    12ee:	sub    %rdi,%rax
    12f1:	lea    (%r8,%rdi,4),%r8
    12f5:	lea    (%rsi,%rdi,4),%rsi
    12f9:	lea    (%r9,%rdi,4),%rdi
    12fd:	xor    %r9d,%r9d
    1300:	cmp    %r9,%rcx
    1303:	je     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xff>
    1305:	cmp    %r9,%rdx
    1308:	je     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xff>
    130a:	mov    (%rsi,%r9,4),%r10d
    130e:	add    (%r8,%r9,4),%r10d
    1312:	mov    %r10d,(%rdi,%r9,4)
    1316:	inc    %r9
    1319:	cmp    %r9,%rax
    131c:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe0>
    131e:	ret
    131f:	ud2
    1321:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    15f0:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    15f5:	lea    0x38(%rsp),%rsi
    15fa:	mov    $0x1,%edi
    15ff:	call   1070 <clock_gettime@plt>
    1604:	mov    0x38(%rsp),%rax
    1609:	mov    %rax,0x50(%rsp)
    160e:	mov    0x40(%rsp),%rax
    1613:	mov    %rax,0x48(%rsp)
    1618:	mov    %r15,0x8(%rsp)
    161d:	test   %r15,%r15
    1620:	jle    1653 <main+0x323>
    1622:	lea    0x68(%rsp),%r15
    1627:	lea    0x10(%rsp),%r12
    162c:	lea    0x80(%rsp),%rbx
    1634:	mov    0x8(%rsp),%r14
    1639:	nopl   0x0(%rax)
    1640:	mov    %r15,%rdi
    1643:	mov    %r12,%rsi
    1646:	mov    %rbx,%rdx
    1649:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    164e:	dec    %r14
    1651:	jne    1640 <main+0x310>
    1653:	movabs $0x14650fb0739d0383,%rbx
    165d:	lea    0x38(%rsp),%rsi
    1662:	mov    $0x1,%edi
    1667:	call   1070 <clock_gettime@plt>
    166c:	mov    0x38(%rsp),%r11
    1671:	mov    0x40(%rsp),%rax
    1676:	mov    0x58(%rsp),%rdx
    167b:	test   %rdx,%rdx
    167e:	je     16ab <main+0x37b>
    1680:	movabs $0x100000001b3,%r10
    168a:	mov    %ebp,%esi
    168c:	and    $0x7,%esi
    168f:	cmp    $0x1c,%r13
    1693:	mov    0x8(%rsp),%rcx
    1698:	mov    0x30(%rsp),%r14
    169d:	jae    16c1 <main+0x391>
    169f:	mov    (%rsp),%r15
    16a3:	mov    %r15,%rdi
    16a6:	jmp    1744 <main+0x414>
    16ab:	mov    %rbx,%r8
    16ae:	mov    0x8(%rsp),%rcx
    16b3:	mov    0x30(%rsp),%r14
    16b8:	mov    (%rsp),%r15
    16bc:	jmp    1766 <main+0x436>
    16c1:	movabs $0x7ffffffffffffffc,%rdi
    16cb:	add    $0xfffffffffffffffc,%rdi
    16cf:	and    %rdi,%rbp
    16d2:	mov    (%rsp),%rdi
    16d6:	cs nopw 0x0(%rax,%rax,1)
    16e0:	mov    (%rdi),%r8d
    16e3:	mov    0x4(%rdi),%r9d
    16e7:	xor    %rbx,%r8
    16ea:	imul   %r10,%r8
    16ee:	xor    %r8,%r9
    16f1:	imul   %r10,%r9
    16f5:	mov    0x8(%rdi),%r8d
    16f9:	xor    %r9,%r8
    16fc:	imul   %r10,%r8
    1700:	mov    0xc(%rdi),%r9d
    1704:	xor    %r8,%r9
    1707:	imul   %r10,%r9
    170b:	mov    0x10(%rdi),%r8d
    170f:	xor    %r9,%r8
    1712:	imul   %r10,%r8
    1716:	mov    0x14(%rdi),%r9d
    171a:	xor    %r8,%r9
    171d:	imul   %r10,%r9
    1721:	mov    0x18(%rdi),%r8d
    1725:	xor    %r9,%r8
    1728:	imul   %r10,%r8
    172c:	mov    0x1c(%rdi),%ebx
    172f:	xor    %r8,%rbx
    1732:	imul   %r10,%rbx
    1736:	add    $0x20,%rdi
    173a:	add    $0xfffffffffffffff8,%rbp
    173e:	jne    16e0 <main+0x3b0>
    1740:	mov    (%rsp),%r15
    1744:	mov    %rbx,%r8
    1747:	test   %rsi,%rsi
    174a:	je     1766 <main+0x436>
    174c:	xor    %r9d,%r9d
    174f:	nop
    1750:	mov    (%rdi,%r9,4),%r8d
    1754:	xor    %rbx,%r8
    1757:	imul   %r10,%r8
    175b:	inc    %r9
    175e:	mov    %r8,%rbx
    1761:	cmp    %r9,%rsi
    1764:	jne    1750 <main+0x420>
    1766:	sub    0x48(%rsp),%rax
    176b:	sub    0x50(%rsp),%r11
    1770:	imul   $0x3b9aca00,%r11,%rsi
    1777:	add    %rax,%rsi
    177a:	movq   %rsi,%xmm1
    177f:	punpckldq 0x889(%rip),%xmm1        # 2010 <_IO_stdin_used+0x10>
    1787:	subpd  0x891(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    178f:	movapd %xmm1,%xmm0
    1793:	unpckhpd %xmm1,%xmm0
    1797:	addsd  %xmm1,%xmm0
    179b:	xorps  %xmm1,%xmm1
    179e:	cvtsi2sd %rcx,%xmm1
    17a3:	divsd  %xmm1,%xmm0
    17a7:	lea    0x8af(%rip),%rdi        # 205d <_IO_stdin_used+0x5d>
    17ae:	mov    $0x4,%esi
    17b3:	mov    $0x1,%al
    17b5:	call   1030 <printf@plt>
    17ba:	mov    %r15,%rdi
    17bd:	call   10a0 <_ZdlPv@plt>
    17c2:	mov    %r14,%rdi
    17c5:	call   10a0 <_ZdlPv@plt>
    17ca:	mov    0x60(%rsp),%rdi
    17cf:	call   10a0 <_ZdlPv@plt>
    17d4:	xor    %eax,%eax
    17d6:	add    $0x98,%rsp
    17dd:	pop    %rbx
    17de:	pop    %r12
    17e0:	pop    %r13
    17e2:	pop    %r14
    17e4:	pop    %r15
    17e6:	pop    %rbp
    17e7:	ret
    17e8:	mov    0x27e9(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    17ef:	mov    (%rax),%rdi
    17f2:	mov    (%rbx),%rdx
    17f5:	lea    0x834(%rip),%rsi        # 2030 <_IO_stdin_used+0x30>
    17fc:	xor    %eax,%eax
    17fe:	call   1110 <fprintf@plt>
    1803:	mov    $0x2,%edi
    1808:	call   1090 <exit@plt>
    180d:	mov    0x27c4(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    1814:	mov    (%rax),%rcx
    1817:	lea    0x829(%rip),%rdi        # 2047 <_IO_stdin_used+0x47>
    181e:	mov    $0xe,%esi
    1823:	mov    $0x1,%edx
    1828:	call   1100 <fwrite@plt>
    182d:	mov    $0x2,%edi
    1832:	call   1090 <exit@plt>
    1837:	lea    0x10(%rsp),%rdi
    183c:	call   1880 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8fe180100Ev>
    1841:	mov    %rax,%r14
    1844:	mov    %r12,%rdi
    1847:	call   10a0 <_ZdlPv@plt>
    184c:	mov    %rbx,%rdi
    184f:	jmp    186b <main+0x53b>
    1851:	mov    %rax,%r14
    1854:	mov    %rbx,%rdi
    1857:	jmp    186b <main+0x53b>
    1859:	mov    %rax,%r14
    185c:	mov    0x10(%rsp),%rdi
    1861:	test   %rdi,%rdi
    1864:	je     1870 <main+0x540>
    1866:	mov    %rdi,0x18(%rsp)
    186b:	call   10a0 <_ZdlPv@plt>
    1870:	mov    %r14,%rdi
    1873:	call   10c0 <_Unwind_Resume@plt>
    1878:	nopl   0x0(%rax,%rax,1)
