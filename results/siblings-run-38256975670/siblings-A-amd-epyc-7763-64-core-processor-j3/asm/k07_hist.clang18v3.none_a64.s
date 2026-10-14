0000000000001240 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rdx
    1243:	mov    0x8(%rsi),%r8
    1247:	sub    %rdx,%r8
    124a:	je     12cf <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x8f>
    1250:	sar    $0x2,%r8
    1254:	mov    (%rdi),%rax
    1257:	cmp    $0x1,%r8
    125b:	mov    %r8,%rsi
    125e:	adc    $0x0,%rsi
    1262:	mov    %esi,%ecx
    1264:	and    $0x3,%ecx
    1267:	cmp    $0x4,%r8
    126b:	jae    1271 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x31>
    126d:	xor    %edi,%edi
    126f:	jmp    12b0 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    1271:	and    $0xfffffffffffffffc,%rsi
    1275:	xor    %edi,%edi
    1277:	nopw   0x0(%rax,%rax,1)
    1280:	movzbl (%rdx,%rdi,4),%r8d
    1285:	incl   (%rax,%r8,4)
    1289:	movzbl 0x4(%rdx,%rdi,4),%r8d
    128f:	incl   (%rax,%r8,4)
    1293:	movzbl 0x8(%rdx,%rdi,4),%r8d
    1299:	incl   (%rax,%r8,4)
    129d:	movzbl 0xc(%rdx,%rdi,4),%r8d
    12a3:	incl   (%rax,%r8,4)
    12a7:	add    $0x4,%rdi
    12ab:	cmp    %rdi,%rsi
    12ae:	jne    1280 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12b0:	test   %rcx,%rcx
    12b3:	je     12cf <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x8f>
    12b5:	lea    (%rdx,%rdi,4),%rdx
    12b9:	xor    %esi,%esi
    12bb:	nopl   0x0(%rax,%rax,1)
    12c0:	movzbl (%rdx,%rsi,4),%edi
    12c4:	incl   (%rax,%rdi,4)
    12c7:	inc    %rsi
    12ca:	cmp    %rsi,%rcx
    12cd:	jne    12c0 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12cf:	ret
