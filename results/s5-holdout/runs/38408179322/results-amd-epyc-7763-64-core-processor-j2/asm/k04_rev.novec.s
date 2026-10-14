0000000000001220 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rsi
    1227:	sub    %rax,%rsi
    122a:	je     1294 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
    122c:	sar    $0x2,%rsi
    1230:	mov    (%rdi),%rcx
    1233:	lea    -0x1(%rsi),%rdi
    1237:	mov    %rsi,%r8
    123a:	and    $0x3,%r8
    123e:	je     1295 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x75>
    1240:	lea    -0x1(%rsi),%rdx
    1244:	mov    -0x4(%rax,%rsi,4),%r9d
    1249:	add    %r9d,%r9d
    124c:	mov    %r9d,-0x4(%rcx,%rsi,4)
    1251:	mov    %rdx,%rsi
    1254:	dec    %r8
    1257:	jne    1240 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x20>
    1259:	cmp    $0x3,%rdi
    125d:	jb     1294 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
    125f:	nop
    1260:	mov    -0x4(%rax,%rdx,4),%esi
    1264:	add    %esi,%esi
    1266:	mov    %esi,-0x4(%rcx,%rdx,4)
    126a:	mov    -0x8(%rax,%rdx,4),%esi
    126e:	add    %esi,%esi
    1270:	mov    %esi,-0x8(%rcx,%rdx,4)
    1274:	mov    -0xc(%rax,%rdx,4),%esi
    1278:	add    %esi,%esi
    127a:	mov    %esi,-0xc(%rcx,%rdx,4)
    127e:	mov    -0x10(%rax,%rdx,4),%esi
    1282:	add    %esi,%esi
    1284:	mov    %esi,-0x10(%rcx,%rdx,4)
    1288:	lea    -0x4(%rdx),%rsi
    128c:	mov    %rsi,%rdx
    128f:	test   %rsi,%rsi
    1292:	jne    1260 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    1294:	ret
    1295:	mov    %rsi,%rdx
    1298:	cmp    $0x3,%rdi
    129c:	jae    1260 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    129e:	jmp    1294 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x74>
