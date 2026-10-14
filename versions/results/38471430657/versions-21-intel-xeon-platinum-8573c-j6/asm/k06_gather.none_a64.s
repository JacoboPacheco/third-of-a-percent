0000000000001240 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%r8
    1243:	mov    0x8(%rdx),%r9
    1247:	sub    %r8,%r9
    124a:	je     1314 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd4>
    1250:	sar    $0x2,%r9
    1254:	mov    (%rsi),%rax
    1257:	mov    (%rdi),%rdx
    125a:	mov    %r9d,%ecx
    125d:	and    $0x3,%ecx
    1260:	cmp    $0x4,%r9
    1264:	jae    126a <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2a>
    1266:	xor    %esi,%esi
    1268:	jmp    12b7 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x77>
    126a:	and    $0xfffffffffffffffc,%r9
    126e:	xor    %esi,%esi
    1270:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127f:	nop
    1280:	movslq (%r8,%rsi,4),%rdi
    1284:	mov    (%rax,%rdi,4),%edi
    1287:	mov    %edi,(%rdx,%rsi,4)
    128a:	movslq 0x4(%r8,%rsi,4),%rdi
    128f:	mov    (%rax,%rdi,4),%edi
    1292:	mov    %edi,0x4(%rdx,%rsi,4)
    1296:	movslq 0x8(%r8,%rsi,4),%rdi
    129b:	mov    (%rax,%rdi,4),%edi
    129e:	mov    %edi,0x8(%rdx,%rsi,4)
    12a2:	movslq 0xc(%r8,%rsi,4),%rdi
    12a7:	mov    (%rax,%rdi,4),%edi
    12aa:	mov    %edi,0xc(%rdx,%rsi,4)
    12ae:	add    $0x4,%rsi
    12b2:	cmp    %rsi,%r9
    12b5:	jne    1280 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12b7:	test   %rcx,%rcx
    12ba:	je     1314 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd4>
    12bc:	lea    (%rdx,%rsi,4),%rdx
    12c0:	lea    (%r8,%rsi,4),%rsi
    12c4:	xor    %edi,%edi
    12c6:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12d5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e4:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	movslq (%rsi,%rdi,4),%r8
    1304:	mov    (%rax,%r8,4),%r8d
    1308:	mov    %r8d,(%rdx,%rdi,4)
    130c:	inc    %rdi
    130f:	cmp    %rdi,%rcx
    1312:	jne    1300 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1314:	ret
    1315:	data16 cs nopw 0x0(%rax,%rax,1)
