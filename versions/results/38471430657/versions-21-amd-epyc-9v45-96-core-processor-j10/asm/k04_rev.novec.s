0000000000001220 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rsi
    1227:	sub    %rax,%rsi
    122a:	je     12a1 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x81>
    122c:	sar    $0x2,%rsi
    1230:	mov    (%rdi),%rcx
    1233:	mov    %rsi,%rdi
    1236:	mov    %rsi,%rdx
    1239:	and    $0x3,%rdi
    123d:	je     1269 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x49>
    123f:	mov    %rsi,%r8
    1242:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1250:	lea    -0x1(%r8),%rdx
    1254:	mov    -0x4(%rax,%r8,4),%r9d
    1259:	add    %r9d,%r9d
    125c:	mov    %r9d,-0x4(%rcx,%r8,4)
    1261:	mov    %rdx,%r8
    1264:	dec    %rdi
    1267:	jne    1250 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1269:	cmp    $0x4,%rsi
    126d:	jb     12a1 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x81>
    126f:	nop
    1270:	mov    -0x4(%rax,%rdx,4),%esi
    1274:	add    %esi,%esi
    1276:	mov    %esi,-0x4(%rcx,%rdx,4)
    127a:	mov    -0x8(%rax,%rdx,4),%esi
    127e:	add    %esi,%esi
    1280:	mov    %esi,-0x8(%rcx,%rdx,4)
    1284:	mov    -0xc(%rax,%rdx,4),%esi
    1288:	add    %esi,%esi
    128a:	mov    %esi,-0xc(%rcx,%rdx,4)
    128e:	mov    -0x10(%rax,%rdx,4),%esi
    1292:	add    %esi,%esi
    1294:	mov    %esi,-0x10(%rcx,%rdx,4)
    1298:	add    $0xfffffffffffffffc,%rdx
    129c:	test   %rdx,%rdx
    129f:	jne    1270 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x50>
    12a1:	ret
    12a2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
