0000000000001220 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rdx),%rcx
    1223:	mov    0x8(%rdx),%r8
    1227:	sub    %rcx,%r8
    122a:	je     1304 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe4>
    1230:	sar    $0x2,%r8
    1234:	mov    (%rsi),%rax
    1237:	mov    (%rdi),%rsi
    123a:	cmp    $0x1,%r8
    123e:	mov    %r8,%rdi
    1241:	adc    $0x0,%rdi
    1245:	mov    %edi,%edx
    1247:	and    $0x7,%edx
    124a:	cmp    $0x8,%r8
    124e:	jae    1258 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x38>
    1250:	xor    %r8d,%r8d
    1253:	jmp    12d7 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xb7>
    1258:	and    $0xfffffffffffffff8,%rdi
    125c:	xor    %r8d,%r8d
    125f:	nop
    1260:	movslq (%rcx,%r8,4),%r9
    1264:	mov    (%rax,%r9,4),%r9d
    1268:	mov    %r9d,(%rsi,%r8,4)
    126c:	movslq 0x4(%rcx,%r8,4),%r9
    1271:	mov    (%rax,%r9,4),%r9d
    1275:	mov    %r9d,0x4(%rsi,%r8,4)
    127a:	movslq 0x8(%rcx,%r8,4),%r9
    127f:	mov    (%rax,%r9,4),%r9d
    1283:	mov    %r9d,0x8(%rsi,%r8,4)
    1288:	movslq 0xc(%rcx,%r8,4),%r9
    128d:	mov    (%rax,%r9,4),%r9d
    1291:	mov    %r9d,0xc(%rsi,%r8,4)
    1296:	movslq 0x10(%rcx,%r8,4),%r9
    129b:	mov    (%rax,%r9,4),%r9d
    129f:	mov    %r9d,0x10(%rsi,%r8,4)
    12a4:	movslq 0x14(%rcx,%r8,4),%r9
    12a9:	mov    (%rax,%r9,4),%r9d
    12ad:	mov    %r9d,0x14(%rsi,%r8,4)
    12b2:	movslq 0x18(%rcx,%r8,4),%r9
    12b7:	mov    (%rax,%r9,4),%r9d
    12bb:	mov    %r9d,0x18(%rsi,%r8,4)
    12c0:	movslq 0x1c(%rcx,%r8,4),%r9
    12c5:	mov    (%rax,%r9,4),%r9d
    12c9:	mov    %r9d,0x1c(%rsi,%r8,4)
    12ce:	add    $0x8,%r8
    12d2:	cmp    %r8,%rdi
    12d5:	jne    1260 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12d7:	test   %rdx,%rdx
    12da:	je     1304 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe4>
    12dc:	lea    (%rsi,%r8,4),%rsi
    12e0:	lea    (%rcx,%r8,4),%rcx
    12e4:	xor    %edi,%edi
    12e6:	cs nopw 0x0(%rax,%rax,1)
    12f0:	movslq (%rcx,%rdi,4),%r8
    12f4:	mov    (%rax,%r8,4),%r8d
    12f8:	mov    %r8d,(%rsi,%rdi,4)
    12fc:	inc    %rdi
    12ff:	cmp    %rdi,%rdx
    1302:	jne    12f0 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd0>
    1304:	ret
    1305:	data16 cs nopw 0x0(%rax,%rax,1)
