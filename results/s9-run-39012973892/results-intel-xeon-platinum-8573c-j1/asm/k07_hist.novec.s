0000000000001220 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rsi
    1227:	sub    %rax,%rsi
    122a:	je     1278 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x58>
    122c:	sar    $0x2,%rsi
    1230:	mov    (%rdi),%rcx
    1233:	mov    $0x1,%edx
    1238:	cmp    $0x2,%rsi
    123c:	cmovae %rsi,%rdx
    1240:	jae    1246 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x26>
    1242:	xor    %esi,%esi
    1244:	jmp    126c <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4c>
    1246:	mov    %rdx,%rdi
    1249:	and    $0xfffffffffffffffe,%rdi
    124d:	xor    %esi,%esi
    124f:	nop
    1250:	movzbl (%rax,%rsi,4),%r8d
    1255:	incl   (%rcx,%r8,4)
    1259:	movzbl 0x4(%rax,%rsi,4),%r8d
    125f:	incl   (%rcx,%r8,4)
    1263:	add    $0x2,%rsi
    1267:	cmp    %rsi,%rdi
    126a:	jne    1250 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    126c:	test   $0x1,%dl
    126f:	je     1278 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x58>
    1271:	movzbl (%rax,%rsi,4),%eax
    1275:	incl   (%rcx,%rax,4)
    1278:	ret
    1279:	nopl   0x0(%rax)
