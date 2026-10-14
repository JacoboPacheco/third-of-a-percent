0000000000001950 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_>:
    1950:	endbr64
    1954:	mov    0x8(%rdx),%rax
    1958:	mov    (%rdx),%r8
    195b:	mov    %rax,%r9
    195e:	sub    %r8,%r9
    1961:	sar    $0x2,%r9
    1965:	cmp    %r8,%rax
    1968:	je     1a00 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0xb0>
    196e:	sub    $0x8,%rsp
    1972:	mov    (%rsi),%r11
    1975:	mov    0x8(%rsi),%rsi
    1979:	mov    %rdi,%rcx
    197c:	xor    %eax,%eax
    197e:	sub    %r11,%rsi
    1981:	sar    $0x2,%rsi
    1985:	movslq (%r8,%rax,4),%rdx
    1989:	cmp    %rsi,%rdx
    198c:	jae    19c0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x70>
    198e:	mov    (%r11,%rdx,4),%r10d
    1992:	mov    (%rcx),%rdi
    1995:	mov    0x8(%rcx),%rdx
    1999:	sub    %rdi,%rdx
    199c:	sar    $0x2,%rdx
    19a0:	cmp    %rdx,%rax
    19a3:	jae    19e0 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x90>
    19a5:	mov    %r10d,(%rdi,%rax,4)
    19a9:	add    $0x1,%rax
    19ad:	cmp    %r9,%rax
    19b0:	jb     1985 <_Z15kern_k06_gatherRSt6vectorIiSaIiEERKS1_S4_+0x35>
    19b2:	add    $0x8,%rsp
    19b6:	ret
    19b7:	nopw   0x0(%rax,%rax,1)
    19c0:	lea    0x63d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    19c7:	lea    0x672(%rip),%rdx        # 2040 <_IO_stdin_used+0x40>
    19ce:	mov    $0x47d,%esi
    19d3:	lea    0x73e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    19da:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    19df:	nop
    19e0:	lea    0x61d(%rip),%rcx        # 2004 <_IO_stdin_used+0x4>
    19e7:	lea    0x752(%rip),%rdx        # 2140 <_IO_stdin_used+0x140>
    19ee:	mov    $0x46a,%esi
    19f3:	lea    0x71e(%rip),%rdi        # 2118 <_IO_stdin_used+0x118>
    19fa:	call   1120 <_ZSt21__glibcxx_assert_failPKciS0_S0_@plt>
    19ff:	nop
    1a00:	ret
    1a01:	cs nopw 0x0(%rax,%rax,1)
    1a0b:	nopl   0x0(%rax,%rax,1)
