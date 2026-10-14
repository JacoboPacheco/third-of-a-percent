0000000000001240 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%rcx
    1243:	mov    0x8(%rdx),%r9
    1247:	sub    %rcx,%r9
    124a:	je     12e4 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa4>
    1250:	sar    $0x2,%r9
    1254:	mov    (%rsi),%rax
    1257:	cmp    $0x1,%r9
    125b:	mov    %r9,%r8
    125e:	adc    $0x0,%r8
    1262:	mov    (%rdi),%rsi
    1265:	mov    %r8d,%edx
    1268:	and    $0x3,%edx
    126b:	cmp    $0x4,%r9
    126f:	jae    1275 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x35>
    1271:	xor    %edi,%edi
    1273:	jmp    12bf <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x7f>
    1275:	and    $0xfffffffffffffffc,%r8
    1279:	xor    %edi,%edi
    127b:	nopl   0x0(%rax,%rax,1)
    1280:	movslq (%rcx,%rdi,4),%r9
    1284:	mov    (%rax,%r9,4),%r9d
    1288:	mov    %r9d,(%rsi,%rdi,4)
    128c:	movslq 0x4(%rcx,%rdi,4),%r9
    1291:	mov    (%rax,%r9,4),%r9d
    1295:	mov    %r9d,0x4(%rsi,%rdi,4)
    129a:	movslq 0x8(%rcx,%rdi,4),%r9
    129f:	mov    (%rax,%r9,4),%r9d
    12a3:	mov    %r9d,0x8(%rsi,%rdi,4)
    12a8:	movslq 0xc(%rcx,%rdi,4),%r9
    12ad:	mov    (%rax,%r9,4),%r9d
    12b1:	mov    %r9d,0xc(%rsi,%rdi,4)
    12b6:	add    $0x4,%rdi
    12ba:	cmp    %rdi,%r8
    12bd:	jne    1280 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12bf:	test   %rdx,%rdx
    12c2:	je     12e4 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa4>
    12c4:	lea    (%rsi,%rdi,4),%rsi
    12c8:	lea    (%rcx,%rdi,4),%rcx
    12cc:	xor    %edi,%edi
    12ce:	xchg   %ax,%ax
    12d0:	movslq (%rcx,%rdi,4),%r8
    12d4:	mov    (%rax,%r8,4),%r8d
    12d8:	mov    %r8d,(%rsi,%rdi,4)
    12dc:	inc    %rdi
    12df:	cmp    %rdi,%rdx
    12e2:	jne    12d0 <_Z15kern_m06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12e4:	ret
    12e5:	data16 cs nopw 0x0(%rax,%rax,1)
