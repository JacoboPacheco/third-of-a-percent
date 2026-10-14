0000000000001240 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rdx
    1247:	sub    %rax,%rdx
    124a:	je     12a8 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x68>
    124c:	mov    (%rdi),%rcx
    124f:	cmp    $0x4,%rdx
    1253:	jne    1259 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x19>
    1255:	xor    %esi,%esi
    1257:	jmp    129c <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5c>
    1259:	mov    %rdx,%rdi
    125c:	sar    $0x2,%rdi
    1260:	and    $0xfffffffffffffffe,%rdi
    1264:	xor    %esi,%esi
    1266:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1275:	data16 cs nopw 0x0(%rax,%rax,1)
    1280:	movzbl (%rax,%rsi,4),%r8d
    1285:	incl   (%rcx,%r8,4)
    1289:	movzbl 0x4(%rax,%rsi,4),%r8d
    128f:	incl   (%rcx,%r8,4)
    1293:	add    $0x2,%rsi
    1297:	cmp    %rsi,%rdi
    129a:	jne    1280 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    129c:	test   $0x4,%dl
    129f:	je     12a8 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x68>
    12a1:	movzbl (%rax,%rsi,4),%eax
    12a5:	incl   (%rcx,%rax,4)
    12a8:	ret
    12a9:	nopl   0x0(%rax)
