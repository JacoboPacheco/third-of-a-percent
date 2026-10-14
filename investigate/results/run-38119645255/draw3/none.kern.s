0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1361 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
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
    128b:	ja     1361 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
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
    12e2:	jmp    1361 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x141>
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
    130a:	and    $0xfffffffffffffff8,%r8
    130e:	xor    %r9d,%r9d
    1311:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1320:	movdqu (%rax,%r9,4),%xmm0
    1326:	movdqu 0x10(%rax,%r9,4),%xmm1
    132d:	movdqu (%rdx,%r9,4),%xmm2
    1333:	paddd  %xmm0,%xmm2
    1337:	movdqu 0x10(%rdx,%r9,4),%xmm0
    133e:	paddd  %xmm1,%xmm0
    1342:	movdqu %xmm2,(%rsi,%r9,4)
    1348:	movdqu %xmm0,0x10(%rsi,%r9,4)
    134f:	add    $0x8,%r9
    1353:	cmp    %r9,%r8
    1356:	jne    1320 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1358:	cmp    %r8,%rdi
    135b:	jne    1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1361:	ret
    1362:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1630:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1635:	lea    0x38(%rsp),%rsi
    163a:	mov    $0x1,%edi
    163f:	call   1070 <clock_gettime@plt>
    1644:	mov    0x38(%rsp),%rax
    1649:	mov    %rax,0x50(%rsp)
    164e:	mov    0x40(%rsp),%rax
    1653:	mov    %rax,0x48(%rsp)
    1658:	mov    %r15,0x8(%rsp)
    165d:	test   %r15,%r15
    1660:	jle    1693 <main+0x323>
    1662:	lea    0x68(%rsp),%r15
    1667:	lea    0x10(%rsp),%r12
    166c:	lea    0x80(%rsp),%rbx
    1674:	mov    0x8(%rsp),%r14
    1679:	nopl   0x0(%rax)
    1680:	mov    %r15,%rdi
    1683:	mov    %r12,%rsi
    1686:	mov    %rbx,%rdx
    1689:	call   1220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    168e:	dec    %r14
    1691:	jne    1680 <main+0x310>
    1693:	movabs $0x14650fb0739d0383,%rbx
    169d:	lea    0x38(%rsp),%rsi
    16a2:	mov    $0x1,%edi
    16a7:	call   1070 <clock_gettime@plt>
    16ac:	mov    0x38(%rsp),%r11
    16b1:	mov    0x40(%rsp),%rax
    16b6:	mov    0x58(%rsp),%rdx
    16bb:	test   %rdx,%rdx
    16be:	je     16eb <main+0x37b>
    16c0:	movabs $0x100000001b3,%r10
    16ca:	mov    %ebp,%esi
    16cc:	and    $0x7,%esi
    16cf:	cmp    $0x1c,%r13
    16d3:	mov    0x8(%rsp),%rcx
    16d8:	mov    0x30(%rsp),%r14
    16dd:	jae    1701 <main+0x391>
    16df:	mov    (%rsp),%r15
    16e3:	mov    %r15,%rdi
    16e6:	jmp    1784 <main+0x414>
    16eb:	mov    %rbx,%r8
    16ee:	mov    0x8(%rsp),%rcx
    16f3:	mov    0x30(%rsp),%r14
    16f8:	mov    (%rsp),%r15
    16fc:	jmp    17a6 <main+0x436>
    1701:	movabs $0x7ffffffffffffffc,%rdi
    170b:	add    $0xfffffffffffffffc,%rdi
    170f:	and    %rdi,%rbp
    1712:	mov    (%rsp),%rdi
    1716:	cs nopw 0x0(%rax,%rax,1)
    1720:	mov    (%rdi),%r8d
    1723:	mov    0x4(%rdi),%r9d
    1727:	xor    %rbx,%r8
    172a:	imul   %r10,%r8
    172e:	xor    %r8,%r9
    1731:	imul   %r10,%r9
    1735:	mov    0x8(%rdi),%r8d
    1739:	xor    %r9,%r8
    173c:	imul   %r10,%r8
    1740:	mov    0xc(%rdi),%r9d
    1744:	xor    %r8,%r9
    1747:	imul   %r10,%r9
    174b:	mov    0x10(%rdi),%r8d
    174f:	xor    %r9,%r8
    1752:	imul   %r10,%r8
    1756:	mov    0x14(%rdi),%r9d
    175a:	xor    %r8,%r9
    175d:	imul   %r10,%r9
    1761:	mov    0x18(%rdi),%r8d
    1765:	xor    %r9,%r8
    1768:	imul   %r10,%r8
    176c:	mov    0x1c(%rdi),%ebx
    176f:	xor    %r8,%rbx
    1772:	imul   %r10,%rbx
    1776:	add    $0x20,%rdi
    177a:	add    $0xfffffffffffffff8,%rbp
    177e:	jne    1720 <main+0x3b0>
    1780:	mov    (%rsp),%r15
    1784:	mov    %rbx,%r8
    1787:	test   %rsi,%rsi
    178a:	je     17a6 <main+0x436>
    178c:	xor    %r9d,%r9d
    178f:	nop
    1790:	mov    (%rdi,%r9,4),%r8d
    1794:	xor    %rbx,%r8
    1797:	imul   %r10,%r8
    179b:	inc    %r9
    179e:	mov    %r8,%rbx
    17a1:	cmp    %r9,%rsi
    17a4:	jne    1790 <main+0x420>
    17a6:	sub    0x48(%rsp),%rax
    17ab:	sub    0x50(%rsp),%r11
    17b0:	imul   $0x3b9aca00,%r11,%rsi
    17b7:	add    %rax,%rsi
    17ba:	movq   %rsi,%xmm1
    17bf:	punpckldq 0x849(%rip),%xmm1        # 2010 <_IO_stdin_used+0x10>
    17c7:	subpd  0x851(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    17cf:	movapd %xmm1,%xmm0
    17d3:	unpckhpd %xmm1,%xmm0
    17d7:	addsd  %xmm1,%xmm0
    17db:	xorps  %xmm1,%xmm1
    17de:	cvtsi2sd %rcx,%xmm1
    17e3:	divsd  %xmm1,%xmm0
    17e7:	lea    0x86f(%rip),%rdi        # 205d <_IO_stdin_used+0x5d>
    17ee:	mov    $0x2,%esi
    17f3:	mov    $0x1,%al
    17f5:	call   1030 <printf@plt>
    17fa:	mov    %r15,%rdi
    17fd:	call   10a0 <_ZdlPv@plt>
    1802:	mov    %r14,%rdi
    1805:	call   10a0 <_ZdlPv@plt>
    180a:	mov    0x60(%rsp),%rdi
    180f:	call   10a0 <_ZdlPv@plt>
    1814:	xor    %eax,%eax
    1816:	add    $0x98,%rsp
    181d:	pop    %rbx
    181e:	pop    %r12
    1820:	pop    %r13
    1822:	pop    %r14
    1824:	pop    %r15
    1826:	pop    %rbp
    1827:	ret
    1828:	mov    0x27a9(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    182f:	mov    (%rax),%rdi
    1832:	mov    (%rbx),%rdx
    1835:	lea    0x7f4(%rip),%rsi        # 2030 <_IO_stdin_used+0x30>
    183c:	xor    %eax,%eax
    183e:	call   1110 <fprintf@plt>
    1843:	mov    $0x2,%edi
    1848:	call   1090 <exit@plt>
    184d:	mov    0x2784(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    1854:	mov    (%rax),%rcx
    1857:	lea    0x7e9(%rip),%rdi        # 2047 <_IO_stdin_used+0x47>
    185e:	mov    $0xe,%esi
    1863:	mov    $0x1,%edx
    1868:	call   1100 <fwrite@plt>
    186d:	mov    $0x2,%edi
    1872:	call   1090 <exit@plt>
    1877:	lea    0x10(%rsp),%rdi
    187c:	call   18c0 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8ne180100Ev>
    1881:	mov    %rax,%r14
    1884:	mov    %r12,%rdi
    1887:	call   10a0 <_ZdlPv@plt>
    188c:	mov    %rbx,%rdi
    188f:	jmp    18ab <main+0x53b>
    1891:	mov    %rax,%r14
    1894:	mov    %rbx,%rdi
    1897:	jmp    18ab <main+0x53b>
    1899:	mov    %rax,%r14
    189c:	mov    0x10(%rsp),%rdi
    18a1:	test   %rdi,%rdi
    18a4:	je     18b0 <main+0x540>
    18a6:	mov    %rdi,0x18(%rsp)
    18ab:	call   10a0 <_ZdlPv@plt>
    18b0:	mov    %r14,%rdi
    18b3:	call   10c0 <_Unwind_Resume@plt>
    18b8:	nopl   0x0(%rax,%rax,1)
