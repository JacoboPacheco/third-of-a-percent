0000000000001240 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     129e <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5e>
    124c:	sar    $0x2,%rcx
    1250:	mov    (%rdi),%rdx
    1253:	mov    0x8(%rdi),%rsi
    1257:	sub    %rdx,%rsi
    125a:	sar    $0x2,%rsi
    125e:	lea    -0x1(%rcx),%rdi
    1262:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1271:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1280:	cmp    %rsi,%rdi
    1283:	jae    129f <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x5f>
    1285:	mov    -0x4(%rax,%rcx,4),%r8d
    128a:	add    %r8d,%r8d
    128d:	mov    %r8d,-0x4(%rdx,%rcx,4)
    1292:	lea    -0x1(%rcx),%r8
    1296:	mov    %r8,%rcx
    1299:	test   %r8,%r8
    129c:	jne    1280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    129e:	ret
    129f:	ud2
    12a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
