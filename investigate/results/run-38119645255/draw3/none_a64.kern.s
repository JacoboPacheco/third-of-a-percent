0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdx),%rdx
    1257:	mov    (%rdi),%rsi
    125a:	cmp    $0x1,%rcx
    125e:	mov    %rcx,%rdi
    1261:	adc    $0x0,%rdi
    1265:	cmp    $0xc,%rcx
    1269:	jae    1344 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x104>
    126f:	xor    %r8d,%r8d
    1272:	mov    %rdi,%r10
    1275:	mov    %r8,%r9
    1278:	and    $0x3,%r10
    127c:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>
    127e:	mov    %r8,%r9
    1281:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1290:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    129f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ae:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bd:	nopl   (%rax)
    12c0:	mov    (%rdx,%r9,4),%r11d
    12c4:	add    (%rax,%r9,4),%r11d
    12c8:	mov    %r11d,(%rsi,%r9,4)
    12cc:	inc    %r9
    12cf:	dec    %r10
    12d2:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12d4:	sub    %rdi,%r8
    12d7:	cmp    $0xfffffffffffffffc,%r8
    12db:	ja     13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	mov    (%rdx,%r9,4),%edi
    1304:	add    (%rax,%r9,4),%edi
    1308:	mov    %edi,(%rsi,%r9,4)
    130c:	mov    0x4(%rdx,%r9,4),%edi
    1311:	add    0x4(%rax,%r9,4),%edi
    1316:	mov    %edi,0x4(%rsi,%r9,4)
    131b:	mov    0x8(%rdx,%r9,4),%edi
    1320:	add    0x8(%rax,%r9,4),%edi
    1325:	mov    %edi,0x8(%rsi,%r9,4)
    132a:	mov    0xc(%rdx,%r9,4),%edi
    132f:	add    0xc(%rax,%r9,4),%edi
    1334:	mov    %edi,0xc(%rsi,%r9,4)
    1339:	add    $0x4,%r9
    133d:	cmp    %r9,%rcx
    1340:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1342:	jmp    13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    1344:	mov    %rsi,%r9
    1347:	sub    %rax,%r9
    134a:	xor    %r8d,%r8d
    134d:	cmp    $0x20,%r9
    1351:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1357:	mov    %rsi,%r9
    135a:	sub    %rdx,%r9
    135d:	cmp    $0x20,%r9
    1361:	jb     1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1367:	mov    %rdi,%r8
    136a:	and    $0xfffffffffffffff8,%r8
    136e:	xor    %r9d,%r9d
    1371:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1380:	movdqu (%rax,%r9,4),%xmm0
    1386:	movdqu 0x10(%rax,%r9,4),%xmm1
    138d:	movdqu (%rdx,%r9,4),%xmm2
    1393:	paddd  %xmm0,%xmm2
    1397:	movdqu 0x10(%rdx,%r9,4),%xmm0
    139e:	paddd  %xmm1,%xmm0
    13a2:	movdqu %xmm2,(%rsi,%r9,4)
    13a8:	movdqu %xmm0,0x10(%rsi,%r9,4)
    13af:	add    $0x8,%r9
    13b3:	cmp    %r9,%r8
    13b6:	jne    1380 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>
    13b8:	cmp    %r8,%rdi
    13bb:	jne    1272 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    13c1:	ret
    13c2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1700:	call   1240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    1705:	lea    0x38(%rsp),%rsi
    170a:	mov    $0x1,%edi
    170f:	call   1070 <clock_gettime@plt>
    1714:	mov    0x38(%rsp),%rax
    1719:	mov    %rax,0x50(%rsp)
    171e:	mov    0x40(%rsp),%rax
    1723:	mov    %rax,0x48(%rsp)
    1728:	mov    %r15,0x8(%rsp)
    172d:	test   %r15,%r15
    1730:	jle    1793 <main+0x3c3>
    1732:	lea    0x68(%rsp),%r15
    1737:	lea    0x10(%rsp),%r12
    173c:	lea    0x80(%rsp),%rbx
    1744:	mov    0x8(%rsp),%r14
    1749:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1758:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1767:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1776:	cs nopw 0x0(%rax,%rax,1)
    1780:	mov    %r15,%rdi
    1783:	mov    %r12,%rsi
    1786:	mov    %rbx,%rdx
    1789:	call   1240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    178e:	dec    %r14
    1791:	jne    1780 <main+0x3b0>
    1793:	movabs $0x14650fb0739d0383,%rbx
    179d:	lea    0x38(%rsp),%rsi
    17a2:	mov    $0x1,%edi
    17a7:	call   1070 <clock_gettime@plt>
    17ac:	mov    0x38(%rsp),%r11
    17b1:	mov    0x40(%rsp),%rax
    17b6:	mov    0x58(%rsp),%rdx
    17bb:	test   %rdx,%rdx
    17be:	je     17eb <main+0x41b>
    17c0:	movabs $0x100000001b3,%r10
    17ca:	mov    %ebp,%esi
    17cc:	and    $0x7,%esi
    17cf:	cmp    $0x1c,%r13
    17d3:	mov    0x8(%rsp),%rcx
    17d8:	mov    0x30(%rsp),%r14
    17dd:	jae    1801 <main+0x431>
    17df:	mov    (%rsp),%r15
    17e3:	mov    %r15,%rdi
    17e6:	jmp    18a4 <main+0x4d4>
    17eb:	mov    %rbx,%r8
    17ee:	mov    0x8(%rsp),%rcx
    17f3:	mov    0x30(%rsp),%r14
    17f8:	mov    (%rsp),%r15
    17fc:	jmp    18d6 <main+0x506>
    1801:	movabs $0x7ffffffffffffffc,%rdi
    180b:	add    $0xfffffffffffffffc,%rdi
    180f:	and    %rdi,%rbp
    1812:	mov    (%rsp),%rdi
    1816:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1825:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1834:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1840:	mov    (%rdi),%r8d
    1843:	mov    0x4(%rdi),%r9d
    1847:	xor    %rbx,%r8
    184a:	imul   %r10,%r8
    184e:	xor    %r8,%r9
    1851:	imul   %r10,%r9
    1855:	mov    0x8(%rdi),%r8d
    1859:	xor    %r9,%r8
    185c:	imul   %r10,%r8
    1860:	mov    0xc(%rdi),%r9d
    1864:	xor    %r8,%r9
    1867:	imul   %r10,%r9
    186b:	mov    0x10(%rdi),%r8d
    186f:	xor    %r9,%r8
    1872:	imul   %r10,%r8
    1876:	mov    0x14(%rdi),%r9d
    187a:	xor    %r8,%r9
    187d:	imul   %r10,%r9
    1881:	mov    0x18(%rdi),%r8d
    1885:	xor    %r9,%r8
    1888:	imul   %r10,%r8
    188c:	mov    0x1c(%rdi),%ebx
    188f:	xor    %r8,%rbx
    1892:	imul   %r10,%rbx
    1896:	add    $0x20,%rdi
    189a:	add    $0xfffffffffffffff8,%rbp
    189e:	jne    1840 <main+0x470>
    18a0:	mov    (%rsp),%r15
    18a4:	mov    %rbx,%r8
    18a7:	test   %rsi,%rsi
    18aa:	je     18d6 <main+0x506>
    18ac:	xor    %r9d,%r9d
    18af:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    18be:	xchg   %ax,%ax
    18c0:	mov    (%rdi,%r9,4),%r8d
    18c4:	xor    %rbx,%r8
    18c7:	imul   %r10,%r8
    18cb:	inc    %r9
    18ce:	mov    %r8,%rbx
    18d1:	cmp    %r9,%rsi
    18d4:	jne    18c0 <main+0x4f0>
    18d6:	sub    0x48(%rsp),%rax
    18db:	sub    0x50(%rsp),%r11
    18e0:	imul   $0x3b9aca00,%r11,%rsi
    18e7:	add    %rax,%rsi
    18ea:	movq   %rsi,%xmm1
    18ef:	punpckldq 0x719(%rip),%xmm1        # 2010 <_IO_stdin_used+0x10>
    18f7:	subpd  0x721(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    18ff:	movapd %xmm1,%xmm0
    1903:	unpckhpd %xmm1,%xmm0
    1907:	addsd  %xmm1,%xmm0
    190b:	xorps  %xmm1,%xmm1
    190e:	cvtsi2sd %rcx,%xmm1
    1913:	divsd  %xmm1,%xmm0
    1917:	lea    0x73f(%rip),%rdi        # 205d <_IO_stdin_used+0x5d>
    191e:	mov    $0x2,%esi
    1923:	mov    $0x1,%al
    1925:	call   1030 <printf@plt>
    192a:	mov    %r15,%rdi
    192d:	call   10a0 <_ZdlPv@plt>
    1932:	mov    %r14,%rdi
    1935:	call   10a0 <_ZdlPv@plt>
    193a:	mov    0x60(%rsp),%rdi
    193f:	call   10a0 <_ZdlPv@plt>
    1944:	xor    %eax,%eax
    1946:	add    $0x98,%rsp
    194d:	pop    %rbx
    194e:	pop    %r12
    1950:	pop    %r13
    1952:	pop    %r14
    1954:	pop    %r15
    1956:	pop    %rbp
    1957:	ret
    1958:	mov    0x2679(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    195f:	mov    (%rax),%rdi
    1962:	mov    (%rbx),%rdx
    1965:	lea    0x6c4(%rip),%rsi        # 2030 <_IO_stdin_used+0x30>
    196c:	xor    %eax,%eax
    196e:	call   1110 <fprintf@plt>
    1973:	mov    $0x2,%edi
    1978:	call   1090 <exit@plt>
    197d:	mov    0x2654(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    1984:	mov    (%rax),%rcx
    1987:	lea    0x6b9(%rip),%rdi        # 2047 <_IO_stdin_used+0x47>
    198e:	mov    $0xe,%esi
    1993:	mov    $0x1,%edx
    1998:	call   1100 <fwrite@plt>
    199d:	mov    $0x2,%edi
    19a2:	call   1090 <exit@plt>
    19a7:	lea    0x10(%rsp),%rdi
    19ac:	call   19f0 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8ne180100Ev>
    19b1:	mov    %rax,%r14
    19b4:	mov    %r12,%rdi
    19b7:	call   10a0 <_ZdlPv@plt>
    19bc:	mov    %rbx,%rdi
    19bf:	jmp    19db <main+0x60b>
    19c1:	mov    %rax,%r14
    19c4:	mov    %rbx,%rdi
    19c7:	jmp    19db <main+0x60b>
    19c9:	mov    %rax,%r14
    19cc:	mov    0x10(%rsp),%rdi
    19d1:	test   %rdi,%rdi
    19d4:	je     19e0 <main+0x610>
    19d6:	mov    %rdi,0x18(%rsp)
    19db:	call   10a0 <_ZdlPv@plt>
    19e0:	mov    %r14,%rdi
    19e3:	call   10c0 <_Unwind_Resume@plt>
    19e8:	nopl   0x0(%rax,%rax,1)
