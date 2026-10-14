0000000000001220 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rdx
    1223:	mov    0x8(%rsi),%r8
    1227:	sub    %rdx,%r8
    122a:	je     12af <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x8f>
    1230:	sar    $0x2,%r8
    1234:	mov    (%rdi),%rax
    1237:	cmp    $0x1,%r8
    123b:	mov    %r8,%rsi
    123e:	adc    $0x0,%rsi
    1242:	mov    %esi,%ecx
    1244:	and    $0x3,%ecx
    1247:	cmp    $0x4,%r8
    124b:	jae    1251 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x31>
    124d:	xor    %edi,%edi
    124f:	jmp    1290 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    1251:	and    $0xfffffffffffffffc,%rsi
    1255:	xor    %edi,%edi
    1257:	nopw   0x0(%rax,%rax,1)
    1260:	movzbl (%rdx,%rdi,4),%r8d
    1265:	incl   (%rax,%r8,4)
    1269:	movzbl 0x4(%rdx,%rdi,4),%r8d
    126f:	incl   (%rax,%r8,4)
    1273:	movzbl 0x8(%rdx,%rdi,4),%r8d
    1279:	incl   (%rax,%r8,4)
    127d:	movzbl 0xc(%rdx,%rdi,4),%r8d
    1283:	incl   (%rax,%r8,4)
    1287:	add    $0x4,%rdi
    128b:	cmp    %rdi,%rsi
    128e:	jne    1260 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    1290:	test   %rcx,%rcx
    1293:	je     12af <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x8f>
    1295:	lea    (%rdx,%rdi,4),%rdx
    1299:	xor    %esi,%esi
    129b:	nopl   0x0(%rax,%rax,1)
    12a0:	movzbl (%rdx,%rsi,4),%edi
    12a4:	incl   (%rax,%rdi,4)
    12a7:	inc    %rsi
    12aa:	cmp    %rsi,%rcx
    12ad:	jne    12a0 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12af:	ret
