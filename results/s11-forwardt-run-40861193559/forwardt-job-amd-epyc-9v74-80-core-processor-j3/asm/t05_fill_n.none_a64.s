0000000000001200 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
    1200:	test   %esi,%esi
    1202:	jle    12ce <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xce>
    1208:	mov    (%rdi),%rax
    120b:	mov    %esi,%ecx
    120d:	cmp    $0x8,%esi
    1210:	jae    1219 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x19>
    1212:	xor    %edx,%edx
    1214:	jmp    12ad <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xad>
    1219:	mov    %ecx,%edx
    121b:	and    $0x7ffffff8,%edx
    1221:	mov    %ecx,%esi
    1223:	shr    $0x3,%esi
    1226:	and    $0xfffffff,%esi
    122c:	shl    $0x5,%rsi
    1230:	movdqa 0xdd8(%rip),%xmm0        # 2010 <_IO_stdin_used+0x10>
    1238:	xor    %edi,%edi
    123a:	movdqa 0xdde(%rip),%xmm1        # 2020 <_IO_stdin_used+0x20>
    1242:	movdqa 0xde6(%rip),%xmm2        # 2030 <_IO_stdin_used+0x30>
    124a:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1259:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1268:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1277:	nopw   0x0(%rax,%rax,1)
    1280:	movdqa %xmm0,%xmm3
    1284:	paddd  %xmm0,%xmm3
    1288:	paddd  %xmm0,%xmm3
    128c:	movdqu %xmm3,(%rax,%rdi,1)
    1291:	paddd  %xmm1,%xmm3
    1295:	movdqu %xmm3,0x10(%rax,%rdi,1)
    129b:	paddd  %xmm2,%xmm0
    129f:	add    $0x20,%rdi
    12a3:	cmp    %rdi,%rsi
    12a6:	jne    1280 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>
    12a8:	cmp    %rcx,%rdx
    12ab:	je     12ce <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xce>
    12ad:	lea    (%rdx,%rdx,2),%esi
    12b0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12bf:	nop
    12c0:	mov    %esi,(%rax,%rdx,4)
    12c3:	inc    %rdx
    12c6:	add    $0x3,%esi
    12c9:	cmp    %rdx,%rcx
    12cc:	jne    12c0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xc0>
    12ce:	ret
    12cf:	nop
