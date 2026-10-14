0000000000001220 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     126a <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4a>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rdi),%rdx
    1233:	mov    0x8(%rdi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	lea    -0x1(%rcx),%rdi
    1242:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1250:	cmp    %rsi,%rdi
    1253:	jae    126b <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4b>
    1255:	mov    -0x4(%rax,%rcx,4),%r8d
    125a:	add    %r8d,%r8d
    125d:	mov    %r8d,-0x4(%rdx,%rcx,4)
    1262:	dec    %rcx
    1265:	test   %rcx,%rcx
    1268:	jne    1250 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    126a:	ret
    126b:	ud2
    126d:	nopl   (%rax)
