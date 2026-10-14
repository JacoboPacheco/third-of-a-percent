0000000000001220 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	mov    %rcx,%rsi
    122d:	sar    $0x2,%rsi
    1231:	cmp    $0x3,%rsi
    1235:	jb     12bd <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9d>
    123b:	mov    (%rdi),%rdx
    123e:	cmp    $0xc,%rcx
    1242:	jne    1255 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x35>
    1244:	mov    $0x1,%esi
    1249:	mov    $0x2,%edi
    124e:	test   $0x4,%cl
    1251:	jne    12b0 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>
    1253:	jmp    12bd <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9d>
    1255:	and    $0xfffffffffffffffe,%rsi
    1259:	mov    $0x2,%edi
    125e:	sub    %rsi,%rdi
    1261:	mov    $0x1,%esi
    1266:	cs nopw 0x0(%rax,%rax,1)
    1270:	mov    (%rax,%rsi,4),%r8d
    1274:	add    -0x4(%rax,%rsi,4),%r8d
    1279:	add    0x4(%rax,%rsi,4),%r8d
    127e:	mov    %r8d,(%rdx,%rsi,4)
    1282:	mov    0x4(%rax,%rsi,4),%r8d
    1287:	add    (%rax,%rsi,4),%r8d
    128b:	add    0x8(%rax,%rsi,4),%r8d
    1290:	mov    %r8d,0x4(%rdx,%rsi,4)
    1295:	lea    (%rdi,%rsi,1),%r8
    1299:	add    $0x2,%r8
    129d:	add    $0x2,%rsi
    12a1:	cmp    $0x1,%r8
    12a5:	jne    1270 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x50>
    12a7:	lea    0x1(%rsi),%rdi
    12ab:	test   $0x4,%cl
    12ae:	je     12bd <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9d>
    12b0:	mov    (%rax,%rsi,4),%ecx
    12b3:	add    -0x4(%rax,%rsi,4),%ecx
    12b7:	add    (%rax,%rdi,4),%ecx
    12ba:	mov    %ecx,(%rdx,%rsi,4)
    12bd:	ret
    12be:	xchg   %ax,%ax
