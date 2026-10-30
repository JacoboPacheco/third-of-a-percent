00000000000011d0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
    11d0:	test   %esi,%esi
    11d2:	jle    125e <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x8e>
    11d8:	mov    (%rdi),%rax
    11db:	mov    %esi,%ecx
    11dd:	cmp    $0x8,%esi
    11e0:	jae    11e6 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x16>
    11e2:	xor    %edx,%edx
    11e4:	jmp    124d <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x7d>
    11e6:	mov    %ecx,%edx
    11e8:	and    $0x7ffffff8,%edx
    11ee:	mov    %ecx,%esi
    11f0:	shr    $0x3,%esi
    11f3:	and    $0xfffffff,%esi
    11f9:	shl    $0x5,%rsi
    11fd:	movdqa 0xe0b(%rip),%xmm0        # 2010 <_IO_stdin_used+0x10>
    1205:	xor    %edi,%edi
    1207:	movdqa 0xe11(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    120f:	movdqa 0xe19(%rip),%xmm2        # 2030 <_IO_stdin_used+0x30>
    1217:	nopw   0x0(%rax,%rax,1)
    1220:	movdqa %xmm0,%xmm3
    1224:	paddd  %xmm0,%xmm3
    1228:	paddd  %xmm0,%xmm3
    122c:	movdqu %xmm3,(%rax,%rdi,1)
    1231:	paddd  %xmm1,%xmm3
    1235:	movdqu %xmm3,0x10(%rax,%rdi,1)
    123b:	paddd  %xmm2,%xmm0
    123f:	add    $0x20,%rdi
    1243:	cmp    %rdi,%rsi
    1246:	jne    1220 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x50>
    1248:	cmp    %rcx,%rdx
    124b:	je     125e <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x8e>
    124d:	lea    (%rdx,%rdx,2),%esi
    1250:	mov    %esi,(%rax,%rdx,4)
    1253:	inc    %rdx
    1256:	add    $0x3,%esi
    1259:	cmp    %rdx,%rcx
    125c:	jne    1250 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>
    125e:	ret
    125f:	nop
