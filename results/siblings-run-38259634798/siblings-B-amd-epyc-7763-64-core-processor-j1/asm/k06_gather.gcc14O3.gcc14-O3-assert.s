0000000000001910 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    1910:	endbr64
    1914:	mov    0x8(%rdx),%rax
    1918:	mov    (%rdx),%r8
    191b:	mov    %rax,%r9
    191e:	sub    %r8,%r9
    1921:	sar    $0x2,%r9
    1925:	cmp    %r8,%rax
    1928:	je     19c0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    192e:	sub    $0x8,%rsp
    1932:	mov    (%rsi),%r11
    1935:	mov    0x8(%rsi),%rsi
    1939:	mov    %rdi,%rcx
    193c:	xor    %eax,%eax
    193e:	sub    %r11,%rsi
    1941:	sar    $0x2,%rsi
    1945:	movslq (%r8,%rax,4),%rdx
    1949:	cmp    %rsi,%rdx
    194c:	jae    1980 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x70>
    194e:	mov    (%r11,%rdx,4),%r10d
    1952:	mov    (%rcx),%rdi
    1955:	mov    0x8(%rcx),%rdx
    1959:	sub    %rdi,%rdx
    195c:	sar    $0x2,%rdx
    1960:	cmp    %rdx,%rax
    1963:	jae    19a0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x90>
    1965:	mov    %r10d,(%rdi,%rax,4)
    1969:	add    $0x1,%rax
    196d:	cmp    %r9,%rax
    1970:	jb     1945 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x35>
    1972:	add    $0x8,%rsp
    1976:	ret
    1977:	nopw   0x0(%rax,%rax,1)
    1980:	lea    0x67d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    1987:	lea    0x6b2(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    198e:	mov    $0x47d,%esi
    1993:	lea    0x77e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    199a:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    199f:	nop
    19a0:	lea    0x65d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    19a7:	lea    0x792(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    19ae:	mov    $0x46a,%esi
    19b3:	lea    0x75e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    19ba:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    19bf:	nop
    19c0:	ret
    19c1:	cs nopw 0x0(%rax,%rax,1)
    19cb:	nopl   0x0(%rax,%rax,1)
