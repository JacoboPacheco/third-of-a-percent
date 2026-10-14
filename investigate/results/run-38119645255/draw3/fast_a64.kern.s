0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%r8
    1243:	mov    0x8(%rsi),%rax
    1247:	sub    %r8,%rax
    124a:	je     135e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11e>
    1250:	sar    $0x2,%rax
    1254:	mov    (%rdx),%rsi
    1257:	mov    0x8(%rdx),%rcx
    125b:	sub    %rsi,%rcx
    125e:	sar    $0x2,%rcx
    1262:	mov    (%rdi),%r9
    1265:	mov    0x8(%rdi),%rdx
    1269:	sub    %r9,%rdx
    126c:	sar    $0x2,%rdx
    1270:	cmp    $0x1,%rax
    1274:	adc    $0x0,%rax
    1278:	lea    -0x1(%rax),%r10
    127c:	cmp    %rdx,%r10
    127f:	cmovae %rdx,%r10
    1283:	cmp    %rcx,%r10
    1286:	cmovae %rcx,%r10
    128a:	cmp    $0x7,%r10
    128e:	ja     1297 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x57>
    1290:	xor    %edi,%edi
    1292:	jmp    131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    1297:	mov    %r9,%r11
    129a:	sub    %r8,%r11
    129d:	xor    %edi,%edi
    129f:	cmp    $0x10,%r11
    12a3:	jb     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12a9:	mov    %r9,%r11
    12ac:	sub    %rsi,%r11
    12af:	cmp    $0x10,%r11
    12b3:	jb     131f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdf>
    12b5:	inc    %r10
    12b8:	mov    %r10d,%edi
    12bb:	and    $0x3,%edi
    12be:	mov    $0x4,%r11d
    12c4:	cmovne %rdi,%r11
    12c8:	mov    %r10,%rdi
    12cb:	sub    %r11,%rdi
    12ce:	xor    %r10d,%r10d
    12d1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ef:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fe:	xchg   %ax,%ax
    1300:	movdqu (%r8,%r10,4),%xmm0
    1306:	movdqu (%rsi,%r10,4),%xmm1
    130c:	paddd  %xmm0,%xmm1
    1310:	movdqu %xmm1,(%r9,%r10,4)
    1316:	add    $0x4,%r10
    131a:	cmp    %r10,%rdi
    131d:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    131f:	sub    %rdi,%rdx
    1322:	sub    %rdi,%rcx
    1325:	sub    %rdi,%rax
    1328:	lea    (%r8,%rdi,4),%r8
    132c:	lea    (%rsi,%rdi,4),%rsi
    1330:	lea    (%r9,%rdi,4),%rdi
    1334:	xor    %r9d,%r9d
    1337:	nopw   0x0(%rax,%rax,1)
    1340:	cmp    %r9,%rcx
    1343:	je     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11f>
    1345:	cmp    %r9,%rdx
    1348:	je     135f <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x11f>
    134a:	mov    (%rsi,%r9,4),%r10d
    134e:	add    (%r8,%r9,4),%r10d
    1352:	mov    %r10d,(%rdi,%r9,4)
    1356:	inc    %r9
    1359:	cmp    %r9,%rax
    135c:	jne    1340 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    135e:	ret
    135f:	ud2
    1361:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    16c0:	call   1240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    16c5:	lea    0x38(%rsp),%rsi
    16ca:	mov    $0x1,%edi
    16cf:	call   1070 <clock_gettime@plt>
    16d4:	mov    0x38(%rsp),%rax
    16d9:	mov    %rax,0x50(%rsp)
    16de:	mov    0x40(%rsp),%rax
    16e3:	mov    %rax,0x48(%rsp)
    16e8:	mov    %r15,0x8(%rsp)
    16ed:	test   %r15,%r15
    16f0:	jle    1753 <main+0x3e3>
    16f2:	lea    0x68(%rsp),%r15
    16f7:	lea    0x10(%rsp),%r12
    16fc:	lea    0x80(%rsp),%rbx
    1704:	mov    0x8(%rsp),%r14
    1709:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1718:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1727:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1736:	cs nopw 0x0(%rax,%rax,1)
    1740:	mov    %r15,%rdi
    1743:	mov    %r12,%rsi
    1746:	mov    %rbx,%rdx
    1749:	call   1240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>
    174e:	dec    %r14
    1751:	jne    1740 <main+0x3d0>
    1753:	movabs $0x14650fb0739d0383,%rbx
    175d:	lea    0x38(%rsp),%rsi
    1762:	mov    $0x1,%edi
    1767:	call   1070 <clock_gettime@plt>
    176c:	mov    0x38(%rsp),%r11
    1771:	mov    0x40(%rsp),%rax
    1776:	mov    0x58(%rsp),%rdx
    177b:	test   %rdx,%rdx
    177e:	je     17ab <main+0x43b>
    1780:	movabs $0x100000001b3,%r10
    178a:	mov    %ebp,%esi
    178c:	and    $0x7,%esi
    178f:	cmp    $0x1c,%r13
    1793:	mov    0x8(%rsp),%rcx
    1798:	mov    0x30(%rsp),%r14
    179d:	jae    17c1 <main+0x451>
    179f:	mov    (%rsp),%r15
    17a3:	mov    %r15,%rdi
    17a6:	jmp    1864 <main+0x4f4>
    17ab:	mov    %rbx,%r8
    17ae:	mov    0x8(%rsp),%rcx
    17b3:	mov    0x30(%rsp),%r14
    17b8:	mov    (%rsp),%r15
    17bc:	jmp    1896 <main+0x526>
    17c1:	movabs $0x7ffffffffffffffc,%rdi
    17cb:	add    $0xfffffffffffffffc,%rdi
    17cf:	and    %rdi,%rbp
    17d2:	mov    (%rsp),%rdi
    17d6:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    17e5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    17f4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1800:	mov    (%rdi),%r8d
    1803:	mov    0x4(%rdi),%r9d
    1807:	xor    %rbx,%r8
    180a:	imul   %r10,%r8
    180e:	xor    %r8,%r9
    1811:	imul   %r10,%r9
    1815:	mov    0x8(%rdi),%r8d
    1819:	xor    %r9,%r8
    181c:	imul   %r10,%r8
    1820:	mov    0xc(%rdi),%r9d
    1824:	xor    %r8,%r9
    1827:	imul   %r10,%r9
    182b:	mov    0x10(%rdi),%r8d
    182f:	xor    %r9,%r8
    1832:	imul   %r10,%r8
    1836:	mov    0x14(%rdi),%r9d
    183a:	xor    %r8,%r9
    183d:	imul   %r10,%r9
    1841:	mov    0x18(%rdi),%r8d
    1845:	xor    %r9,%r8
    1848:	imul   %r10,%r8
    184c:	mov    0x1c(%rdi),%ebx
    184f:	xor    %r8,%rbx
    1852:	imul   %r10,%rbx
    1856:	add    $0x20,%rdi
    185a:	add    $0xfffffffffffffff8,%rbp
    185e:	jne    1800 <main+0x490>
    1860:	mov    (%rsp),%r15
    1864:	mov    %rbx,%r8
    1867:	test   %rsi,%rsi
    186a:	je     1896 <main+0x526>
    186c:	xor    %r9d,%r9d
    186f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    187e:	xchg   %ax,%ax
    1880:	mov    (%rdi,%r9,4),%r8d
    1884:	xor    %rbx,%r8
    1887:	imul   %r10,%r8
    188b:	inc    %r9
    188e:	mov    %r8,%rbx
    1891:	cmp    %r9,%rsi
    1894:	jne    1880 <main+0x510>
    1896:	sub    0x48(%rsp),%rax
    189b:	sub    0x50(%rsp),%r11
    18a0:	imul   $0x3b9aca00,%r11,%rsi
    18a7:	add    %rax,%rsi
    18aa:	movq   %rsi,%xmm1
    18af:	punpckldq 0x759(%rip),%xmm1        # 2010 <_IO_stdin_used+0x10>
    18b7:	subpd  0x761(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    18bf:	movapd %xmm1,%xmm0
    18c3:	unpckhpd %xmm1,%xmm0
    18c7:	addsd  %xmm1,%xmm0
    18cb:	xorps  %xmm1,%xmm1
    18ce:	cvtsi2sd %rcx,%xmm1
    18d3:	divsd  %xmm1,%xmm0
    18d7:	lea    0x77f(%rip),%rdi        # 205d <_IO_stdin_used+0x5d>
    18de:	mov    $0x4,%esi
    18e3:	mov    $0x1,%al
    18e5:	call   1030 <printf@plt>
    18ea:	mov    %r15,%rdi
    18ed:	call   10a0 <_ZdlPv@plt>
    18f2:	mov    %r14,%rdi
    18f5:	call   10a0 <_ZdlPv@plt>
    18fa:	mov    0x60(%rsp),%rdi
    18ff:	call   10a0 <_ZdlPv@plt>
    1904:	xor    %eax,%eax
    1906:	add    $0x98,%rsp
    190d:	pop    %rbx
    190e:	pop    %r12
    1910:	pop    %r13
    1912:	pop    %r14
    1914:	pop    %r15
    1916:	pop    %rbp
    1917:	ret
    1918:	mov    0x26b9(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    191f:	mov    (%rax),%rdi
    1922:	mov    (%rbx),%rdx
    1925:	lea    0x704(%rip),%rsi        # 2030 <_IO_stdin_used+0x30>
    192c:	xor    %eax,%eax
    192e:	call   1110 <fprintf@plt>
    1933:	mov    $0x2,%edi
    1938:	call   1090 <exit@plt>
    193d:	mov    0x2694(%rip),%rax        # 3fd8 <stderr@GLIBC_2.2.5>
    1944:	mov    (%rax),%rcx
    1947:	lea    0x6f9(%rip),%rdi        # 2047 <_IO_stdin_used+0x47>
    194e:	mov    $0xe,%esi
    1953:	mov    $0x1,%edx
    1958:	call   1100 <fwrite@plt>
    195d:	mov    $0x2,%edi
    1962:	call   1090 <exit@plt>
    1967:	lea    0x10(%rsp),%rdi
    196c:	call   19b0 <_ZNKSt3__16vectorIiNS_9allocatorIiEEE20__throw_length_errorB8fe180100Ev>
    1971:	mov    %rax,%r14
    1974:	mov    %r12,%rdi
    1977:	call   10a0 <_ZdlPv@plt>
    197c:	mov    %rbx,%rdi
    197f:	jmp    199b <main+0x62b>
    1981:	mov    %rax,%r14
    1984:	mov    %rbx,%rdi
    1987:	jmp    199b <main+0x62b>
    1989:	mov    %rax,%r14
    198c:	mov    0x10(%rsp),%rdi
    1991:	test   %rdi,%rdi
    1994:	je     19a0 <main+0x630>
    1996:	mov    %rdi,0x18(%rsp)
    199b:	call   10a0 <_ZdlPv@plt>
    19a0:	mov    %r14,%rdi
    19a3:	call   10c0 <_Unwind_Resume@plt>
    19a8:	nopl   0x0(%rax,%rax,1)
