0000000000001220 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rdx
    1227:	sub    %rax,%rdx
    122a:	je     1278 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x58>
    122c:	mov    (%rdi),%rcx
    122f:	cmp    $0x4,%rdx
    1233:	jne    1239 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x19>
    1235:	xor    %esi,%esi
    1237:	jmp    126c <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4c>
    1239:	mov    %rdx,%rdi
    123c:	sar    $0x2,%rdi
    1240:	and    $0xfffffffffffffffe,%rdi
    1244:	xor    %esi,%esi
    1246:	cs nopw 0x0(%rax,%rax,1)
    1250:	movzbl (%rax,%rsi,4),%r8d
    1255:	incl   (%rcx,%r8,4)
    1259:	movzbl 0x4(%rax,%rsi,4),%r8d
    125f:	incl   (%rcx,%r8,4)
    1263:	add    $0x2,%rsi
    1267:	cmp    %rsi,%rdi
    126a:	jne    1250 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    126c:	test   $0x4,%dl
    126f:	je     1278 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x58>
    1271:	movzbl (%rax,%rsi,4),%eax
    1275:	incl   (%rcx,%rax,4)
    1278:	ret
    1279:	nopl   0x0(%rax)
