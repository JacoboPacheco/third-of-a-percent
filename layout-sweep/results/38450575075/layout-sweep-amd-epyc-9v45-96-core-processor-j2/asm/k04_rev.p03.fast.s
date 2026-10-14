0000000000001250 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1250:	mov    (%rsi),%rax
    1253:	mov    0x8(%rsi),%rcx
    1257:	sub    %rax,%rcx
    125a:	je     129e <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    125c:	sar    $0x2,%rcx
    1260:	mov    (%rdi),%rdx
    1263:	mov    0x8(%rdi),%rsi
    1267:	sub    %rdx,%rsi
    126a:	sar    $0x2,%rsi
    126e:	lea    -0x1(%rcx),%rdi
    1272:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1280:	cmp    %rsi,%rdi
    1283:	jae    129f <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4f>
    1285:	mov    -0x4(%rax,%rcx,4),%r8d
    128a:	add    %r8d,%r8d
    128d:	mov    %r8d,-0x4(%rdx,%rcx,4)
    1292:	lea    -0x1(%rcx),%r8
    1296:	mov    %r8,%rcx
    1299:	test   %r8,%r8
    129c:	jne    1280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    129e:	ret
    129f:	ud2
    12a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
