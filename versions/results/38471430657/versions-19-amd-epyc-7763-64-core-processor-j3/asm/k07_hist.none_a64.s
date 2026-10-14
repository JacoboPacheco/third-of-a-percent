0000000000001240 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rsi
    1247:	sub    %rax,%rsi
    124a:	je     12a8 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x68>
    124c:	sar    $0x2,%rsi
    1250:	mov    (%rdi),%rcx
    1253:	mov    $0x1,%edx
    1258:	cmp    $0x2,%rsi
    125c:	cmovae %rsi,%rdx
    1260:	jae    1266 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x26>
    1262:	xor    %esi,%esi
    1264:	jmp    129c <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5c>
    1266:	mov    %rdx,%rdi
    1269:	and    $0xfffffffffffffffe,%rdi
    126d:	xor    %esi,%esi
    126f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127e:	xchg   %ax,%ax
    1280:	movzbl (%rax,%rsi,4),%r8d
    1285:	incl   (%rcx,%r8,4)
    1289:	movzbl 0x4(%rax,%rsi,4),%r8d
    128f:	incl   (%rcx,%r8,4)
    1293:	add    $0x2,%rsi
    1297:	cmp    %rsi,%rdi
    129a:	jne    1280 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    129c:	test   $0x1,%dl
    129f:	je     12a8 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x68>
    12a1:	movzbl (%rax,%rsi,4),%eax
    12a5:	incl   (%rcx,%rax,4)
    12a8:	ret
    12a9:	nopl   0x0(%rax)
